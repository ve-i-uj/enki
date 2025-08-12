"""Entity message handlers."""

import dataclasses
import logging
from dataclasses import dataclass
from typing import Any, ClassVar

from enki import kbemath, msgspec
from enki.msg.message import Message
from enki.core.novalue import NoValue
from enki.handlers.base import Handler, MsgResult, ParsedMsgInfo
from enki.misc import devonly

from ..client_msg_parser.ehelper import EntityHelper
from ..layer import ilayer
from ..layer.thlayer import IGameLayer

logger = logging.getLogger(__name__)


class _OptimizedXYZReader:
    """???.

    Кодировка float32:
        - 0-7 бит хранят мантиссу
        - 8-10 бит хранят экспоненту
        - 11 бит хранят флаг

    Используются всего 24 бита (3 байта) для хранения 2 чисел с плавающей
    запятой. Но требуется возможность достижения чисел между -512 и 512.
    В 8-битной мантиссе можно поставить только максимальное значение 256,
    а показатель степени имеет только 3 бита. Округляем первый бит,
    чтобы получить диапазон между (-512, -2) | (2, 512). Т.е. координаты
    выше 512 по модулю и меньше 2 по модулю не могут быть закодированы таким
    способом. Чтобы обойти это, в координату в любом случае добавляется или
    вычитается 2, чтобы точно не было координаты в диапазоне [-2, 2]. На
    стадии декодирования соответственно нужно вычесть или добавить двойку (в
    зависимости от модуля числа) после декодирования.

    А дальше магия ...
    См. kbe/src/lib/common/memorystream.h:453 (readPackXZ)
    и kbe/src/lib/network/bundle.h:381 (appendPackXZ)
    """

    @staticmethod
    def int32_to_float32(value: int) -> float:
        return kbetype.FLOAT.decode(memoryview(kbetype.INT32.encode(value)))[0]

    @staticmethod
    def float32_to_int32(value: float) -> int:
        return kbetype.INT32.decode(memoryview(kbetype.FLOAT.encode(value)))[0]

    @staticmethod
    def read_packed_xz(data: memoryview) -> tuple[kbetype.Vector2, memoryview]:
        # 0x40000000 is 0b1000000000000000000000000000000
        x = 0x40000000
        z = 0x40000000

        data_: int = 0

        value_1, offset = kbetype.UINT8.decode(data)
        data = data[offset:]
        value_2, offset = kbetype.UINT8.decode(data)
        data = data[offset:]
        value_3, offset = kbetype.UINT8.decode(data)
        data = data[offset:]

        # There were 3 bytes ...
        data_ |= value_1 << 16
        data_ |= value_2 << 8
        data_ |= value_3
        # ... and now there is one 24 bit value. This value contains two float
        # numbers by 12 bit per a value.

        # 0x7ff000 is 0b11111111111000000000000
        # The half of the value is cut off and then left shifts three bits
        x |= (data_ & 0x7FF000) << 3
        z |= (data_ & 0x0007FF) << 15

        x = _OptimizedXYZReader.float32_to_int32(
            _OptimizedXYZReader.int32_to_float32(x) - 2.0
        )
        z = _OptimizedXYZReader.float32_to_int32(
            _OptimizedXYZReader.int32_to_float32(z) - 2.0
        )

        # 0x800000 is 0b100000000000000000000000
        # TODO: [2022-08-31 15:29 burov_alexey@mail.ru]:
        # Знак определяется?
        x |= (data_ & 0x800000) << 8
        z |= (data_ & 0x000800) << 20

        return kbetype.Vector2(
            _OptimizedXYZReader.int32_to_float32(x),
            _OptimizedXYZReader.int32_to_float32(z),
        ), data

    @staticmethod
    def read_packed_y(data: memoryview) -> tuple[float, memoryview]:
        data_, offset = kbetype.UINT16.decode(data)
        data = data[offset:]

        y = 0x40000000
        y |= (data_ & 0x7FFF) << 12
        y = _OptimizedXYZReader.float32_to_int32(
            _OptimizedXYZReader.int32_to_float32(y) - 2.0
        )
        y |= (data_ & 0x8000) << 16

        return _OptimizedXYZReader.int32_to_float32(y), data


class _OnEntityCreatedMixin:
    """Действие при создании сущности."""

    _entity_helper: EntityHelper
    _game: IGameLayer

    def on_entity_created(
        self, entity_id: int, entity_cls_name: str, is_player: bool
    ):
        logger.debug("[%s] %s", self, devonly.func_args_values())
        desc = self._entity_helper.get_entity_descr_by_cls_name(entity_cls_name)

        self._game.call_entity_created(entity_id, entity_cls_name, is_player)

        for comp_name in desc.component_names:
            self._game.call_component_onAttached(entity_id, comp_name)


@dataclass
class PoseData:
    x: float = NoValue.NO_POS_DIR_VALUE
    y: float = NoValue.NO_POS_DIR_VALUE
    z: float = NoValue.NO_POS_DIR_VALUE
    yaw: float = NoValue.NO_POS_DIR_VALUE
    pitch: float = NoValue.NO_POS_DIR_VALUE
    roll: float = NoValue.NO_POS_DIR_VALUE

    @property
    def position(self) -> Position:
        return Position(self.x, self.y, self.z)

    @property
    def direction(self) -> Direction:
        return Direction(self.roll, self.pitch, self.yaw)

    def update_position(self, new_position: Position):
        self.x = new_position.x
        self.y = new_position.y
        self.z = new_position.z

    def update_direction(self, new_direction: Direction):
        self.roll = new_direction.roll
        self.pitch = new_direction.pitch
        self.yaw = new_direction.yaw


@dataclass
class EntityParsedMsgData(ParsedMsgInfo):
    pass


class EntityMsgParserResult(MsgResult):
    result: EntityParsedMsgData
    msg_id: int = NoValue.NO_ID


class EntityMsgParser(IMsgParser):
    def __init__(self, entity_helper: EntityHelper):
        self._entity_helper = entity_helper

    @property
    def _game(self) -> IGameLayer:
        return ilayer.get_game_layer()

    def get_entity_id(self, data: memoryview) -> tuple[int, memoryview]:
        entity_id, offset = kbetype.ENTITY_ID.decode(data)
        data = data[offset:]
        return entity_id, data

    def parse_data(
        self, data: memoryview, entity_id: int
    ) -> tuple[EntityParsedMsgData, memoryview]:
        return EntityParsedMsgData(), data[:]

    def process_parsed_data(
        self, pd: EntityParsedMsgData, entity_id: int
    ) -> EntityMsgParserResult:
        return EntityMsgParserResult(False, pd)

    def parse(self, msg: Message) -> EntityMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        data = msg.get_values()[0]
        entity_id, data = self.get_entity_id(data)
        pd, data = self.parse_data(data, entity_id)
        return self.process_parsed_data(pd, entity_id)

    def set_pose(self, entity_id: int, pose_data: PoseData):
        self._game.update_entity_properties(
            entity_id,
            {
                "position": pose_data.position,
                "direction": pose_data.direction,
            },
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"


class _OptimizedHandlerMixin:
    """С оптимизациями заложенными серверным движком вычисляются entity_id."""

    _entity_helper: EntityHelper

    def get_entity_id(self, data: memoryview) -> tuple[int, memoryview]:
        return self.get_optimized_entity_id(data)

    def get_optimized_entity_id(self, data: memoryview) -> tuple[int, memoryview]:
        if not self._entity_helper.is_aliasEntityID:
            entity_id, offset = kbetype.INT32.decode(data)
            data = data[offset:]
            return entity_id, data

        alias_id, offset = kbetype.UINT8.decode(data)
        data = data[offset:]
        entity_id = self._entity_helper.get_entity_id_by(alias_id)

        return entity_id, data


@dataclass
class _OnUpdateData_XYZ_YPR_BaseParsedMsgData(EntityParsedMsgData):
    pass


@dataclass
class _OnUpdateData_XYZ_YPR_BaseMsgParserResult(EntityMsgParserResult):
    result: _OnUpdateData_XYZ_YPR_BaseParsedMsgData
    msg_id: int = NoValue.NO_ID


class _OnUpdateData_XYZ_YPR_BaseHandler(EntityHandler, _OptimizedHandlerMixin):
    _parsed_data_cls: ClassVar[type[_OnUpdateData_XYZ_YPR_BaseParsedMsgData]]
    _handler_result_cls: ClassVar[type[_OnUpdateData_XYZ_YPR_BaseMsgParserResult]]

    def get_entity_id(self, data: memoryview) -> tuple[int, memoryview]:
        return self.get_optimized_entity_id(data)

    def parse_data(
        self, data: memoryview, entity_id: int
    ) -> tuple[_OnUpdateData_XYZ_YPR_BaseParsedMsgData, memoryview]:
        values = []
        for _ in range(len(dataclasses.fields(self._parsed_data_cls))):
            value, offset = kbetype.FLOAT.decode(data)
            data = data[offset:]
            values.append(value)
        pd = self._parsed_data_cls(*values)
        return pd, data

    def process_parsed_data(
        self, pd: _OnUpdateData_XYZ_YPR_BaseParsedMsgData, entity_id: int
    ) -> _OnUpdateData_XYZ_YPR_BaseMsgParserResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name)
            for f in dataclasses.fields(self._parsed_data_cls)
        })
        self.set_pose(entity_id, pose_data)

        return _OnUpdateData_XYZ_YPR_BaseMsgParserResult(True, pd)


@dataclass
class OnUpdatePropertysParsedMsgData(ParsedMsgInfo):
    entity_id: int
    e_properties: dict[str, Any]
    ec_properties: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclass
class OnUpdatePropertysMsgParserResult(MsgResult):
    result: OnUpdatePropertysParsedMsgData
    msg_id: int = msgspec.client.onUpdatePropertys.id


class OnUpdatePropertysHandler(EntityHandler):
    """Handler of `onUpdatePropertys`."""

    def parse(self, msg: Message) -> OnUpdatePropertysMsgParserResult:
        """Handler of `onUpdatePropertys`."""
        logger.debug(f"[{self}] ({devonly.func_args_values()})")
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])
        entity_id, data = self.get_entity_id(data)
        parsed_data = OnUpdatePropertysParsedMsgData(
            entity_id=entity_id, e_properties={}
        )

        cls_name = self._entity_helper.get_entity_cls_name_by_eid(entity_id)
        assert cls_name is not None
        desc = self._entity_helper.get_entity_descr_by_cls_name(cls_name)
        while data:
            if (
                self._entity_helper.get_kbenginexml().cellapp.entitydefAliasID
                and len(desc.property_desc_by_id) <= 255
            ):
                component_uid, shift = kbetype.UINT8.decode(data)
                data = data[shift:]
                property_uid, shift = kbetype.UINT8.decode(data)
                data = data[shift:]
            else:
                component_uid, shift = kbetype.UINT16.decode(data)
                data = data[shift:]
                property_uid, shift = kbetype.UINT16.decode(data)
                data = data[shift:]

            prop_id = component_uid or property_uid
            assert prop_id != 0, "There is NO id of the property"

            type_spec = desc.property_desc_by_id[prop_id]
            value, shift = type_spec.kbetype.decode(data)
            data = data[shift:]

            if type_spec.name in desc.component_names:
                component_name = type_spec.name
                # Это значит, что свойство на самом деле компонент (т.е. отдельный тип)
                ec_data: kbetype.EntityComponentData = value

                comp_desc = self._entity_helper.get_entity_descr_by_uid(
                    value.component_ent_id
                )
                while ec_data.count > 0:
                    if (
                        self._entity_helper.get_kbenginexml().cellapp.entitydefAliasID
                        and len(comp_desc.property_desc_by_id) <= 255
                    ):
                        _component_uid, shift = kbetype.UINT8.decode(data)
                        data = data[shift:]
                        property_uid, shift = kbetype.UINT8.decode(data)
                        data = data[shift:]
                    else:
                        _component_uid, shift = kbetype.UINT16.decode(data)
                        data = data[shift:]
                        property_uid, shift = kbetype.UINT16.decode(data)
                        data = data[shift:]
                    type_spec = comp_desc.property_desc_by_id[property_uid]
                    v, shift = type_spec.kbetype.decode(data)
                    data = data[shift:]
                    ec_data.properties[type_spec.name] = v
                    ec_data.count -= 1

                parsed_data.ec_properties = ec_data.properties
                self._game.update_component_properties(
                    entity_id, component_name, ec_data.properties
                )
                continue

            parsed_data.e_properties[type_spec.name] = value

        self._game.update_entity_properties(entity_id, parsed_data.e_properties)

        return OnUpdatePropertysMsgParserResult(success=True, result=parsed_data)


@dataclass
class OnUpdatePropertysOptimizedMsgParserResult(OnUpdatePropertysMsgParserResult):
    msg_id: int = msgspec.client.onUpdatePropertysOptimized.id


class OnUpdatePropertysOptimizedHandler(
    OnUpdatePropertysHandler, _OptimizedHandlerMixin
):
    def parse(self, msg: Message) -> OnUpdatePropertysMsgParserResult:
        res = super().handle(msg)
        return OnUpdatePropertysOptimizedMsgParserResult(
            success=True, result=res.result
        )


@dataclass
class OnCreatedProxiesParsedMsgData(ParsedMsgInfo):
    # After each proxy is created, a uuid is generated by the system,
    # which is used for identification when the front-end re-logins
    rnd_uuid: int
    entity_id: int
    cls_name: str  # the class name of the entity


@dataclass
class OnCreatedProxiesMsgParserResult(MsgResult):
    result: OnCreatedProxiesParsedMsgData
    msg_id: int = msgspec.client.onCreatedProxies.id


class OnCreatedProxiesHandler(EntityHandler, _OnEntityCreatedMixin):
    def parse(self, msg: Message) -> OnCreatedProxiesMsgParserResult:
        values: tuple[Any, ...] = msg.get_values()
        pd = OnCreatedProxiesParsedMsgData(*values)
        self.on_entity_created(pd.entity_id, pd.cls_name, True)
        self._entity_helper.on_entity_created(
            pd.entity_id, pd.cls_name, is_player=True
        )

        return OnCreatedProxiesMsgParserResult(success=True, result=pd)


@dataclass
class OnRemoteMethodCallParsedMsgData(ParsedMsgInfo):
    entity_id: int
    method_name: str
    arguments: list


@dataclass
class OnRemoteMethodCallMsgParserResult(MsgResult):
    result: OnRemoteMethodCallParsedMsgData
    msg_id: int = msgspec.client.onRemoteMethodCall.id


class OnRemoteMethodCallHandler(EntityHandler):
    def parse(self, msg: Message) -> OnRemoteMethodCallMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])
        entity_id, offset = kbetype.ENTITY_ID.decode(data)
        data = data[offset:]

        cls_name = self._entity_helper.get_entity_cls_name_by_eid(entity_id)
        assert cls_name is not None
        entity_desc = self._entity_helper.get_entity_descr_by_cls_name(cls_name)

        if entity_desc.is_optimized_cl_method_uid:
            # componentPropertyAliasID
            component_prop_id, offset = kbetype.UINT8.decode(data)
            data = data[offset:]
        else:
            component_prop_id, offset = kbetype.UINT16.decode(data)
            data = data[offset:]

        comp_prop_desc = None
        if component_prop_id != NoValue.NO_ID:
            # It's a component remote method call. The call addresses to
            # the entity property. Get descriptsion of this property.
            comp_prop_desc = entity_desc.property_desc_by_id[component_prop_id]
            # It's an instance of the component-entity (e.g "Test" entity in the demo)
            entity_desc = self._entity_helper.get_entity_descr_by_cls_name(
                comp_prop_desc.component_type_name
            )

        if entity_desc.is_optimized_cl_method_uid:
            method_id, offset = kbetype.UINT8.decode(data)
            data = data[offset:]
        else:
            method_id, offset = kbetype.UINT16.decode(data)
            data = data[offset:]

        method_desc = entity_desc.client_methods[method_id]

        arguments = []
        for kbe_type in method_desc.kbetypes:
            value, offset = kbe_type.decode(data)
            data = data[offset:]
            arguments.append(value)

        if comp_prop_desc is None:
            self._game.call_entity_method(entity_id, method_desc.name, *arguments)
        else:
            self._game.call_component_method(
                entity_id, comp_prop_desc.name, method_desc.name, *arguments
            )

        parsed_data = OnRemoteMethodCallParsedMsgData(
            entity_id=entity_id, method_name=method_desc.name, arguments=arguments
        )
        return OnRemoteMethodCallMsgParserResult(success=True, result=parsed_data)


@dataclass
class OnRemoteMethodCallOptimizedParsedMsgData(ParsedMsgInfo):
    entity_id: int
    method_name: str
    arguments: list


@dataclass
class OnRemoteMethodCallOptimizedMsgParserResult(MsgResult):
    result: OnRemoteMethodCallOptimizedParsedMsgData
    msg_id: int = msgspec.client.onRemoteMethodCallOptimized.id


class OnRemoteMethodCallOptimizedHandler(
    OnRemoteMethodCallHandler, _OptimizedHandlerMixin
):
    def parse(self, msg: Message) -> OnRemoteMethodCallOptimizedMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        res = super().handle(msg)
        pd = OnRemoteMethodCallOptimizedParsedMsgData(
            entity_id=res.result.entity_id,
            method_name=res.result.method_name,
            arguments=res.result.arguments,
        )
        return OnRemoteMethodCallOptimizedMsgParserResult(
            res.success, pd, text=res.text
        )


@dataclass
class OnEntityDestroyedParsedMsgData(ParsedMsgInfo):
    entity_id: int


@dataclass
class OnEntityDestroyedMsgParserResult(MsgResult):
    result: OnEntityDestroyedParsedMsgData
    msg_id: int = msgspec.client.onEntityDestroyed.id


class OnEntityDestroyedHandler(EntityHandler):
    def parse(self, msg: Message) -> OnEntityDestroyedMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        entity_id = msg.get_values()[0]

        desc = self._entity_helper.get_entity_descr_by_eid(entity_id)

        for comp_name in desc.component_names:
            self._game.call_component_method(entity_id, comp_name, "onDetached")

        self._entity_helper.on_entity_destroyed(entity_id)
        self._game.call_entity_destroyed(entity_id)

        return OnEntityDestroyedMsgParserResult(
            success=True, result=OnEntityDestroyedParsedMsgData(entity_id)
        )


@dataclass
class OnEntityEnterWorldParsedMsgData(ParsedMsgInfo):
    entity_id: int = 0
    entity_type_id: int = 0
    is_on_ground: bool = False


@dataclass
class OnEntityEnterWorldMsgParserResult(MsgResult):
    result: OnEntityEnterWorldParsedMsgData
    msg_id: int = msgspec.client.onEntityEnterWorld.id


class OnEntityEnterWorldHandler(EntityHandler, _OnEntityCreatedMixin):
    def parse(self, msg: Message) -> OnEntityEnterWorldMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        data = msg.get_values()[0]
        entity_id, data = self.get_entity_id(data)

        if self._entity_helper.is_entitydefAliasID:
            entity_type_id, offset = kbetype.UINT8.decode(data)
            data = data[offset:]
        else:
            entity_type_id, offset = kbetype.UINT16.decode(data)
            data = data[offset:]

        is_on_ground = False  # noqa
        if data:
            is_on_ground, offset = kbetype.BOOL.decode(data)
            data = data[offset:]

        pd = OnEntityEnterWorldParsedMsgData(entity_id, entity_type_id, is_on_ground)

        desc = self._entity_helper.get_entity_descr_by_uid(entity_type_id)

        if not self._entity_helper.is_player(entity_id):
            # The proxy entity (aka player) is initialized in the onCreatedProxies
            self.on_entity_created(entity_id, desc.name, False)
            self._entity_helper.on_entity_created(
                pd.entity_id, desc.name, is_player=False
            )

        self._game.call_entity_method(entity_id, "onEnterWorld")

        for comp_name in desc.component_names:
            self._game.call_component_method(entity_id, comp_name, "onEnterWorld")

        self._game.update_entity_properties(entity_id, {"onGround": pd.is_on_ground})

        return OnEntityEnterWorldMsgParserResult(success=True, result=pd)


@dataclass
class OnEntityLeaveWorldParsedMsgData(ParsedMsgInfo):
    entity_id: int = NoValue.NO_ENTITY_ID


@dataclass
class OnEntityLeaveWorldMsgParserResult(MsgResult):
    result: OnEntityLeaveWorldParsedMsgData
    msg_id: int = msgspec.client.onEntityLeaveWorld.id


class OnEntityLeaveWorldHandler(EntityHandler):
    def parse(self, msg: Message) -> OnEntityLeaveWorldMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        data = msg.get_values()[0]
        entity_id, data = self.get_entity_id(data)

        desc = self._entity_helper.get_entity_descr_by_eid(entity_id)
        self._entity_helper.on_entity_leave_world(entity_id)

        self._game.call_entity_method(entity_id, "onLeaveWorld")
        for comp_name in desc.component_names:
            self._game.call_component_method(entity_id, comp_name, "onLeaveWorld")

        return OnEntityLeaveWorldMsgParserResult(
            success=True, result=OnEntityLeaveWorldParsedMsgData(entity_id)
        )


@dataclass
class OnEntityLeaveWorldOptimizedParsedMsgData(ParsedMsgInfo):
    entity_id: int = NoValue.NO_ENTITY_ID


@dataclass
class OnEntityLeaveWorldOptimizedMsgParserResult(MsgResult):
    result: OnEntityLeaveWorldOptimizedParsedMsgData
    msg_id: int = msgspec.client.onEntityLeaveWorldOptimized.id


class OnEntityLeaveWorldOptimizedHandler(
    OnEntityLeaveWorldHandler, _OptimizedHandlerMixin
):
    def get_entity_id(self, data: memoryview) -> tuple[int, memoryview]:
        return self.get_optimized_entity_id(data)

    def parse(self, msg: Message) -> OnEntityLeaveWorldOptimizedMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        res: OnEntityLeaveWorldMsgParserResult = super().handle(msg)
        return OnEntityLeaveWorldOptimizedMsgParserResult(
            success=res.success,
            result=OnEntityLeaveWorldOptimizedParsedMsgData(res.result.entity_id),
        )


@dataclass
class OnSetEntityPosAndDirParsedMsgData(ParsedMsgInfo):
    entity_id: int
    position: Position
    direction: Direction


@dataclass
class OnSetEntityPosAndDirMsgParserResult(MsgResult):
    result: OnSetEntityPosAndDirParsedMsgData
    msg_id: int = msgspec.client.onSetEntityPosAndDir.id


class OnSetEntityPosAndDirHandler(EntityHandler):
    def parse(self, msg: Message) -> OnSetEntityPosAndDirMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])
        entity_id, data = self.get_entity_id(data)

        x, offset = kbetype.FLOAT.decode(data)
        data = data[offset:]
        y, offset = kbetype.FLOAT.decode(data)
        data = data[offset:]
        z, offset = kbetype.FLOAT.decode(data)
        data = data[offset:]
        position = Position(x, y, z)

        x, offset = kbetype.FLOAT.decode(data)
        data = data[offset:]
        y, offset = kbetype.FLOAT.decode(data)
        data = data[offset:]
        z, offset = kbetype.FLOAT.decode(data)
        data = data[offset:]
        direction = Direction(x, y, z)

        pd = OnSetEntityPosAndDirParsedMsgData(entity_id, position, direction)

        pose_data = PoseData()
        pose_data.update_position(position)
        pose_data.update_direction(direction)

        self.set_pose(entity_id, pose_data)

        return OnSetEntityPosAndDirMsgParserResult(success=True, result=pd)


@dataclass
class OnEntityEnterSpaceParsedMsgData(ParsedMsgInfo):
    entity_id: int
    space_id: int
    is_on_ground: bool


@dataclass
class OnEntityEnterSpaceMsgParserResult(MsgResult):
    result: OnEntityEnterSpaceParsedMsgData
    msg_id: int = msgspec.client.onEntityEnterSpace.id


class OnEntityEnterSpaceHandler(EntityHandler):
    def parse(self, msg: Message) -> OnEntityEnterSpaceMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])
        entity_id, offset = kbetype.ENTITY_ID.decode(data)
        data = data[offset:]

        space_id, offset = kbetype.SPACE_ID.decode(data)
        data = data[offset:]

        is_on_ground = False
        if data:
            is_on_ground, offset = kbetype.BOOL.decode(data)
            data = data[offset:]

        pd = OnEntityEnterSpaceParsedMsgData(entity_id, space_id, is_on_ground)

        desc = self._entity_helper.get_entity_descr_by_eid(entity_id)

        self._game.update_entity_properties(
            entity_id,
            {
                "spaceID": pd.space_id,
                "onGround": pd.is_on_ground,
            },
        )
        self._game.call_entity_method(entity_id, "onEnterSpace")

        for comp_name in desc.component_names:
            self._game.call_component_method(entity_id, comp_name, "onEnterSpace")

        return OnEntityEnterSpaceMsgParserResult(True, pd)


@dataclass
class OnEntityLeaveSpaceParsedMsgData(ParsedMsgInfo):
    entity_id: int


@dataclass
class OnEntityLeaveSpaceMsgParserResult(MsgResult):
    result: OnEntityLeaveSpaceParsedMsgData
    msg_id: int = msgspec.client.onEntityLeaveSpace.id


class OnEntityLeaveSpaceHandler(EntityHandler):
    def parse(self, msg: Message) -> OnEntityLeaveSpaceMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])
        entity_id, offset = kbetype.ENTITY_ID.decode(data)
        data = data[offset:]

        pd = OnEntityLeaveSpaceParsedMsgData(entity_id)

        desc = self._entity_helper.get_entity_descr_by_eid(entity_id)
        self._game.call_entity_method(entity_id, "onLeaveSpace")

        for comp_name in desc.component_names:
            self._game.call_component_method(entity_id, comp_name, "onLeaveSpace")

        return OnEntityLeaveSpaceMsgParserResult(True, pd)


@dataclass
class OnUpdateBasePosParsedMsgData(ParsedMsgInfo):
    position: Position


@dataclass
class OnUpdateBasePosMsgParserResult(MsgResult):
    result: OnUpdateBasePosParsedMsgData
    msg_id: int = msgspec.client.onUpdateBasePos.id


class OnUpdateBasePosHandler(EntityHandler):
    def parse(self, msg: Message) -> OnUpdateBasePosMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        entity_id = self._entity_helper.get_player_id()

        pose_data = PoseData(*msg.get_values())
        self.set_pose(entity_id, pose_data)

        pd = OnUpdateBasePosParsedMsgData(pose_data.position)
        return OnUpdateBasePosMsgParserResult(True, pd)


@dataclass
class OnUpdateBaseDirParsedMsgData(ParsedMsgInfo):
    direction: Direction


@dataclass
class OnUpdateBaseDirMsgParserResult(MsgResult):
    result: OnUpdateBaseDirParsedMsgData
    msg_id: int = msgspec.client.onUpdateBaseDir.id


class OnUpdateBaseDirHandler(EntityHandler):
    def parse(self, msg: Message) -> OnUpdateBaseDirMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        entity_id = self._entity_helper.get_player_id()
        pd: OnUpdateBaseDirParsedMsgData = OnUpdateBaseDirParsedMsgData(
            Direction(*msg.get_values())
        )
        pose_data = PoseData()
        pose_data.update_direction(pd.direction)
        self.set_pose(entity_id, pose_data)
        return OnUpdateBaseDirMsgParserResult(True, pd)


@dataclass
class OnUpdateBasePosXZParsedMsgData(ParsedMsgInfo):
    x: float
    z: float


@dataclass
class OnUpdateBasePosXZMsgParserResult(MsgResult):
    result: OnUpdateBasePosXZParsedMsgData
    msg_id: int = msgspec.client.onUpdateBasePosXZ.id


class OnUpdateBasePosXZHandler(EntityHandler):
    def parse(self, msg: Message) -> OnUpdateBasePosXZMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        entity_id = self._entity_helper.get_player_id()
        values: tuple[Any, ...] = msg.get_values()
        pd = OnUpdateBasePosXZParsedMsgData(*values)

        pose_data = PoseData(x=pd.x, z=pd.z)
        self.set_pose(entity_id, pose_data)

        return OnUpdateBasePosXZMsgParserResult(True, pd)


@dataclass
class OnUpdateDataParsedMsgData(ParsedMsgInfo):
    pass


@dataclass
class OnUpdateDataMsgParserResult(MsgResult):
    result: OnUpdateDataParsedMsgData
    msg_id: int = msgspec.client.onUpdateData.id


class OnUpdateDataHandler(EntityHandler, _OptimizedHandlerMixin):
    def parse(self, msg: Message) -> OnUpdateDataMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        res = super().handle(msg)
        return OnUpdateDataMsgParserResult(
            res.success, OnUpdateDataParsedMsgData(), text=res.text
        )


@dataclass
class OnUpdateData_XZ_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float


@dataclass
class OnUpdateData_XZ_MsgParserResult(_OnUpdateData_XYZ_YPR_BaseMsgParserResult):
    result: OnUpdateData_XZ_ParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xz.id


class OnUpdateData_XZ_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XZ_ParsedMsgData
    _handler_result_cls = OnUpdateData_XZ_MsgParserResult


@dataclass
class OnUpdateData_YPR_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    yaw: float
    pitch: float
    roll: float


@dataclass
class OnUpdateData_YPR_MsgParserResult(_OnUpdateData_XYZ_YPR_BaseMsgParserResult):
    result: OnUpdateData_YPR_ParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_ypr.id


class OnUpdateData_YPR_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_YPR_ParsedMsgData
    _handler_result_cls = OnUpdateData_YPR_MsgParserResult


@dataclass
class OnUpdateData_YP_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    yaw: float
    pitch: float


@dataclass
class OnUpdateData_YP_MsgParserResult(_OnUpdateData_XYZ_YPR_BaseMsgParserResult):
    result: OnUpdateData_YP_ParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_yp.id


class OnUpdateData_YP_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_YP_ParsedMsgData
    _handler_result_cls = OnUpdateData_YP_MsgParserResult


@dataclass
class OnUpdateData_YR_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    yaw: float
    roll: float


@dataclass
class OnUpdateData_YR_MsgParserResult(_OnUpdateData_XYZ_YPR_BaseMsgParserResult):
    result: OnUpdateData_YR_ParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_yr.id


class OnUpdateData_YR_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_YR_ParsedMsgData
    _handler_result_cls = OnUpdateData_YR_MsgParserResult


@dataclass
class OnUpdateData_PR_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    pitch: float
    roll: float


@dataclass
class OnUpdateData_PR_MsgParserResult(_OnUpdateData_XYZ_YPR_BaseMsgParserResult):
    result: OnUpdateData_PR_ParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_pr.id


class OnUpdateData_PR_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_PR_ParsedMsgData
    _handler_result_cls = OnUpdateData_PR_MsgParserResult


@dataclass
class OnUpdateData_Y_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    yaw: float


@dataclass
class OnUpdateData_Y_MsgParserResult(_OnUpdateData_XYZ_YPR_BaseMsgParserResult):
    result: OnUpdateData_Y_ParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_y.id


class OnUpdateData_Y_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_Y_ParsedMsgData
    _handler_result_cls = OnUpdateData_Y_MsgParserResult


@dataclass
class OnUpdateData_P_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    pitch: float


@dataclass
class OnUpdateData_P_MsgParserResult(_OnUpdateData_XYZ_YPR_BaseMsgParserResult):
    result: OnUpdateData_P_ParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_p.id


class OnUpdateData_P_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_P_ParsedMsgData
    _handler_result_cls = OnUpdateData_P_MsgParserResult


@dataclass
class OnUpdateData_R_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    roll: float


@dataclass
class OnUpdateData_R_MsgParserResult(_OnUpdateData_XYZ_YPR_BaseMsgParserResult):
    result: OnUpdateData_R_ParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_r.id


class OnUpdateData_R_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_R_ParsedMsgData
    _handler_result_cls = OnUpdateData_R_MsgParserResult


@dataclass
class OnUpdateData_XZ_YPR_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float
    yaw: float
    pitch: float
    roll: float


@dataclass
class OnUpdateData_XZ_YPR_MsgParserResult(_OnUpdateData_XYZ_YPR_BaseMsgParserResult):
    result: OnUpdateData_XZ_YPR_ParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xz_ypr.id


class OnUpdateData_XZ_YPR_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XZ_YPR_ParsedMsgData
    _handler_result_cls = OnUpdateData_XZ_YPR_MsgParserResult


@dataclass
class OnUpdateData_XZ_YP_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float
    yaw: float
    pitch: float


@dataclass
class OnUpdateData_XZ_YP_MsgParserResult(_OnUpdateData_XYZ_YPR_BaseMsgParserResult):
    result: OnUpdateData_XZ_YP_ParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xz_yp.id


class OnUpdateData_XZ_YP_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XZ_YP_ParsedMsgData
    _handler_result_cls = OnUpdateData_XZ_YP_MsgParserResult


@dataclass
class OnUpdateData_XZ_YR_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float
    yaw: float
    roll: float


@dataclass
class OnUpdateData_XZ_YR_MsgParserResult(_OnUpdateData_XYZ_YPR_BaseMsgParserResult):
    result: OnUpdateData_XZ_YR_ParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xz_yr.id


class OnUpdateData_XZ_YR_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XZ_YR_ParsedMsgData
    _handler_result_cls = OnUpdateData_XZ_YR_MsgParserResult


@dataclass
class OnUpdateData_XZ_PR_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float
    yaw: float
    pitch: float
    roll: float


@dataclass
class OnUpdateData_XZ_PR_MsgParserResult(_OnUpdateData_XYZ_YPR_BaseMsgParserResult):
    result: OnUpdateData_XZ_PR_ParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xz_pr.id


class OnUpdateData_XZ_PR_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XZ_PR_ParsedMsgData
    _handler_result_cls = OnUpdateData_XZ_PR_MsgParserResult


@dataclass
class OnUpdateData_XZ_Y_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float
    yaw: float


@dataclass
class OnUpdateData_XZ_Y_MsgParserResult(_OnUpdateData_XYZ_YPR_BaseMsgParserResult):
    result: OnUpdateData_XZ_Y_ParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xz_y.id


class OnUpdateData_XZ_Y_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XZ_Y_ParsedMsgData
    _handler_result_cls = OnUpdateData_XZ_Y_MsgParserResult


@dataclass
class OnUpdateData_XZ_P_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float
    pitch: float


@dataclass
class OnUpdateData_XZ_P_MsgParserResult(_OnUpdateData_XYZ_YPR_BaseMsgParserResult):
    result: OnUpdateData_XZ_P_ParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xz_p.id


class OnUpdateData_XZ_P_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XZ_P_ParsedMsgData
    _handler_result_cls = OnUpdateData_XZ_P_MsgParserResult


@dataclass
class OnUpdateData_XZ_R_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float
    roll: float


@dataclass
class OnUpdateData_XZ_R_MsgParserResult(_OnUpdateData_XYZ_YPR_BaseMsgParserResult):
    result: OnUpdateData_XZ_R_ParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xz_r.id


class OnUpdateData_XZ_R_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XZ_R_ParsedMsgData
    _handler_result_cls = OnUpdateData_XZ_R_MsgParserResult


@dataclass
class OnUpdateData_XYZ_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float
    y: float


@dataclass
class OnUpdateData_XYZ_MsgParserResult(_OnUpdateData_XYZ_YPR_BaseMsgParserResult):
    result: OnUpdateData_XYZ_ParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xyz.id


class OnUpdateData_XYZ_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XYZ_ParsedMsgData
    _handler_result_cls = OnUpdateData_XYZ_MsgParserResult


@dataclass
class OnUpdateData_XYZ_YPR_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float
    y: float
    yaw: float
    pitch: float
    roll: float


@dataclass
class OnUpdateData_XYZ_YPR_MsgParserResult(_OnUpdateData_XYZ_YPR_BaseMsgParserResult):
    result: OnUpdateData_XYZ_YPR_ParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xyz_ypr.id


class OnUpdateData_XYZ_YPR_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XYZ_YPR_ParsedMsgData
    _handler_result_cls = OnUpdateData_XYZ_YPR_MsgParserResult


@dataclass
class OnUpdateData_XYZ_YP_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float
    y: float
    yaw: float
    pitch: float


@dataclass
class OnUpdateData_XYZ_YP_MsgParserResult(_OnUpdateData_XYZ_YPR_BaseMsgParserResult):
    result: OnUpdateData_XYZ_YP_ParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xyz_yp.id


class OnUpdateData_XYZ_YP_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XYZ_YP_ParsedMsgData
    _handler_result_cls = OnUpdateData_XYZ_YP_MsgParserResult


@dataclass
class OnUpdateData_XYZ_YR_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float
    y: float
    yaw: float
    pitch: float


@dataclass
class OnUpdateData_XYZ_YR_MsgParserResult(_OnUpdateData_XYZ_YPR_BaseMsgParserResult):
    result: OnUpdateData_XYZ_YR_ParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xyz_yr.id


class OnUpdateData_XYZ_YR_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XYZ_YR_ParsedMsgData
    _handler_result_cls = OnUpdateData_XYZ_YR_MsgParserResult


@dataclass
class OnUpdateData_XYZ_PR_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float
    y: float
    pitch: float
    roll: float


@dataclass
class OnUpdateData_XYZ_PR_MsgParserResult(_OnUpdateData_XYZ_YPR_BaseMsgParserResult):
    result: OnUpdateData_XYZ_PR_ParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xyz_pr.id


class OnUpdateData_XYZ_PR_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XYZ_PR_ParsedMsgData
    _handler_result_cls = OnUpdateData_XYZ_PR_MsgParserResult


@dataclass
class OnUpdateData_XYZ_Y_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float
    y: float
    yaw: float


@dataclass
class OnUpdateData_XYZ_Y_MsgParserResult(_OnUpdateData_XYZ_YPR_BaseMsgParserResult):
    result: OnUpdateData_XYZ_Y_ParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xyz_y.id


class OnUpdateData_XYZ_Y_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XYZ_Y_ParsedMsgData
    _handler_result_cls = OnUpdateData_XYZ_Y_MsgParserResult


@dataclass
class OnUpdateData_XYZ_P_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float
    y: float
    pitch: float


@dataclass
class OnUpdateData_XYZ_P_MsgParserResult(_OnUpdateData_XYZ_YPR_BaseMsgParserResult):
    result: OnUpdateData_XYZ_P_ParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xyz_p.id


class OnUpdateData_XYZ_P_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XYZ_P_ParsedMsgData
    _handler_result_cls = OnUpdateData_XYZ_P_MsgParserResult


@dataclass
class OnUpdateData_XYZ_R_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float
    y: float
    pitch: float


@dataclass
class OnUpdateData_XYZ_R_MsgParserResult(_OnUpdateData_XYZ_YPR_BaseMsgParserResult):
    result: OnUpdateData_XYZ_R_ParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xyz_r.id


class OnUpdateData_XYZ_R_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XYZ_R_ParsedMsgData
    _handler_result_cls = OnUpdateData_XYZ_R_MsgParserResult


@dataclass
class OnUpdateData_Y_OptimizedParsedMsgData(EntityParsedMsgData):
    yaw: float


@dataclass
class OnUpdateData_Y_OptimizedMsgParserResult(EntityMsgParserResult):
    result: OnUpdateData_Y_OptimizedParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_y_optimized.id


class OnUpdateData_Y_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):
    def parse_data(
        self, data: memoryview, entity_id: int
    ) -> tuple[OnUpdateData_Y_OptimizedParsedMsgData, memoryview]:
        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle = kbemath.int82angle(value)
        pd = OnUpdateData_Y_OptimizedParsedMsgData(angle)
        return pd, data

    def process_parsed_data(
        self, pd: OnUpdateData_Y_OptimizedParsedMsgData, entity_id: int
    ) -> OnUpdateData_Y_OptimizedMsgParserResult:
        pose_data = PoseData(**{
            "yaw": pd.yaw,
        })
        self.set_pose(entity_id, pose_data)

        return OnUpdateData_Y_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_R_OptimizedParsedMsgData(EntityParsedMsgData):
    roll: float


@dataclass
class OnUpdateData_R_OptimizedMsgParserResult(EntityMsgParserResult):
    result: OnUpdateData_R_OptimizedParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_r_optimized.id


class OnUpdateData_R_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):
    def parse_data(
        self, data: memoryview, entity_id: int
    ) -> tuple[OnUpdateData_R_OptimizedParsedMsgData, memoryview]:
        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle = kbemath.int82angle(value)
        pd = OnUpdateData_R_OptimizedParsedMsgData(angle)
        return pd, data

    def process_parsed_data(
        self, pd: OnUpdateData_R_OptimizedParsedMsgData, entity_id: int
    ) -> OnUpdateData_R_OptimizedMsgParserResult:
        pose_data = PoseData(**{
            "roll": pd.roll,
        })
        self.set_pose(entity_id, pose_data)

        return OnUpdateData_R_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_P_OptimizedParsedMsgData(EntityParsedMsgData):
    pitch: float


@dataclass
class OnUpdateData_P_OptimizedMsgParserResult(EntityMsgParserResult):
    result: OnUpdateData_P_OptimizedParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_p_optimized.id


class OnUpdateData_P_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):
    def parse_data(
        self, data: memoryview, entity_id: int
    ) -> tuple[OnUpdateData_P_OptimizedParsedMsgData, memoryview]:
        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle = kbemath.int82angle(value)
        pd = OnUpdateData_P_OptimizedParsedMsgData(angle)
        return pd, data

    def process_parsed_data(
        self, pd: OnUpdateData_P_OptimizedParsedMsgData, entity_id: int
    ) -> OnUpdateData_P_OptimizedMsgParserResult:
        pose_data = PoseData(**{
            "pitch": pd.pitch,
        })
        self.set_pose(entity_id, pose_data)

        return OnUpdateData_P_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_YP_OptimizedParsedMsgData(EntityParsedMsgData):
    yaw: float
    pitch: float


@dataclass
class OnUpdateData_YP_OptimizedMsgParserResult(EntityMsgParserResult):
    result: OnUpdateData_YP_OptimizedParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_yp_optimized.id


class OnUpdateData_YP_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):
    def parse_data(
        self, data: memoryview, entity_id: int
    ) -> tuple[OnUpdateData_YP_OptimizedParsedMsgData, memoryview]:
        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)
        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_2 = kbemath.int82angle(value)
        pd = OnUpdateData_YP_OptimizedParsedMsgData(angle_1, angle_2)
        return pd, data

    def process_parsed_data(
        self, pd: OnUpdateData_YP_OptimizedParsedMsgData, entity_id: int
    ) -> OnUpdateData_YP_OptimizedMsgParserResult:
        pose_data = PoseData(**{
            "yaw": pd.yaw,
            "pitch": pd.pitch,
        })
        self.set_pose(entity_id, pose_data)

        return OnUpdateData_YP_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_YR_OptimizedParsedMsgData(EntityParsedMsgData):
    yaw: float
    roll: float


@dataclass
class OnUpdateData_YR_OptimizedMsgParserResult(EntityMsgParserResult):
    result: OnUpdateData_YR_OptimizedParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_yr_optimized.id


class OnUpdateData_YR_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):
    def parse_data(
        self, data: memoryview, entity_id: int
    ) -> tuple[OnUpdateData_YR_OptimizedParsedMsgData, memoryview]:
        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)
        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_2 = kbemath.int82angle(value)
        pd = OnUpdateData_YR_OptimizedParsedMsgData(angle_1, angle_2)
        return pd, data

    def process_parsed_data(
        self, pd: OnUpdateData_YR_OptimizedParsedMsgData, entity_id: int
    ) -> OnUpdateData_YR_OptimizedMsgParserResult:
        pose_data = PoseData(**{
            "yaw": pd.yaw,
            "roll": pd.roll,
        })
        self.set_pose(entity_id, pose_data)

        return OnUpdateData_YR_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_PR_OptimizedParsedMsgData(EntityParsedMsgData):
    pitch: float
    roll: float


@dataclass
class OnUpdateData_PR_OptimizedMsgParserResult(EntityMsgParserResult):
    result: OnUpdateData_PR_OptimizedParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_pr_optimized.id


class OnUpdateData_PR_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):
    def parse_data(
        self, data: memoryview, entity_id: int
    ) -> tuple[OnUpdateData_PR_OptimizedParsedMsgData, memoryview]:
        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_2 = kbemath.int82angle(value)

        pd = OnUpdateData_PR_OptimizedParsedMsgData(angle_1, angle_2)
        return pd, data

    def process_parsed_data(
        self, pd: OnUpdateData_PR_OptimizedParsedMsgData, entity_id: int
    ) -> OnUpdateData_PR_OptimizedMsgParserResult:
        pose_data = PoseData(**{
            "pitch": pd.pitch,
            "roll": pd.roll,
        })
        self.set_pose(entity_id, pose_data)

        return OnUpdateData_PR_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_YPR_OptimizedParsedMsgData(EntityParsedMsgData):
    yaw: float
    pitch: float
    roll: float


@dataclass
class OnUpdateData_YPR_OptimizedMsgParserResult(EntityMsgParserResult):
    result: OnUpdateData_YPR_OptimizedParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_ypr_optimized.id


class OnUpdateData_YPR_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):
    def parse_data(
        self, data: memoryview, entity_id: int
    ) -> tuple[OnUpdateData_YPR_OptimizedParsedMsgData, memoryview]:
        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_2 = kbemath.int82angle(value)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_3 = kbemath.int82angle(value)

        pd = OnUpdateData_YPR_OptimizedParsedMsgData(angle_1, angle_2, angle_3)
        return pd, data

    def process_parsed_data(
        self, pd: OnUpdateData_YPR_OptimizedParsedMsgData, entity_id: int
    ) -> OnUpdateData_YPR_OptimizedMsgParserResult:
        pose_data = PoseData(**{
            "yaw": pd.yaw,
            "pitch": pd.pitch,
            "roll": pd.roll,
        })
        self.set_pose(entity_id, pose_data)

        return OnUpdateData_YPR_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XZ_OptimizedParsedMsgData(EntityParsedMsgData):
    x: float
    z: float


@dataclass
class OnUpdateData_XZ_OptimizedMsgParserResult(EntityMsgParserResult):
    result: OnUpdateData_XZ_OptimizedParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xz_optimized.id


class OnUpdateData_XZ_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):
    def parse_data(
        self, data: memoryview, entity_id: int
    ) -> tuple[OnUpdateData_XZ_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)
        pd = OnUpdateData_XZ_OptimizedParsedMsgData(v2.x, v2.y)
        return pd, data

    def process_parsed_data(
        self, pd: OnUpdateData_XZ_OptimizedParsedMsgData, entity_id: int
    ) -> OnUpdateData_XZ_OptimizedMsgParserResult:
        pose_data = PoseData(**{
            "x": pd.x,
            "z": pd.z,
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XZ_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XZ_YPR_OptimizedParsedMsgData(EntityParsedMsgData):
    x: float
    z: float
    yaw: float
    pitch: float
    roll: float


@dataclass
class OnUpdateData_XZ_YPR_OptimizedMsgParserResult(EntityMsgParserResult):
    result: OnUpdateData_XZ_YPR_OptimizedParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xz_ypr_optimized.id


class OnUpdateData_XZ_YPR_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):
    def parse_data(
        self, data: memoryview, entity_id: int
    ) -> tuple[OnUpdateData_XZ_YPR_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        yaw = kbemath.int82angle(value)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        pitch = kbemath.int82angle(value)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        roll = kbemath.int82angle(value)

        pd = OnUpdateData_XZ_YPR_OptimizedParsedMsgData(v2.x, v2.y, yaw, pitch, roll)
        return pd, data

    def process_parsed_data(
        self, pd: OnUpdateData_XZ_YPR_OptimizedParsedMsgData, entity_id: int
    ) -> OnUpdateData_XZ_YPR_OptimizedMsgParserResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XZ_YPR_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XZ_YP_OptimizedParsedMsgData(EntityParsedMsgData):
    x: float
    z: float
    yaw: float
    pitch: float


@dataclass
class OnUpdateData_XZ_YP_OptimizedMsgParserResult(EntityMsgParserResult):
    result: OnUpdateData_XZ_YP_OptimizedParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xz_yp_optimized.id


class OnUpdateData_XZ_YP_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):
    def parse_data(
        self, data: memoryview, entity_id: int
    ) -> tuple[OnUpdateData_XZ_YP_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        yaw = kbemath.int82angle(value)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        pitch = kbemath.int82angle(value)

        pd = OnUpdateData_XZ_YP_OptimizedParsedMsgData(v2.x, v2.y, yaw, pitch)
        return pd, data

    def process_parsed_data(
        self, pd: OnUpdateData_XZ_YP_OptimizedParsedMsgData, entity_id: int
    ) -> OnUpdateData_XZ_YP_OptimizedMsgParserResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XZ_YP_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XZ_YR_OptimizedParsedMsgData(EntityParsedMsgData):
    x: float
    z: float
    yaw: float
    roll: float


@dataclass
class OnUpdateData_XZ_YR_OptimizedMsgParserResult(EntityMsgParserResult):
    result: OnUpdateData_XZ_YR_OptimizedParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xz_yr_optimized.id


class OnUpdateData_XZ_YR_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):
    def parse_data(
        self, data: memoryview, entity_id: int
    ) -> tuple[OnUpdateData_XZ_YR_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        yaw = kbemath.int82angle(value)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        roll = kbemath.int82angle(value)

        pd = OnUpdateData_XZ_YR_OptimizedParsedMsgData(v2.x, v2.y, yaw, roll)
        return pd, data

    def process_parsed_data(
        self, pd: OnUpdateData_XZ_YR_OptimizedParsedMsgData, entity_id: int
    ) -> OnUpdateData_XZ_YR_OptimizedMsgParserResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XZ_YR_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XZ_PR_OptimizedParsedMsgData(EntityParsedMsgData):
    x: float
    z: float
    pitch: float
    roll: float


@dataclass
class OnUpdateData_XZ_PR_OptimizedMsgParserResult(EntityMsgParserResult):
    result: OnUpdateData_XZ_PR_OptimizedParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xz_pr_optimized.id


class OnUpdateData_XZ_PR_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):
    def parse_data(
        self, data: memoryview, entity_id: int
    ) -> tuple[OnUpdateData_XZ_PR_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        pitch = kbemath.int82angle(value)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        roll = kbemath.int82angle(value)

        pd = OnUpdateData_XZ_PR_OptimizedParsedMsgData(v2.x, v2.y, pitch, roll)
        return pd, data

    def process_parsed_data(
        self, pd: OnUpdateData_XZ_PR_OptimizedParsedMsgData, entity_id: int
    ) -> OnUpdateData_XZ_PR_OptimizedMsgParserResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XZ_PR_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XZ_Y_OptimizedParsedMsgData(EntityParsedMsgData):
    x: float
    z: float
    yaw: float


@dataclass
class OnUpdateData_XZ_Y_OptimizedMsgParserResult(EntityMsgParserResult):
    result: OnUpdateData_XZ_Y_OptimizedParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xz_y_optimized.id


class OnUpdateData_XZ_Y_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):
    def parse_data(
        self, data: memoryview, entity_id: int
    ) -> tuple[OnUpdateData_XZ_Y_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        yaw = kbemath.int82angle(value)

        pd = OnUpdateData_XZ_Y_OptimizedParsedMsgData(v2.x, v2.y, yaw)
        return pd, data

    def process_parsed_data(
        self, pd: OnUpdateData_XZ_Y_OptimizedParsedMsgData, entity_id: int
    ) -> OnUpdateData_XZ_Y_OptimizedMsgParserResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XZ_Y_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XZ_P_OptimizedParsedMsgData(EntityParsedMsgData):
    x: float
    z: float
    pitch: float


@dataclass
class OnUpdateData_XZ_P_OptimizedMsgParserResult(EntityMsgParserResult):
    result: OnUpdateData_XZ_P_OptimizedParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xz_p_optimized.id


class OnUpdateData_XZ_P_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):
    def parse_data(
        self, data: memoryview, entity_id: int
    ) -> tuple[OnUpdateData_XZ_P_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        pitch = kbemath.int82angle(value)

        pd = OnUpdateData_XZ_P_OptimizedParsedMsgData(v2.x, v2.y, pitch)
        return pd, data

    def process_parsed_data(
        self, pd: OnUpdateData_XZ_P_OptimizedParsedMsgData, entity_id: int
    ) -> OnUpdateData_XZ_P_OptimizedMsgParserResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XZ_P_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XZ_R_OptimizedParsedMsgData(EntityParsedMsgData):
    x: float
    z: float
    roll: float


@dataclass
class OnUpdateData_XZ_R_OptimizedMsgParserResult(EntityMsgParserResult):
    result: OnUpdateData_XZ_R_OptimizedParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xz_r_optimized.id


class OnUpdateData_XZ_R_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):
    def parse_data(
        self, data: memoryview, entity_id: int
    ) -> tuple[OnUpdateData_XZ_R_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        roll = kbemath.int82angle(value)

        pd: OnUpdateData_XZ_R_OptimizedParsedMsgData = (
            OnUpdateData_XZ_R_OptimizedParsedMsgData(v2.x, v2.y, roll)
        )
        return pd, data

    def process_parsed_data(
        self, pd: OnUpdateData_XZ_R_OptimizedParsedMsgData, entity_id: int
    ) -> OnUpdateData_XZ_R_OptimizedMsgParserResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XZ_R_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XYZ_OptimizedParsedMsgData(EntityParsedMsgData):
    x: float
    y: float
    z: float


@dataclass
class OnUpdateData_XYZ_OptimizedMsgParserResult(EntityMsgParserResult):
    result: OnUpdateData_XYZ_OptimizedParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xyz_optimized.id


class OnUpdateData_XYZ_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):
    def parse_data(
        self, data: memoryview, entity_id: int
    ) -> tuple[OnUpdateData_XYZ_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)
        y, data = _OptimizedXYZReader.read_packed_y(data)
        pd = OnUpdateData_XYZ_OptimizedParsedMsgData(v2.x, y, v2.y)
        return pd, data

    def process_parsed_data(
        self, pd: OnUpdateData_XYZ_OptimizedParsedMsgData, entity_id: int
    ) -> OnUpdateData_XYZ_OptimizedMsgParserResult:
        pose_data = PoseData(**{
            "x": pd.x,
            "y": pd.y,
            "z": pd.z,
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XYZ_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XYZ_YPR_OptimizedParsedMsgData(EntityParsedMsgData):
    x: float
    y: float
    z: float
    yaw: float
    pitch: float
    roll: float


@dataclass
class OnUpdateData_XYZ_YPR_OptimizedMsgParserResult(EntityMsgParserResult):
    result: OnUpdateData_XYZ_YPR_OptimizedParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xyz_ypr_optimized.id


class OnUpdateData_XYZ_YPR_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):
    def parse_data(
        self, data: memoryview, entity_id: int
    ) -> tuple[OnUpdateData_XYZ_YPR_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)
        y, data = _OptimizedXYZReader.read_packed_y(data)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_2 = kbemath.int82angle(value)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_3 = kbemath.int82angle(value)

        pd = OnUpdateData_XYZ_YPR_OptimizedParsedMsgData(
            v2.x, y, v2.y, angle_1, angle_2, angle_3
        )
        return pd, data

    def process_parsed_data(
        self, pd: OnUpdateData_XYZ_YPR_OptimizedParsedMsgData, entity_id: int
    ) -> OnUpdateData_XYZ_YPR_OptimizedMsgParserResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XYZ_YPR_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XYZ_YP_OptimizedParsedMsgData(EntityParsedMsgData):
    x: float
    y: float
    z: float
    yaw: float
    pitch: float


@dataclass
class OnUpdateData_XYZ_YP_OptimizedMsgParserResult(EntityMsgParserResult):
    result: OnUpdateData_XYZ_YP_OptimizedParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xyz_yp_optimized.id


class OnUpdateData_XYZ_YP_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):
    def parse_data(
        self, data: memoryview, entity_id: int
    ) -> tuple[OnUpdateData_XYZ_YP_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)
        y, data = _OptimizedXYZReader.read_packed_y(data)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_2 = kbemath.int82angle(value)

        pd = OnUpdateData_XYZ_YP_OptimizedParsedMsgData(v2.x, y, v2.y, angle_1, angle_2)
        return pd, data

    def process_parsed_data(
        self, pd: OnUpdateData_XYZ_YP_OptimizedParsedMsgData, entity_id: int
    ) -> OnUpdateData_XYZ_YP_OptimizedMsgParserResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XYZ_YP_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XYZ_YR_OptimizedParsedMsgData(EntityParsedMsgData):
    x: float
    y: float
    z: float
    yaw: float
    roll: float


@dataclass
class OnUpdateData_XYZ_YR_OptimizedMsgParserResult(EntityMsgParserResult):
    result: OnUpdateData_XYZ_YR_OptimizedParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xyz_yr_optimized.id


class OnUpdateData_XYZ_YR_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):
    def parse_data(
        self, data: memoryview, entity_id: int
    ) -> tuple[OnUpdateData_XYZ_YR_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)
        y, data = _OptimizedXYZReader.read_packed_y(data)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_2 = kbemath.int82angle(value)

        pd = OnUpdateData_XYZ_YR_OptimizedParsedMsgData(v2.x, y, v2.y, angle_1, angle_2)
        return pd, data

    def process_parsed_data(
        self, pd: OnUpdateData_XYZ_YR_OptimizedParsedMsgData, entity_id: int
    ) -> OnUpdateData_XYZ_YR_OptimizedMsgParserResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XYZ_YR_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XYZ_PR_OptimizedParsedMsgData(EntityParsedMsgData):
    x: float
    y: float
    z: float
    pitch: float
    roll: float


@dataclass
class OnUpdateData_XYZ_PR_OptimizedMsgParserResult(EntityMsgParserResult):
    result: OnUpdateData_XYZ_PR_OptimizedParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xyz_pr_optimized.id


class OnUpdateData_XYZ_PR_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):
    def parse_data(
        self, data: memoryview, entity_id: int
    ) -> tuple[OnUpdateData_XYZ_PR_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)
        y, data = _OptimizedXYZReader.read_packed_y(data)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_2 = kbemath.int82angle(value)

        pd = OnUpdateData_XYZ_PR_OptimizedParsedMsgData(v2.x, y, v2.y, angle_1, angle_2)
        return pd, data

    def process_parsed_data(
        self, pd: OnUpdateData_XYZ_PR_OptimizedParsedMsgData, entity_id: int
    ) -> OnUpdateData_XYZ_PR_OptimizedMsgParserResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XYZ_PR_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XYZ_Y_OptimizedParsedMsgData(EntityParsedMsgData):
    x: float
    y: float
    z: float
    yaw: float


@dataclass
class OnUpdateData_XYZ_Y_OptimizedMsgParserResult(EntityMsgParserResult):
    result: OnUpdateData_XYZ_Y_OptimizedParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xyz_y_optimized.id


class OnUpdateData_XYZ_Y_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):
    def parse_data(
        self, data: memoryview, entity_id: int
    ) -> tuple[OnUpdateData_XYZ_Y_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)
        y, data = _OptimizedXYZReader.read_packed_y(data)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)

        pd = OnUpdateData_XYZ_Y_OptimizedParsedMsgData(v2.x, y, v2.y, angle_1)
        return pd, data

    def process_parsed_data(
        self, pd: OnUpdateData_XYZ_Y_OptimizedParsedMsgData, entity_id: int
    ) -> OnUpdateData_XYZ_Y_OptimizedMsgParserResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XYZ_Y_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XYZ_P_OptimizedParsedMsgData(EntityParsedMsgData):
    x: float
    y: float
    z: float
    pitch: float


@dataclass
class OnUpdateData_XYZ_P_OptimizedMsgParserResult(EntityMsgParserResult):
    result: OnUpdateData_XYZ_P_OptimizedParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xyz_p_optimized.id


class OnUpdateData_XYZ_P_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):
    def parse_data(
        self, data: memoryview, entity_id: int
    ) -> tuple[OnUpdateData_XYZ_P_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)
        y, data = _OptimizedXYZReader.read_packed_y(data)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)

        pd = OnUpdateData_XYZ_P_OptimizedParsedMsgData(v2.x, y, v2.y, angle_1)
        return pd, data

    def process_parsed_data(
        self, pd: OnUpdateData_XYZ_P_OptimizedParsedMsgData, entity_id: int
    ) -> OnUpdateData_XYZ_P_OptimizedMsgParserResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XYZ_P_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XYZ_R_OptimizedParsedMsgData(EntityParsedMsgData):
    x: float
    y: float
    z: float
    roll: float


@dataclass
class OnUpdateData_XYZ_R_OptimizedMsgParserResult(EntityMsgParserResult):
    result: OnUpdateData_XYZ_R_OptimizedParsedMsgData
    msg_id: int = msgspec.client.onUpdateData_xyz_r_optimized.id


class OnUpdateData_XYZ_R_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):
    def parse_data(
        self, data: memoryview, entity_id: int
    ) -> tuple[OnUpdateData_XYZ_R_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)
        y, data = _OptimizedXYZReader.read_packed_y(data)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)

        pd = OnUpdateData_XYZ_R_OptimizedParsedMsgData(v2.x, y, v2.y, angle_1)
        return pd, data

    def process_parsed_data(
        self, pd: OnUpdateData_XYZ_R_OptimizedParsedMsgData, entity_id: int
    ) -> OnUpdateData_XYZ_R_OptimizedMsgParserResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XYZ_R_OptimizedMsgParserResult(True, pd)


@dataclass
class OnControlEntityParsedMsgData(EntityParsedMsgData):
    is_controlled: bool


@dataclass
class OnControlEntityMsgParserResult(MsgResult):
    success: bool
    result: OnControlEntityParsedMsgData
    msg_id: int = msgspec.client.onControlEntity.id
    text: str = ""


class OnControlEntityHandler(EntityHandler):
    def parse(self, msg: Message) -> OnControlEntityMsgParserResult:
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])
        entity_id, data = self.get_entity_id(data)
        is_controlled, offset = kbetype.BOOL.decode(data)
        data = data[offset:]
        # TODO: [2022-09-07 13:44 burov_alexey@mail.ru]:
        # I cannot find the server code that sends the "onControlEntity" message.
        # I think it's legacy code thats why I do nothin in this handler.
        return OnControlEntityMsgParserResult(
            True, OnControlEntityParsedMsgData(is_controlled)
        )


__all__ = [
    "EntityHandler",
    "OnCreatedProxiesHandler",
    "OnEntityDestroyedHandler",
    "OnEntityEnterWorldHandler",
    "OnEntityLeaveWorldHandler",
    "OnEntityEnterSpaceHandler",
    "OnEntityLeaveSpaceHandler",
    "OnEntityLeaveWorldOptimizedHandler",
    "OnSetEntityPosAndDirHandler",
    "OnUpdatePropertysHandler",
    "OnUpdatePropertysOptimizedHandler",
    "OnRemoteMethodCallHandler",
    "OnRemoteMethodCallOptimizedHandler",
    "OnUpdateBasePosHandler",
    "OnUpdateBaseDirHandler",
    "OnUpdateBasePosXZHandler",
    "OnUpdateDataHandler",
    "OnUpdateData_YPR_Handler",
    "OnUpdateData_YP_Handler",
    "OnUpdateData_YR_Handler",
    "OnUpdateData_PR_Handler",
    "OnUpdateData_Y_Handler",
    "OnUpdateData_P_Handler",
    "OnUpdateData_R_Handler",
    "OnUpdateData_XZ_Handler",
    "OnUpdateData_XZ_YPR_Handler",
    "OnUpdateData_XZ_YP_Handler",
    "OnUpdateData_XZ_YR_Handler",
    "OnUpdateData_XZ_PR_Handler",
    "OnUpdateData_XZ_Y_Handler",
    "OnUpdateData_XZ_P_Handler",
    "OnUpdateData_XZ_R_Handler",
    "OnUpdateData_XYZ_Handler",
    "OnUpdateData_XYZ_YPR_Handler",
    "OnUpdateData_XYZ_YP_Handler",
    "OnUpdateData_XYZ_YR_Handler",
    "OnUpdateData_XYZ_PR_Handler",
    "OnUpdateData_XYZ_Y_Handler",
    "OnUpdateData_XYZ_P_Handler",
    "OnUpdateData_XYZ_R_Handler",
    "OnUpdateData_P_OptimizedHandler",
    "OnUpdateData_Y_OptimizedHandler",
    "OnUpdateData_R_OptimizedHandler",
    "OnUpdateData_YP_OptimizedHandler",
    "OnUpdateData_YR_OptimizedHandler",
    "OnUpdateData_PR_OptimizedHandler",
    "OnUpdateData_YPR_OptimizedHandler",
    "OnUpdateData_XZ_OptimizedHandler",
    "OnUpdateData_XZ_YPR_OptimizedHandler",
    "OnUpdateData_XZ_YR_OptimizedHandler",
    "OnUpdateData_XZ_YP_OptimizedHandler",
    "OnUpdateData_XZ_PR_OptimizedHandler",
    "OnUpdateData_XZ_Y_OptimizedHandler",
    "OnUpdateData_XZ_P_OptimizedHandler",
    "OnUpdateData_XZ_R_OptimizedHandler",
    "OnUpdateData_XYZ_OptimizedHandler",
    "OnUpdateData_XYZ_YPR_OptimizedHandler",
    "OnUpdateData_XYZ_YP_OptimizedHandler",
    "OnUpdateData_XYZ_YR_OptimizedHandler",
    "OnUpdateData_XYZ_PR_OptimizedHandler",
    "OnUpdateData_XYZ_Y_OptimizedHandler",
    "OnUpdateData_XYZ_P_OptimizedHandler",
    "OnUpdateData_XYZ_R_OptimizedHandler",
    "OnControlEntityHandler",
]
