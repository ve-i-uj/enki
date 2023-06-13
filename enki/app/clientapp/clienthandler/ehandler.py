"""Entity message handlers."""

import dataclasses
import logging
from dataclasses import dataclass
from typing import ClassVar, Dict, Any, Type

from enki.misc import devonly
from enki.core.enkitype import NoValue
from enki.core import kbetype, kbemath

from enki.core.message import Message
from enki.core.kbetype import Position, Direction
from enki.core import msgspec
from enki.handler.base import Handler, HandlerResult, ParsedMsgData

from ..clienthandler.ehelper import EntityHelper
from ..layer import ilayer
from ..layer.thlayer import IGameLayer


logger = logging.getLogger(__name__)


class _OptimizedXYZReader:
    """

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
        return kbetype.FLOAT.decode(
            memoryview(kbetype.INT32.encode(value))
        )[0]

    @staticmethod
    def float32_to_int32(value: float) -> int:
        return kbetype.INT32.decode(
            memoryview(kbetype.FLOAT.encode(value))
        )[0]

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
        data_ |= (value_1 << 16)
        data_ |= (value_2 << 8)
        data_ |= value_3
        # ... and now there is one 24 bit value. This value contains two float
        # numbers by 12 bit per a value.

        # 0x7ff000 is 0b11111111111000000000000
        # The half of the value is cut off and then left shifts three bits
        x |= (data_ & 0x7ff000) << 3
        z |= (data_ & 0x0007ff) << 15

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
            _OptimizedXYZReader.int32_to_float32(z)
        ), data

    @staticmethod
    def read_packed_y(data: memoryview) -> tuple[float, memoryview]:
        data_, offset = kbetype.UINT16.decode(data)
        data = data[offset:]

        y = 0x40000000
        y |= (data_ & 0x7fff) << 12
        y = _OptimizedXYZReader.float32_to_int32(
            _OptimizedXYZReader.int32_to_float32(y) - 2.0
        )
        y |= (data_ & 0x8000) << 16

        return _OptimizedXYZReader.int32_to_float32(y), data


class _OnEntityCreatedMixin:
    """Действие при создании сущности."""
    _entity_helper: EntityHelper
    _game: IGameLayer

    def on_entity_created(self, entity_id: int, entity_cls_name: str, is_player: bool):
        logger.debug('[%s] %s', self, devonly.func_args_values())
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
class EntityParsedData(ParsedMsgData):
    pass


class EntityHandlerResult(HandlerResult):
    result: EntityParsedData
    msg_id: int = NoValue.NO_ID


class EntityHandler(Handler):

    def __init__(self, entity_helper: EntityHelper):
        self._entity_helper = entity_helper

    @property
    def _game(self) -> IGameLayer:
        return ilayer.get_game_layer()

    def get_entity_id(self, data: memoryview) -> tuple[int, memoryview]:
        entity_id, offset = kbetype.ENTITY_ID.decode(data)
        data = data[offset:]
        return entity_id, data

    def parse_data(self, data: memoryview, entity_id: int) -> tuple[EntityParsedData, memoryview]:
        return EntityParsedData(), data[:]

    def process_parsed_data(self, pd: EntityParsedData, entity_id: int) -> EntityHandlerResult:
        return EntityHandlerResult(False, pd)

    def handle(self, msg: Message) -> EntityHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        data = msg.get_values()[0]
        entity_id, data = self.get_entity_id(data)
        pd, data = self.parse_data(data, entity_id)
        return self.process_parsed_data(pd, entity_id)

    def set_pose(self, entity_id: int, pose_data: PoseData):
        self._game.update_entity_properties(entity_id, {
            'position': pose_data.position,
            'direction': pose_data.direction,
        })

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'


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
class _OnUpdateData_XYZ_YPR_BaseParsedData(EntityParsedData):
    pass


@dataclass
class _OnUpdateData_XYZ_YPR_BaseHandlerResult(EntityHandlerResult):
    result: _OnUpdateData_XYZ_YPR_BaseParsedData
    msg_id: int = NoValue.NO_ID


class _OnUpdateData_XYZ_YPR_BaseHandler(EntityHandler, _OptimizedHandlerMixin):
    _parsed_data_cls: ClassVar[Type[_OnUpdateData_XYZ_YPR_BaseParsedData]]
    _handler_result_cls: ClassVar[Type[_OnUpdateData_XYZ_YPR_BaseHandlerResult]]

    def get_entity_id(self, data: memoryview) -> tuple[int, memoryview]:
        return self.get_optimized_entity_id(data)

    def parse_data(self, data: memoryview, entity_id: int
                   ) -> tuple[_OnUpdateData_XYZ_YPR_BaseParsedData, memoryview]:
        values = []
        for _ in range(len(dataclasses.fields(self._parsed_data_cls))):
            value, offset = kbetype.FLOAT.decode(data)
            data = data[offset:]
            values.append(value)
        pd = self._parsed_data_cls(*values)
        return pd, data

    def process_parsed_data(self, pd: _OnUpdateData_XYZ_YPR_BaseParsedData,
                            entity_id: int) -> _OnUpdateData_XYZ_YPR_BaseHandlerResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f
            in dataclasses.fields(self._parsed_data_cls)
        })
        self.set_pose(entity_id, pose_data)

        return _OnUpdateData_XYZ_YPR_BaseHandlerResult(True, pd)


@dataclass
class OnUpdatePropertysParsedData(ParsedMsgData):
    entity_id: int
    e_properties: Dict[str, Any]
    ec_properties: Dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclass
class OnUpdatePropertysHandlerResult(HandlerResult):
    result: OnUpdatePropertysParsedData
    msg_id: int = msgspec.app.client.onUpdatePropertys.id


class OnUpdatePropertysHandler(EntityHandler):

    def handle(self, msg: Message) -> OnUpdatePropertysHandlerResult:
        """Handler of `onUpdatePropertys`."""
        logger.debug(f'[{self}] ({devonly.func_args_values()})')
        data: memoryview = msg.get_values()[0]
        entity_id, data = self.get_entity_id(data)
        parsed_data = OnUpdatePropertysParsedData(
            entity_id=entity_id,
            e_properties={}
        )

        cls_name = self._entity_helper.get_entity_cls_name_by_eid(entity_id)
        assert cls_name is not None
        desc = self._entity_helper.get_entity_descr_by_cls_name(cls_name)
        while data:
            if self._entity_helper.get_kbenginexml().cellapp.entitydefAliasID \
                    and len(desc.property_desc_by_id) <= 255:
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
            assert prop_id != 0, 'There is NO id of the property'

            type_spec = desc.property_desc_by_id[prop_id]
            value, shift = type_spec.kbetype.decode(data)
            data = data[shift:]

            if type_spec.name in desc.component_names:
                component_name = type_spec.name
                # Это значит, что свойство на самом деле компонент (т.е. отдельный тип)
                ec_data: kbetype.EntityComponentData = value

                comp_desc = self._entity_helper.get_entity_descr_by_uid(value.component_ent_id)
                while ec_data.count > 0:
                    if self._entity_helper.get_kbenginexml().cellapp.entitydefAliasID \
                            and len(comp_desc.property_desc_by_id) <= 255:
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

        return OnUpdatePropertysHandlerResult(
            success=True,
            result=parsed_data
        )


@dataclass
class OnUpdatePropertysOptimizedHandlerResult(OnUpdatePropertysHandlerResult):
    msg_id: int = msgspec.app.client.onUpdatePropertysOptimized.id


class OnUpdatePropertysOptimizedHandler(OnUpdatePropertysHandler,
                                        _OptimizedHandlerMixin):

    def handle(self, msg: Message) -> OnUpdatePropertysHandlerResult:
        res = super().handle(msg)
        return OnUpdatePropertysOptimizedHandlerResult(
            success=True,
            result=res.result
        )


@dataclass
class OnCreatedProxiesParsedData(ParsedMsgData):
    # After each proxy is created, a uuid is generated by the system,
    # which is used for identification when the front-end re-logins
    rnd_uuid: int
    entity_id: int
    cls_name: str  # the class name of the entity


@dataclass
class OnCreatedProxiesHandlerResult(HandlerResult):
    result: OnCreatedProxiesParsedData
    msg_id: int = msgspec.app.client.onCreatedProxies.id


class OnCreatedProxiesHandler(EntityHandler, _OnEntityCreatedMixin):

    def handle(self, msg: Message) -> OnCreatedProxiesHandlerResult:
        pd = OnCreatedProxiesParsedData(*msg.get_values())
        self.on_entity_created(pd.entity_id, pd.cls_name, True)
        self._entity_helper.on_entity_created(pd.entity_id, pd.cls_name, is_player=True)

        return OnCreatedProxiesHandlerResult(
            success=True,
            result=pd
        )


@dataclass
class OnRemoteMethodCallParsedData(ParsedMsgData):
    entity_id: int
    method_name: str
    arguments: list


@dataclass
class OnRemoteMethodCallHandlerResult(HandlerResult):
    result: OnRemoteMethodCallParsedData
    msg_id: int = msgspec.app.client.onRemoteMethodCall.id


class OnRemoteMethodCallHandler(EntityHandler):

    def handle(self, msg: Message) -> OnRemoteMethodCallHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        data: memoryview = msg.get_values()[0]
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
                comp_prop_desc.component_type_name)

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
                entity_id, comp_prop_desc.name, method_desc.name,
                *arguments
            )

        parsed_data = OnRemoteMethodCallParsedData(
            entity_id=entity_id,
            method_name=method_desc.name,
            arguments=arguments
        )
        return OnRemoteMethodCallHandlerResult(
            success=True,
            result=parsed_data
        )


@dataclass
class OnRemoteMethodCallOptimizedParsedData(ParsedMsgData):
    entity_id: int
    method_name: str
    arguments: list


@dataclass
class OnRemoteMethodCallOptimizedHandlerResult(HandlerResult):
    result: OnRemoteMethodCallOptimizedParsedData
    msg_id: int = msgspec.app.client.onRemoteMethodCallOptimized.id


class OnRemoteMethodCallOptimizedHandler(OnRemoteMethodCallHandler, _OptimizedHandlerMixin):

    def handle(self, msg: Message) -> OnRemoteMethodCallOptimizedHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        res = super().handle(msg)
        pd = OnRemoteMethodCallOptimizedParsedData(
            entity_id=res.result.entity_id,
            method_name=res.result.method_name,
            arguments=res.result.arguments,
        )
        return OnRemoteMethodCallOptimizedHandlerResult(res.success, pd, text=res.text)


@dataclass
class OnEntityDestroyedParsedData(ParsedMsgData):
    entity_id: int


@dataclass
class OnEntityDestroyedHandlerResult(HandlerResult):
    result: OnEntityDestroyedParsedData
    msg_id: int = msgspec.app.client.onEntityDestroyed.id


class OnEntityDestroyedHandler(EntityHandler):

    def handle(self, msg: Message) -> OnEntityDestroyedHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        entity_id = msg.get_values()[0]

        desc = self._entity_helper.get_entity_descr_by_eid(entity_id)

        for comp_name in desc.component_names:
            self._game.call_component_method(entity_id, comp_name, 'onDetached')

        self._entity_helper.on_entity_destroyed(entity_id)
        self._game.call_entity_destroyed(entity_id)

        return OnEntityDestroyedHandlerResult(
            success=True,
            result=OnEntityDestroyedParsedData(entity_id)
        )


@dataclass
class OnEntityEnterWorldParsedData(ParsedMsgData):
    entity_id: int = 0
    entity_type_id: int = 0
    is_on_ground: bool = False


@dataclass
class OnEntityEnterWorldHandlerResult(HandlerResult):
    result: OnEntityEnterWorldParsedData
    msg_id: int = msgspec.app.client.onEntityEnterWorld.id


class OnEntityEnterWorldHandler(EntityHandler, _OnEntityCreatedMixin):

    def handle(self, msg: Message) -> OnEntityEnterWorldHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
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

        pd = OnEntityEnterWorldParsedData(entity_id, entity_type_id, is_on_ground)

        desc = self._entity_helper.get_entity_descr_by_uid(entity_type_id)

        if not self._entity_helper.is_player(entity_id):
            # The proxy entity (aka player) is initialized in the onCreatedProxies
            self.on_entity_created(entity_id, desc.name, False)
            self._entity_helper.on_entity_created(pd.entity_id, desc.name, is_player=False)

        self._game.call_entity_method(entity_id, 'onEnterWorld')

        for comp_name in desc.component_names:
            self._game.call_component_method(entity_id, comp_name, 'onEnterWorld')

        self._game.update_entity_properties(entity_id,
                                            {'onGround': pd.is_on_ground})

        return OnEntityEnterWorldHandlerResult(
            success=True,
            result=pd
        )


@dataclass
class OnEntityLeaveWorldParsedData(ParsedMsgData):
    entity_id: int = NoValue.NO_ENTITY_ID


@dataclass
class OnEntityLeaveWorldHandlerResult(HandlerResult):
    result: OnEntityLeaveWorldParsedData
    msg_id: int = msgspec.app.client.onEntityLeaveWorld.id


class OnEntityLeaveWorldHandler(EntityHandler):

    def handle(self, msg: Message) -> OnEntityLeaveWorldHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        data = msg.get_values()[0]
        entity_id, data = self.get_entity_id(data)

        desc = self._entity_helper.get_entity_descr_by_eid(entity_id)
        self._entity_helper.on_entity_leave_world(entity_id)

        self._game.call_entity_method(entity_id, 'onLeaveWorld')
        for comp_name in desc.component_names:
            self._game.call_component_method(entity_id, comp_name, 'onLeaveWorld')

        return OnEntityLeaveWorldHandlerResult(
            success=True,
            result=OnEntityLeaveWorldParsedData(entity_id)
        )


@dataclass
class OnEntityLeaveWorldOptimizedParsedData(ParsedMsgData):
    entity_id: int = NoValue.NO_ENTITY_ID


@dataclass
class OnEntityLeaveWorldOptimizedHandlerResult(HandlerResult):
    result: OnEntityLeaveWorldOptimizedParsedData
    msg_id: int = msgspec.app.client.onEntityLeaveWorldOptimized.id


class OnEntityLeaveWorldOptimizedHandler(OnEntityLeaveWorldHandler, _OptimizedHandlerMixin):

    def get_entity_id(self, data: memoryview) -> tuple[int, memoryview]:
        return self.get_optimized_entity_id(data)

    def handle(self, msg: Message) -> OnEntityLeaveWorldOptimizedHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        res: OnEntityLeaveWorldHandlerResult = super().handle(msg)
        return OnEntityLeaveWorldOptimizedHandlerResult(
            success=res.success,
            result=OnEntityLeaveWorldOptimizedParsedData(res.result.entity_id)
        )


@dataclass
class OnSetEntityPosAndDirParsedData(ParsedMsgData):
    entity_id: int
    position: Position
    direction: Direction


@dataclass
class OnSetEntityPosAndDirHandlerResult(HandlerResult):
    result: OnSetEntityPosAndDirParsedData
    msg_id: int = msgspec.app.client.onSetEntityPosAndDir.id


class OnSetEntityPosAndDirHandler(EntityHandler):

    def handle(self, msg: Message) -> OnSetEntityPosAndDirHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        data: memoryview = msg.get_values()[0]
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

        pd = OnSetEntityPosAndDirParsedData(
            entity_id, position, direction
        )

        pose_data = PoseData()
        pose_data.update_position(position)
        pose_data.update_direction(direction)

        self.set_pose(entity_id, pose_data)

        return OnSetEntityPosAndDirHandlerResult(
            success=True,
            result=pd
        )


@dataclass
class OnEntityEnterSpaceParsedData(ParsedMsgData):
    entity_id: int
    space_id: int
    is_on_ground: bool


@dataclass
class OnEntityEnterSpaceHandlerResult(HandlerResult):
    result: OnEntityEnterSpaceParsedData
    msg_id: int = msgspec.app.client.onEntityEnterSpace.id


class OnEntityEnterSpaceHandler(EntityHandler):

    def handle(self, msg: Message) -> OnEntityEnterSpaceHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        data: memoryview = msg.get_values()[0]
        entity_id, offset = kbetype.ENTITY_ID.decode(data)
        data = data[offset:]

        space_id, offset = kbetype.SPACE_ID.decode(data)
        data = data[offset:]

        is_on_ground = False
        if data:
            is_on_ground, offset = kbetype.BOOL.decode(data)
            data = data[offset:]

        pd = OnEntityEnterSpaceParsedData(entity_id, space_id, is_on_ground)

        desc = self._entity_helper.get_entity_descr_by_eid(entity_id)

        self._game.update_entity_properties(entity_id, {
            'spaceID': pd.space_id,
            'onGround': pd.is_on_ground,
        })
        self._game.call_entity_method(entity_id, 'onEnterSpace')

        for comp_name in desc.component_names:
            self._game.call_component_method(entity_id, comp_name, 'onEnterSpace')

        return OnEntityEnterSpaceHandlerResult(True, pd)


@dataclass
class OnEntityLeaveSpaceParsedData(ParsedMsgData):
    entity_id: int


@dataclass
class OnEntityLeaveSpaceHandlerResult(HandlerResult):
    result: OnEntityLeaveSpaceParsedData
    msg_id: int = msgspec.app.client.onEntityLeaveSpace.id


class OnEntityLeaveSpaceHandler(EntityHandler):

    def handle(self, msg: Message) -> OnEntityLeaveSpaceHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        data: memoryview = msg.get_values()[0]
        entity_id, offset = kbetype.ENTITY_ID.decode(data)
        data = data[offset:]

        pd = OnEntityLeaveSpaceParsedData(entity_id)

        desc = self._entity_helper.get_entity_descr_by_eid(entity_id)
        self._game.call_entity_method(entity_id, 'onLeaveSpace')

        for comp_name in desc.component_names:
            self._game.call_component_method(entity_id, comp_name, 'onLeaveSpace')

        return OnEntityLeaveSpaceHandlerResult(True, pd)


@dataclass
class OnUpdateBasePosParsedData(ParsedMsgData):
    position: Position


@dataclass
class OnUpdateBasePosHandlerResult(HandlerResult):
    result: OnUpdateBasePosParsedData
    msg_id: int = msgspec.app.client.onUpdateBasePos.id


class OnUpdateBasePosHandler(EntityHandler):

    def handle(self, msg: Message) -> OnUpdateBasePosHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        entity_id = self._entity_helper.get_player_id()

        pose_data = PoseData(*msg.get_values())
        self.set_pose(entity_id, pose_data)

        pd = OnUpdateBasePosParsedData(
            pose_data.position
        )
        return OnUpdateBasePosHandlerResult(True, pd)


@dataclass
class OnUpdateBaseDirParsedData(ParsedMsgData):
    direction: Direction


@dataclass
class OnUpdateBaseDirHandlerResult(HandlerResult):
    result: OnUpdateBaseDirParsedData
    msg_id: int = msgspec.app.client.onUpdateBaseDir.id


class OnUpdateBaseDirHandler(EntityHandler):

    def handle(self, msg: Message) -> OnUpdateBaseDirHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        entity_id = self._entity_helper.get_player_id()
        pd: OnUpdateBaseDirParsedData = OnUpdateBaseDirParsedData(
            Direction(*msg.get_values())
        )
        pose_data = PoseData()
        pose_data.update_direction(pd.direction)
        self.set_pose(entity_id, pose_data)
        return OnUpdateBaseDirHandlerResult(True, pd)


@dataclass
class OnUpdateBasePosXZParsedData(ParsedMsgData):
    x: float
    z: float


@dataclass
class OnUpdateBasePosXZHandlerResult(HandlerResult):
    result: OnUpdateBasePosXZParsedData
    msg_id: int = msgspec.app.client.onUpdateBasePosXZ.id


class OnUpdateBasePosXZHandler(EntityHandler):

    def handle(self, msg: Message) -> OnUpdateBasePosXZHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        entity_id = self._entity_helper.get_player_id()
        pd = OnUpdateBasePosXZParsedData(*msg.get_values())

        pose_data = PoseData(x=pd.x, z=pd.z)
        self.set_pose(entity_id, pose_data)

        return OnUpdateBasePosXZHandlerResult(True, pd)


@dataclass
class OnUpdateDataParsedData(ParsedMsgData):
    pass


@dataclass
class OnUpdateDataHandlerResult(HandlerResult):
    result: OnUpdateDataParsedData
    msg_id: int = msgspec.app.client.onUpdateData.id


class OnUpdateDataHandler(EntityHandler, _OptimizedHandlerMixin):

    def handle(self, msg: Message) -> OnUpdateDataHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        res = super().handle(msg)
        return OnUpdateDataHandlerResult(
            res.success, OnUpdateDataParsedData(), text=res.text
        )


@dataclass
class OnUpdateData_XZ_ParsedData(_OnUpdateData_XYZ_YPR_BaseParsedData):
    x: float
    z: float


@dataclass
class OnUpdateData_XZ_HandlerResult(_OnUpdateData_XYZ_YPR_BaseHandlerResult):
    result: OnUpdateData_XZ_ParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xz.id


class OnUpdateData_XZ_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XZ_ParsedData
    _handler_result_cls = OnUpdateData_XZ_HandlerResult


@dataclass
class OnUpdateData_YPR_ParsedData(_OnUpdateData_XYZ_YPR_BaseParsedData):
    yaw: float
    pitch: float
    roll: float


@dataclass
class OnUpdateData_YPR_HandlerResult(_OnUpdateData_XYZ_YPR_BaseHandlerResult):
    result: OnUpdateData_YPR_ParsedData
    msg_id: int = msgspec.app.client.onUpdateData_ypr.id


class OnUpdateData_YPR_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_YPR_ParsedData
    _handler_result_cls = OnUpdateData_YPR_HandlerResult


@dataclass
class OnUpdateData_YP_ParsedData(_OnUpdateData_XYZ_YPR_BaseParsedData):
    yaw: float
    pitch: float


@dataclass
class OnUpdateData_YP_HandlerResult(_OnUpdateData_XYZ_YPR_BaseHandlerResult):
    result: OnUpdateData_YP_ParsedData
    msg_id: int = msgspec.app.client.onUpdateData_yp.id


class OnUpdateData_YP_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_YP_ParsedData
    _handler_result_cls = OnUpdateData_YP_HandlerResult


@dataclass
class OnUpdateData_YR_ParsedData(_OnUpdateData_XYZ_YPR_BaseParsedData):
    yaw: float
    roll: float


@dataclass
class OnUpdateData_YR_HandlerResult(_OnUpdateData_XYZ_YPR_BaseHandlerResult):
    result: OnUpdateData_YR_ParsedData
    msg_id: int = msgspec.app.client.onUpdateData_yr.id


class OnUpdateData_YR_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_YR_ParsedData
    _handler_result_cls = OnUpdateData_YR_HandlerResult


@dataclass
class OnUpdateData_PR_ParsedData(_OnUpdateData_XYZ_YPR_BaseParsedData):
    pitch: float
    roll: float


@dataclass
class OnUpdateData_PR_HandlerResult(_OnUpdateData_XYZ_YPR_BaseHandlerResult):
    result: OnUpdateData_PR_ParsedData
    msg_id: int = msgspec.app.client.onUpdateData_pr.id


class OnUpdateData_PR_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_PR_ParsedData
    _handler_result_cls = OnUpdateData_PR_HandlerResult


@dataclass
class OnUpdateData_Y_ParsedData(_OnUpdateData_XYZ_YPR_BaseParsedData):
    yaw: float


@dataclass
class OnUpdateData_Y_HandlerResult(_OnUpdateData_XYZ_YPR_BaseHandlerResult):
    result: OnUpdateData_Y_ParsedData
    msg_id: int = msgspec.app.client.onUpdateData_y.id


class OnUpdateData_Y_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_Y_ParsedData
    _handler_result_cls = OnUpdateData_Y_HandlerResult


@dataclass
class OnUpdateData_P_ParsedData(_OnUpdateData_XYZ_YPR_BaseParsedData):
    pitch: float


@dataclass
class OnUpdateData_P_HandlerResult(_OnUpdateData_XYZ_YPR_BaseHandlerResult):
    result: OnUpdateData_P_ParsedData
    msg_id: int = msgspec.app.client.onUpdateData_p.id


class OnUpdateData_P_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_P_ParsedData
    _handler_result_cls = OnUpdateData_P_HandlerResult


@dataclass
class OnUpdateData_R_ParsedData(_OnUpdateData_XYZ_YPR_BaseParsedData):
    roll: float


@dataclass
class OnUpdateData_R_HandlerResult(_OnUpdateData_XYZ_YPR_BaseHandlerResult):
    result: OnUpdateData_R_ParsedData
    msg_id: int = msgspec.app.client.onUpdateData_r.id


class OnUpdateData_R_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_R_ParsedData
    _handler_result_cls = OnUpdateData_R_HandlerResult


@dataclass
class OnUpdateData_XZ_YPR_ParsedData(_OnUpdateData_XYZ_YPR_BaseParsedData):
    x: float
    z: float
    yaw: float
    pitch: float
    roll: float


@dataclass
class OnUpdateData_XZ_YPR_HandlerResult(_OnUpdateData_XYZ_YPR_BaseHandlerResult):
    result: OnUpdateData_XZ_YPR_ParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xz_ypr.id


class OnUpdateData_XZ_YPR_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XZ_YPR_ParsedData
    _handler_result_cls = OnUpdateData_XZ_YPR_HandlerResult


@dataclass
class OnUpdateData_XZ_YP_ParsedData(_OnUpdateData_XYZ_YPR_BaseParsedData):
    x: float
    z: float
    yaw: float
    pitch: float


@dataclass
class OnUpdateData_XZ_YP_HandlerResult(_OnUpdateData_XYZ_YPR_BaseHandlerResult):
    result: OnUpdateData_XZ_YP_ParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xz_yp.id


class OnUpdateData_XZ_YP_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XZ_YP_ParsedData
    _handler_result_cls = OnUpdateData_XZ_YP_HandlerResult


@dataclass
class OnUpdateData_XZ_YR_ParsedData(_OnUpdateData_XYZ_YPR_BaseParsedData):
    x: float
    z: float
    yaw: float
    roll: float


@dataclass
class OnUpdateData_XZ_YR_HandlerResult(_OnUpdateData_XYZ_YPR_BaseHandlerResult):
    result: OnUpdateData_XZ_YR_ParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xz_yr.id


class OnUpdateData_XZ_YR_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XZ_YR_ParsedData
    _handler_result_cls = OnUpdateData_XZ_YR_HandlerResult


@dataclass
class OnUpdateData_XZ_PR_ParsedData(_OnUpdateData_XYZ_YPR_BaseParsedData):
    x: float
    z: float
    yaw: float
    pitch: float
    roll: float


@dataclass
class OnUpdateData_XZ_PR_HandlerResult(_OnUpdateData_XYZ_YPR_BaseHandlerResult):
    result: OnUpdateData_XZ_PR_ParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xz_pr.id


class OnUpdateData_XZ_PR_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XZ_PR_ParsedData
    _handler_result_cls = OnUpdateData_XZ_PR_HandlerResult


@dataclass
class OnUpdateData_XZ_Y_ParsedData(_OnUpdateData_XYZ_YPR_BaseParsedData):
    x: float
    z: float
    yaw: float


@dataclass
class OnUpdateData_XZ_Y_HandlerResult(_OnUpdateData_XYZ_YPR_BaseHandlerResult):
    result: OnUpdateData_XZ_Y_ParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xz_y.id


class OnUpdateData_XZ_Y_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XZ_Y_ParsedData
    _handler_result_cls = OnUpdateData_XZ_Y_HandlerResult


@dataclass
class OnUpdateData_XZ_P_ParsedData(_OnUpdateData_XYZ_YPR_BaseParsedData):
    x: float
    z: float
    pitch: float


@dataclass
class OnUpdateData_XZ_P_HandlerResult(_OnUpdateData_XYZ_YPR_BaseHandlerResult):
    result: OnUpdateData_XZ_P_ParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xz_p.id


class OnUpdateData_XZ_P_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XZ_P_ParsedData
    _handler_result_cls = OnUpdateData_XZ_P_HandlerResult


@dataclass
class OnUpdateData_XZ_R_ParsedData(_OnUpdateData_XYZ_YPR_BaseParsedData):
    x: float
    z: float
    roll: float


@dataclass
class OnUpdateData_XZ_R_HandlerResult(_OnUpdateData_XYZ_YPR_BaseHandlerResult):
    result: OnUpdateData_XZ_R_ParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xz_r.id


class OnUpdateData_XZ_R_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XZ_R_ParsedData
    _handler_result_cls = OnUpdateData_XZ_R_HandlerResult


@dataclass
class OnUpdateData_XYZ_ParsedData(_OnUpdateData_XYZ_YPR_BaseParsedData):
    x: float
    z: float
    y: float


@dataclass
class OnUpdateData_XYZ_HandlerResult(_OnUpdateData_XYZ_YPR_BaseHandlerResult):
    result: OnUpdateData_XYZ_ParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xyz.id


class OnUpdateData_XYZ_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XYZ_ParsedData
    _handler_result_cls = OnUpdateData_XYZ_HandlerResult


@dataclass
class OnUpdateData_XYZ_YPR_ParsedData(_OnUpdateData_XYZ_YPR_BaseParsedData):
    x: float
    z: float
    y: float
    yaw: float
    pitch: float
    roll: float


@dataclass
class OnUpdateData_XYZ_YPR_HandlerResult(_OnUpdateData_XYZ_YPR_BaseHandlerResult):
    result: OnUpdateData_XYZ_YPR_ParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xyz_ypr.id


class OnUpdateData_XYZ_YPR_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XYZ_YPR_ParsedData
    _handler_result_cls = OnUpdateData_XYZ_YPR_HandlerResult


@dataclass
class OnUpdateData_XYZ_YP_ParsedData(_OnUpdateData_XYZ_YPR_BaseParsedData):
    x: float
    z: float
    y: float
    yaw: float
    pitch: float


@dataclass
class OnUpdateData_XYZ_YP_HandlerResult(_OnUpdateData_XYZ_YPR_BaseHandlerResult):
    result: OnUpdateData_XYZ_YP_ParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xyz_yp.id


class OnUpdateData_XYZ_YP_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XYZ_YP_ParsedData
    _handler_result_cls = OnUpdateData_XYZ_YP_HandlerResult


@dataclass
class OnUpdateData_XYZ_YR_ParsedData(_OnUpdateData_XYZ_YPR_BaseParsedData):
    x: float
    z: float
    y: float
    yaw: float
    pitch: float


@dataclass
class OnUpdateData_XYZ_YR_HandlerResult(_OnUpdateData_XYZ_YPR_BaseHandlerResult):
    result: OnUpdateData_XYZ_YR_ParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xyz_yr.id


class OnUpdateData_XYZ_YR_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XYZ_YR_ParsedData
    _handler_result_cls = OnUpdateData_XYZ_YR_HandlerResult


@dataclass
class OnUpdateData_XYZ_PR_ParsedData(_OnUpdateData_XYZ_YPR_BaseParsedData):
    x: float
    z: float
    y: float
    pitch: float
    roll: float


@dataclass
class OnUpdateData_XYZ_PR_HandlerResult(_OnUpdateData_XYZ_YPR_BaseHandlerResult):
    result: OnUpdateData_XYZ_PR_ParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xyz_pr.id


class OnUpdateData_XYZ_PR_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XYZ_PR_ParsedData
    _handler_result_cls = OnUpdateData_XYZ_PR_HandlerResult


@dataclass
class OnUpdateData_XYZ_Y_ParsedData(_OnUpdateData_XYZ_YPR_BaseParsedData):
    x: float
    z: float
    y: float
    yaw: float


@dataclass
class OnUpdateData_XYZ_Y_HandlerResult(_OnUpdateData_XYZ_YPR_BaseHandlerResult):
    result: OnUpdateData_XYZ_Y_ParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xyz_y.id


class OnUpdateData_XYZ_Y_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XYZ_Y_ParsedData
    _handler_result_cls = OnUpdateData_XYZ_Y_HandlerResult


@dataclass
class OnUpdateData_XYZ_P_ParsedData(_OnUpdateData_XYZ_YPR_BaseParsedData):
    x: float
    z: float
    y: float
    pitch: float


@dataclass
class OnUpdateData_XYZ_P_HandlerResult(_OnUpdateData_XYZ_YPR_BaseHandlerResult):
    result: OnUpdateData_XYZ_P_ParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xyz_p.id


class OnUpdateData_XYZ_P_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XYZ_P_ParsedData
    _handler_result_cls = OnUpdateData_XYZ_P_HandlerResult


@dataclass
class OnUpdateData_XYZ_R_ParsedData(_OnUpdateData_XYZ_YPR_BaseParsedData):
    x: float
    z: float
    y: float
    pitch: float


@dataclass
class OnUpdateData_XYZ_R_HandlerResult(_OnUpdateData_XYZ_YPR_BaseHandlerResult):
    result: OnUpdateData_XYZ_R_ParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xyz_r.id


class OnUpdateData_XYZ_R_Handler(_OnUpdateData_XYZ_YPR_BaseHandler):
    _parsed_data_cls = OnUpdateData_XYZ_R_ParsedData
    _handler_result_cls = OnUpdateData_XYZ_R_HandlerResult


@dataclass
class OnUpdateData_Y_OptimizedParsedData(EntityParsedData):
    yaw: float


@dataclass
class OnUpdateData_Y_OptimizedHandlerResult(EntityHandlerResult):
    result: OnUpdateData_Y_OptimizedParsedData
    msg_id: int = msgspec.app.client.onUpdateData_y_optimized.id


class OnUpdateData_Y_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):

    def parse_data(self, data: memoryview, entity_id: int
                   ) -> tuple[OnUpdateData_Y_OptimizedParsedData, memoryview]:
        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle = kbemath.int82angle(value)
        pd = OnUpdateData_Y_OptimizedParsedData(angle)
        return pd, data

    def process_parsed_data(self, pd: OnUpdateData_Y_OptimizedParsedData,
                            entity_id: int) -> OnUpdateData_Y_OptimizedHandlerResult:
        pose_data = PoseData(**{
            'yaw': pd.yaw,
        })
        self.set_pose(entity_id, pose_data)

        return OnUpdateData_Y_OptimizedHandlerResult(True, pd)


@dataclass
class OnUpdateData_R_OptimizedParsedData(EntityParsedData):
    roll: float


@dataclass
class OnUpdateData_R_OptimizedHandlerResult(EntityHandlerResult):
    result: OnUpdateData_R_OptimizedParsedData
    msg_id: int = msgspec.app.client.onUpdateData_r_optimized.id


class OnUpdateData_R_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):

    def parse_data(self, data: memoryview, entity_id: int
                   ) -> tuple[OnUpdateData_R_OptimizedParsedData, memoryview]:
        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle = kbemath.int82angle(value)
        pd = OnUpdateData_R_OptimizedParsedData(angle)
        return pd, data

    def process_parsed_data(self, pd: OnUpdateData_R_OptimizedParsedData,
                            entity_id: int) -> OnUpdateData_R_OptimizedHandlerResult:
        pose_data = PoseData(**{
            'roll': pd.roll,
        })
        self.set_pose(entity_id, pose_data)

        return OnUpdateData_R_OptimizedHandlerResult(True, pd)


@dataclass
class OnUpdateData_P_OptimizedParsedData(EntityParsedData):
    pitch: float


@dataclass
class OnUpdateData_P_OptimizedHandlerResult(EntityHandlerResult):
    result: OnUpdateData_P_OptimizedParsedData
    msg_id: int = msgspec.app.client.onUpdateData_p_optimized.id


class OnUpdateData_P_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):

    def parse_data(self, data: memoryview, entity_id: int
                   ) -> tuple[OnUpdateData_P_OptimizedParsedData, memoryview]:
        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle = kbemath.int82angle(value)
        pd = OnUpdateData_P_OptimizedParsedData(angle)
        return pd, data

    def process_parsed_data(self, pd: OnUpdateData_P_OptimizedParsedData,
                            entity_id: int) -> OnUpdateData_P_OptimizedHandlerResult:
        pose_data = PoseData(**{
            'pitch': pd.pitch,
        })
        self.set_pose(entity_id, pose_data)

        return OnUpdateData_P_OptimizedHandlerResult(True, pd)


@dataclass
class OnUpdateData_YP_OptimizedParsedData(EntityParsedData):
    yaw: float
    pitch: float


@dataclass
class OnUpdateData_YP_OptimizedHandlerResult(EntityHandlerResult):
    result: OnUpdateData_YP_OptimizedParsedData
    msg_id: int = msgspec.app.client.onUpdateData_yp_optimized.id


class OnUpdateData_YP_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):

    def parse_data(self, data: memoryview, entity_id: int
                   ) -> tuple[OnUpdateData_YP_OptimizedParsedData, memoryview]:
        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)
        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_2 = kbemath.int82angle(value)
        pd = OnUpdateData_YP_OptimizedParsedData(angle_1, angle_2)
        return pd, data

    def process_parsed_data(self, pd: OnUpdateData_YP_OptimizedParsedData,
                            entity_id: int) -> OnUpdateData_YP_OptimizedHandlerResult:
        pose_data = PoseData(**{
            'yaw': pd.yaw,
            'pitch': pd.pitch,
        })
        self.set_pose(entity_id, pose_data)

        return OnUpdateData_YP_OptimizedHandlerResult(True, pd)


@dataclass
class OnUpdateData_YR_OptimizedParsedData(EntityParsedData):
    yaw: float
    roll: float


@dataclass
class OnUpdateData_YR_OptimizedHandlerResult(EntityHandlerResult):
    result: OnUpdateData_YR_OptimizedParsedData
    msg_id: int = msgspec.app.client.onUpdateData_yr_optimized.id


class OnUpdateData_YR_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):

    def parse_data(self, data: memoryview, entity_id: int
                   ) -> tuple[OnUpdateData_YR_OptimizedParsedData, memoryview]:
        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)
        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_2 = kbemath.int82angle(value)
        pd = OnUpdateData_YR_OptimizedParsedData(angle_1, angle_2)
        return pd, data

    def process_parsed_data(self, pd: OnUpdateData_YR_OptimizedParsedData,
                            entity_id: int) -> OnUpdateData_YR_OptimizedHandlerResult:
        pose_data = PoseData(**{
            'yaw': pd.yaw,
            'roll': pd.roll,
        })
        self.set_pose(entity_id, pose_data)

        return OnUpdateData_YR_OptimizedHandlerResult(True, pd)


@dataclass
class OnUpdateData_PR_OptimizedParsedData(EntityParsedData):
    pitch: float
    roll: float


@dataclass
class OnUpdateData_PR_OptimizedHandlerResult(EntityHandlerResult):
    result: OnUpdateData_PR_OptimizedParsedData
    msg_id: int = msgspec.app.client.onUpdateData_pr_optimized.id


class OnUpdateData_PR_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):

    def parse_data(self, data: memoryview, entity_id: int
                   ) -> tuple[OnUpdateData_PR_OptimizedParsedData, memoryview]:
        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_2 = kbemath.int82angle(value)

        pd = OnUpdateData_PR_OptimizedParsedData(angle_1, angle_2)
        return pd, data

    def process_parsed_data(self, pd: OnUpdateData_PR_OptimizedParsedData,
                            entity_id: int) -> OnUpdateData_PR_OptimizedHandlerResult:
        pose_data = PoseData(**{
            'pitch': pd.pitch,
            'roll': pd.roll,
        })
        self.set_pose(entity_id, pose_data)

        return OnUpdateData_PR_OptimizedHandlerResult(True, pd)


@dataclass
class OnUpdateData_YPR_OptimizedParsedData(EntityParsedData):
    yaw: float
    pitch: float
    roll: float


@dataclass
class OnUpdateData_YPR_OptimizedHandlerResult(EntityHandlerResult):
    result: OnUpdateData_YPR_OptimizedParsedData
    msg_id: int = msgspec.app.client.onUpdateData_ypr_optimized.id


class OnUpdateData_YPR_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):

    def parse_data(self, data: memoryview, entity_id: int
                   ) -> tuple[OnUpdateData_YPR_OptimizedParsedData, memoryview]:
        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_2 = kbemath.int82angle(value)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_3 = kbemath.int82angle(value)

        pd = OnUpdateData_YPR_OptimizedParsedData(angle_1, angle_2, angle_3)
        return pd, data

    def process_parsed_data(self, pd: OnUpdateData_YPR_OptimizedParsedData,
                            entity_id: int) -> OnUpdateData_YPR_OptimizedHandlerResult:
        pose_data = PoseData(**{
            'yaw': pd.yaw,
            'pitch': pd.pitch,
            'roll': pd.roll,
        })
        self.set_pose(entity_id, pose_data)

        return OnUpdateData_YPR_OptimizedHandlerResult(True, pd)


@dataclass
class OnUpdateData_XZ_OptimizedParsedData(EntityParsedData):
    x: float
    z: float


@dataclass
class OnUpdateData_XZ_OptimizedHandlerResult(EntityHandlerResult):
    result: OnUpdateData_XZ_OptimizedParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xz_optimized.id


class OnUpdateData_XZ_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):

    def parse_data(self, data: memoryview, entity_id: int
                   ) -> tuple[OnUpdateData_XZ_OptimizedParsedData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)
        pd = OnUpdateData_XZ_OptimizedParsedData(v2.x, v2.y)
        return pd, data

    def process_parsed_data(self, pd: OnUpdateData_XZ_OptimizedParsedData,
                            entity_id: int) -> OnUpdateData_XZ_OptimizedHandlerResult:
        pose_data = PoseData(**{
            'x': pd.x,
            'z': pd.z,
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XZ_OptimizedHandlerResult(True, pd)


@dataclass
class OnUpdateData_XZ_YPR_OptimizedParsedData(EntityParsedData):
    x: float
    z: float
    yaw: float
    pitch: float
    roll: float


@dataclass
class OnUpdateData_XZ_YPR_OptimizedHandlerResult(EntityHandlerResult):
    result: OnUpdateData_XZ_YPR_OptimizedParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xz_ypr_optimized.id


class OnUpdateData_XZ_YPR_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):

    def parse_data(self, data: memoryview, entity_id: int
                   ) -> tuple[OnUpdateData_XZ_YPR_OptimizedParsedData, memoryview]:
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

        pd = OnUpdateData_XZ_YPR_OptimizedParsedData(
            v2.x, v2.y, yaw, pitch, roll
        )
        return pd, data

    def process_parsed_data(self, pd: OnUpdateData_XZ_YPR_OptimizedParsedData,
                            entity_id: int) -> OnUpdateData_XZ_YPR_OptimizedHandlerResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XZ_YPR_OptimizedHandlerResult(True, pd)


@dataclass
class OnUpdateData_XZ_YP_OptimizedParsedData(EntityParsedData):
    x: float
    z: float
    yaw: float
    pitch: float


@dataclass
class OnUpdateData_XZ_YP_OptimizedHandlerResult(EntityHandlerResult):
    result: OnUpdateData_XZ_YP_OptimizedParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xz_yp_optimized.id


class OnUpdateData_XZ_YP_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):

    def parse_data(self, data: memoryview, entity_id: int
                   ) -> tuple[OnUpdateData_XZ_YP_OptimizedParsedData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        yaw = kbemath.int82angle(value)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        pitch = kbemath.int82angle(value)

        pd = OnUpdateData_XZ_YP_OptimizedParsedData(
            v2.x, v2.y, yaw, pitch
        )
        return pd, data

    def process_parsed_data(self, pd: OnUpdateData_XZ_YP_OptimizedParsedData,
                            entity_id: int) -> OnUpdateData_XZ_YP_OptimizedHandlerResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XZ_YP_OptimizedHandlerResult(True, pd)


@dataclass
class OnUpdateData_XZ_YR_OptimizedParsedData(EntityParsedData):
    x: float
    z: float
    yaw: float
    roll: float


@dataclass
class OnUpdateData_XZ_YR_OptimizedHandlerResult(EntityHandlerResult):
    result: OnUpdateData_XZ_YR_OptimizedParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xz_yr_optimized.id


class OnUpdateData_XZ_YR_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):

    def parse_data(self, data: memoryview, entity_id: int
                   ) -> tuple[OnUpdateData_XZ_YR_OptimizedParsedData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        yaw = kbemath.int82angle(value)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        roll = kbemath.int82angle(value)

        pd = OnUpdateData_XZ_YR_OptimizedParsedData(
            v2.x, v2.y, yaw, roll
        )
        return pd, data

    def process_parsed_data(self, pd: OnUpdateData_XZ_YR_OptimizedParsedData,
                            entity_id: int) -> OnUpdateData_XZ_YR_OptimizedHandlerResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XZ_YR_OptimizedHandlerResult(True, pd)


@dataclass
class OnUpdateData_XZ_PR_OptimizedParsedData(EntityParsedData):
    x: float
    z: float
    pitch: float
    roll: float


@dataclass
class OnUpdateData_XZ_PR_OptimizedHandlerResult(EntityHandlerResult):
    result: OnUpdateData_XZ_PR_OptimizedParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xz_pr_optimized.id


class OnUpdateData_XZ_PR_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):

    def parse_data(self, data: memoryview, entity_id: int
                   ) -> tuple[OnUpdateData_XZ_PR_OptimizedParsedData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        pitch = kbemath.int82angle(value)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        roll = kbemath.int82angle(value)

        pd = OnUpdateData_XZ_PR_OptimizedParsedData(
            v2.x, v2.y, pitch, roll
        )
        return pd, data

    def process_parsed_data(self, pd: OnUpdateData_XZ_PR_OptimizedParsedData,
                            entity_id: int) -> OnUpdateData_XZ_PR_OptimizedHandlerResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XZ_PR_OptimizedHandlerResult(True, pd)


@dataclass
class OnUpdateData_XZ_Y_OptimizedParsedData(EntityParsedData):
    x: float
    z: float
    yaw: float


@dataclass
class OnUpdateData_XZ_Y_OptimizedHandlerResult(EntityHandlerResult):
    result: OnUpdateData_XZ_Y_OptimizedParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xz_y_optimized.id


class OnUpdateData_XZ_Y_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):

    def parse_data(self, data: memoryview, entity_id: int
                   ) -> tuple[OnUpdateData_XZ_Y_OptimizedParsedData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        yaw = kbemath.int82angle(value)

        pd = OnUpdateData_XZ_Y_OptimizedParsedData(
            v2.x, v2.y, yaw
        )
        return pd, data

    def process_parsed_data(self, pd: OnUpdateData_XZ_Y_OptimizedParsedData,
                            entity_id: int) -> OnUpdateData_XZ_Y_OptimizedHandlerResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XZ_Y_OptimizedHandlerResult(True, pd)


@dataclass
class OnUpdateData_XZ_P_OptimizedParsedData(EntityParsedData):
    x: float
    z: float
    pitch: float


@dataclass
class OnUpdateData_XZ_P_OptimizedHandlerResult(EntityHandlerResult):
    result: OnUpdateData_XZ_P_OptimizedParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xz_p_optimized.id


class OnUpdateData_XZ_P_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):

    def parse_data(self, data: memoryview, entity_id: int
                   ) -> tuple[OnUpdateData_XZ_P_OptimizedParsedData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        pitch = kbemath.int82angle(value)

        pd = OnUpdateData_XZ_P_OptimizedParsedData(
            v2.x, v2.y, pitch
        )
        return pd, data

    def process_parsed_data(self, pd: OnUpdateData_XZ_P_OptimizedParsedData,
                            entity_id: int) -> OnUpdateData_XZ_P_OptimizedHandlerResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XZ_P_OptimizedHandlerResult(True, pd)


@dataclass
class OnUpdateData_XZ_R_OptimizedParsedData(EntityParsedData):
    x: float
    z: float
    roll: float


@dataclass
class OnUpdateData_XZ_R_OptimizedHandlerResult(EntityHandlerResult):
    result: OnUpdateData_XZ_R_OptimizedParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xz_r_optimized.id


class OnUpdateData_XZ_R_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):

    def parse_data(self, data: memoryview, entity_id: int
                   ) -> tuple[OnUpdateData_XZ_R_OptimizedParsedData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        roll = kbemath.int82angle(value)

        pd: OnUpdateData_XZ_R_OptimizedParsedData = OnUpdateData_XZ_R_OptimizedParsedData(
            v2.x, v2.y, roll
        )
        return pd, data

    def process_parsed_data(self, pd: OnUpdateData_XZ_R_OptimizedParsedData,
                            entity_id: int) -> OnUpdateData_XZ_R_OptimizedHandlerResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XZ_R_OptimizedHandlerResult(True, pd)


@dataclass
class OnUpdateData_XYZ_OptimizedParsedData(EntityParsedData):
    x: float
    y: float
    z: float


@dataclass
class OnUpdateData_XYZ_OptimizedHandlerResult(EntityHandlerResult):
    result: OnUpdateData_XYZ_OptimizedParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xyz_optimized.id


class OnUpdateData_XYZ_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):

    def parse_data(self, data: memoryview, entity_id: int
                   ) -> tuple[OnUpdateData_XYZ_OptimizedParsedData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)
        y, data = _OptimizedXYZReader.read_packed_y(data)
        pd = OnUpdateData_XYZ_OptimizedParsedData(v2.x, y, v2.y)
        return pd, data

    def process_parsed_data(self, pd: OnUpdateData_XYZ_OptimizedParsedData,
                            entity_id: int) -> OnUpdateData_XYZ_OptimizedHandlerResult:
        pose_data = PoseData(**{
            'x': pd.x,
            'y': pd.y,
            'z': pd.z,
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XYZ_OptimizedHandlerResult(True, pd)


@dataclass
class OnUpdateData_XYZ_YPR_OptimizedParsedData(EntityParsedData):
    x: float
    y: float
    z: float
    yaw: float
    pitch: float
    roll: float


@dataclass
class OnUpdateData_XYZ_YPR_OptimizedHandlerResult(EntityHandlerResult):
    result: OnUpdateData_XYZ_YPR_OptimizedParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xyz_ypr_optimized.id


class OnUpdateData_XYZ_YPR_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):

    def parse_data(self, data: memoryview, entity_id: int
                   ) -> tuple[OnUpdateData_XYZ_YPR_OptimizedParsedData, memoryview]:
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

        pd = OnUpdateData_XYZ_YPR_OptimizedParsedData(
            v2.x, y, v2.y, angle_1, angle_2, angle_3
        )
        return pd, data

    def process_parsed_data(self, pd: OnUpdateData_XYZ_YPR_OptimizedParsedData,
                            entity_id: int) -> OnUpdateData_XYZ_YPR_OptimizedHandlerResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XYZ_YPR_OptimizedHandlerResult(True, pd)


@dataclass
class OnUpdateData_XYZ_YP_OptimizedParsedData(EntityParsedData):
    x: float
    y: float
    z: float
    yaw: float
    pitch: float


@dataclass
class OnUpdateData_XYZ_YP_OptimizedHandlerResult(EntityHandlerResult):
    result: OnUpdateData_XYZ_YP_OptimizedParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xyz_yp_optimized.id


class OnUpdateData_XYZ_YP_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):

    def parse_data(self, data: memoryview, entity_id: int
                   ) -> tuple[OnUpdateData_XYZ_YP_OptimizedParsedData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)
        y, data = _OptimizedXYZReader.read_packed_y(data)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_2 = kbemath.int82angle(value)

        pd = OnUpdateData_XYZ_YP_OptimizedParsedData(
            v2.x, y, v2.y, angle_1, angle_2
        )
        return pd, data

    def process_parsed_data(self, pd: OnUpdateData_XYZ_YP_OptimizedParsedData,
                            entity_id: int) -> OnUpdateData_XYZ_YP_OptimizedHandlerResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XYZ_YP_OptimizedHandlerResult(True, pd)


@dataclass
class OnUpdateData_XYZ_YR_OptimizedParsedData(EntityParsedData):
    x: float
    y: float
    z: float
    yaw: float
    roll: float


@dataclass
class OnUpdateData_XYZ_YR_OptimizedHandlerResult(EntityHandlerResult):
    result: OnUpdateData_XYZ_YR_OptimizedParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xyz_yr_optimized.id


class OnUpdateData_XYZ_YR_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):

    def parse_data(self, data: memoryview, entity_id: int
                   ) -> tuple[OnUpdateData_XYZ_YR_OptimizedParsedData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)
        y, data = _OptimizedXYZReader.read_packed_y(data)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_2 = kbemath.int82angle(value)

        pd = OnUpdateData_XYZ_YR_OptimizedParsedData(
            v2.x, y, v2.y, angle_1, angle_2
        )
        return pd, data

    def process_parsed_data(self, pd: OnUpdateData_XYZ_YR_OptimizedParsedData,
                            entity_id: int) -> OnUpdateData_XYZ_YR_OptimizedHandlerResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XYZ_YR_OptimizedHandlerResult(True, pd)


@dataclass
class OnUpdateData_XYZ_PR_OptimizedParsedData(EntityParsedData):
    x: float
    y: float
    z: float
    pitch: float
    roll: float


@dataclass
class OnUpdateData_XYZ_PR_OptimizedHandlerResult(EntityHandlerResult):
    result: OnUpdateData_XYZ_PR_OptimizedParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xyz_pr_optimized.id


class OnUpdateData_XYZ_PR_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):

    def parse_data(self, data: memoryview, entity_id: int
                   ) -> tuple[OnUpdateData_XYZ_PR_OptimizedParsedData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)
        y, data = _OptimizedXYZReader.read_packed_y(data)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_2 = kbemath.int82angle(value)

        pd = OnUpdateData_XYZ_PR_OptimizedParsedData(
            v2.x, y, v2.y, angle_1, angle_2
        )
        return pd, data

    def process_parsed_data(self, pd: OnUpdateData_XYZ_PR_OptimizedParsedData,
                            entity_id: int) -> OnUpdateData_XYZ_PR_OptimizedHandlerResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XYZ_PR_OptimizedHandlerResult(True, pd)


@dataclass
class OnUpdateData_XYZ_Y_OptimizedParsedData(EntityParsedData):
    x: float
    y: float
    z: float
    yaw: float


@dataclass
class OnUpdateData_XYZ_Y_OptimizedHandlerResult(EntityHandlerResult):
    result: OnUpdateData_XYZ_Y_OptimizedParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xyz_y_optimized.id


class OnUpdateData_XYZ_Y_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):

    def parse_data(self, data: memoryview, entity_id: int
                   ) -> tuple[OnUpdateData_XYZ_Y_OptimizedParsedData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)
        y, data = _OptimizedXYZReader.read_packed_y(data)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)

        pd = OnUpdateData_XYZ_Y_OptimizedParsedData(
            v2.x, y, v2.y, angle_1
        )
        return pd, data

    def process_parsed_data(self, pd: OnUpdateData_XYZ_Y_OptimizedParsedData,
                            entity_id: int) -> OnUpdateData_XYZ_Y_OptimizedHandlerResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XYZ_Y_OptimizedHandlerResult(True, pd)


@dataclass
class OnUpdateData_XYZ_P_OptimizedParsedData(EntityParsedData):
    x: float
    y: float
    z: float
    pitch: float


@dataclass
class OnUpdateData_XYZ_P_OptimizedHandlerResult(EntityHandlerResult):
    result: OnUpdateData_XYZ_P_OptimizedParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xyz_p_optimized.id


class OnUpdateData_XYZ_P_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):

    def parse_data(self, data: memoryview, entity_id: int
                   ) -> tuple[OnUpdateData_XYZ_P_OptimizedParsedData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)
        y, data = _OptimizedXYZReader.read_packed_y(data)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)

        pd = OnUpdateData_XYZ_P_OptimizedParsedData(
            v2.x, y, v2.y, angle_1
        )
        return pd, data

    def process_parsed_data(self, pd: OnUpdateData_XYZ_P_OptimizedParsedData,
                            entity_id: int) -> OnUpdateData_XYZ_P_OptimizedHandlerResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XYZ_P_OptimizedHandlerResult(True, pd)


@dataclass
class OnUpdateData_XYZ_R_OptimizedParsedData(EntityParsedData):
    x: float
    y: float
    z: float
    roll: float


@dataclass
class OnUpdateData_XYZ_R_OptimizedHandlerResult(EntityHandlerResult):
    result: OnUpdateData_XYZ_R_OptimizedParsedData
    msg_id: int = msgspec.app.client.onUpdateData_xyz_r_optimized.id


class OnUpdateData_XYZ_R_OptimizedHandler(EntityHandler, _OptimizedHandlerMixin):

    def parse_data(self, data: memoryview, entity_id: int
                   ) -> tuple[OnUpdateData_XYZ_R_OptimizedParsedData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)
        y, data = _OptimizedXYZReader.read_packed_y(data)

        value, offset = kbetype.INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)

        pd = OnUpdateData_XYZ_R_OptimizedParsedData(
            v2.x, y, v2.y, angle_1
        )
        return pd, data

    def process_parsed_data(self, pd: OnUpdateData_XYZ_R_OptimizedParsedData,
                            entity_id: int) -> OnUpdateData_XYZ_R_OptimizedHandlerResult:
        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)
        })
        self.set_pose(entity_id, pose_data)
        return OnUpdateData_XYZ_R_OptimizedHandlerResult(True, pd)


@dataclass
class OnControlEntityParsedData(EntityParsedData):
    is_controlled: bool


@dataclass
class OnControlEntityHandlerResult(HandlerResult):
    success: bool
    result: OnControlEntityParsedData
    msg_id: int = msgspec.app.client.onControlEntity.id
    text: str = ''


class OnControlEntityHandler(EntityHandler):

    def handle(self, msg: Message) -> OnControlEntityHandlerResult:
        data: memoryview = msg.get_values()[0]
        entity_id, data = self.get_entity_id(data)
        is_controlled, offset = kbetype.BOOL.decode(data)
        data = data[offset:]
        # TODO: [2022-09-07 13:44 burov_alexey@mail.ru]:
        # I cannot find the server code that sends the "onControlEntity" message.
        # I think it's legacy code thats why I do nothin in this handler.
        return OnControlEntityHandlerResult(
            True, OnControlEntityParsedData(is_controlled)
        )


__all__ = [
    'EntityHandler',

    'OnCreatedProxiesHandler',
    'OnEntityDestroyedHandler',
    'OnEntityEnterWorldHandler',
    'OnEntityLeaveWorldHandler',
    'OnEntityEnterSpaceHandler',
    'OnEntityLeaveSpaceHandler',
    'OnEntityLeaveWorldOptimizedHandler',

    'OnSetEntityPosAndDirHandler',

    'OnUpdatePropertysHandler',
    'OnUpdatePropertysOptimizedHandler',

    'OnRemoteMethodCallHandler',
    'OnRemoteMethodCallOptimizedHandler',

    'OnUpdateBasePosHandler',
    'OnUpdateBaseDirHandler',
    'OnUpdateBasePosXZHandler',

    'OnUpdateDataHandler',

    'OnUpdateData_YPR_Handler',
    'OnUpdateData_YP_Handler',
    'OnUpdateData_YR_Handler',
    'OnUpdateData_PR_Handler',
    'OnUpdateData_Y_Handler',
    'OnUpdateData_P_Handler',
    'OnUpdateData_R_Handler',

    'OnUpdateData_XZ_Handler',
    'OnUpdateData_XZ_YPR_Handler',
    'OnUpdateData_XZ_YP_Handler',
    'OnUpdateData_XZ_YR_Handler',
    'OnUpdateData_XZ_PR_Handler',
    'OnUpdateData_XZ_Y_Handler',
    'OnUpdateData_XZ_P_Handler',
    'OnUpdateData_XZ_R_Handler',

    'OnUpdateData_XYZ_Handler',
    'OnUpdateData_XYZ_YPR_Handler',
    'OnUpdateData_XYZ_YP_Handler',
    'OnUpdateData_XYZ_YR_Handler',
    'OnUpdateData_XYZ_PR_Handler',
    'OnUpdateData_XYZ_Y_Handler',
    'OnUpdateData_XYZ_P_Handler',
    'OnUpdateData_XYZ_R_Handler',

    'OnUpdateData_P_OptimizedHandler',
    'OnUpdateData_Y_OptimizedHandler',
    'OnUpdateData_R_OptimizedHandler',
    'OnUpdateData_YP_OptimizedHandler',
    'OnUpdateData_YR_OptimizedHandler',
    'OnUpdateData_PR_OptimizedHandler',
    'OnUpdateData_YPR_OptimizedHandler',

    'OnUpdateData_XZ_OptimizedHandler',
    'OnUpdateData_XZ_YPR_OptimizedHandler',
    'OnUpdateData_XZ_YR_OptimizedHandler',
    'OnUpdateData_XZ_YP_OptimizedHandler',
    'OnUpdateData_XZ_PR_OptimizedHandler',
    'OnUpdateData_XZ_Y_OptimizedHandler',
    'OnUpdateData_XZ_P_OptimizedHandler',
    'OnUpdateData_XZ_R_OptimizedHandler',

    'OnUpdateData_XYZ_OptimizedHandler',
    'OnUpdateData_XYZ_YPR_OptimizedHandler',
    'OnUpdateData_XYZ_YP_OptimizedHandler',
    'OnUpdateData_XYZ_YR_OptimizedHandler',
    'OnUpdateData_XYZ_PR_OptimizedHandler',
    'OnUpdateData_XYZ_Y_OptimizedHandler',
    'OnUpdateData_XYZ_P_OptimizedHandler',
    'OnUpdateData_XYZ_R_OptimizedHandler',

    'OnControlEntityHandler',
]
