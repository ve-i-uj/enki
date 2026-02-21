"""Entity message handlers."""

from __future__ import annotations

import dataclasses
import logging
import typing
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, TypeAlias

from enki import msgspec
from enki.kbetype.decoders.basic_data_type_decoders import (
    BOOL,
    FLOAT,
    INT8,
    INT32,
    UINT8,
    UINT16,
    VECTOR3,
)
from enki.kbetype.decoders.custom_decoders import (
    ENTITY_ID,
    SPACE_ID,
    KBEEntityId,
    KBESpaceId,
)
from enki.kbetype.pytypes.basic_data_types import (
    KBEBool,
    KBEFloat,
    KBEInt32,
    KBERowByteData,
    KBEVector2,
    KBEVector3,
)
from enki.kbetype.pytypes.vectors import Direction, Position
from enki.misc import devonly
from enki.msg.message import Message
from enki.msg_parser import kbemath
from enki.msg_parser.client_msg_parser.client_msg_pasrser import (
    OnUpdateBasePosMsgParser,
)
from enki.msg_parser.imsg_parser import (
    IMsgParser,
    MsgParserResult,
    ParsedMsgData,
)

if TYPE_CHECKING:
    from enki.kbetype.pytypes.entity_component import EntityComponentData
    from enki.msg.msg_descr import MsgId

    from .ehelper import EntityHelper

logger = logging.getLogger(__name__)


EntityId: TypeAlias = int


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
    def int32_to_float32(value: KBEInt32) -> KBEFloat:
        return FLOAT.decode(memoryview(INT32.encode(value)))[0]

    @staticmethod
    def float32_to_int32(value: KBEFloat) -> KBEInt32:
        return INT32.decode(memoryview(FLOAT.encode(value)))[0]

    @staticmethod
    def read_packed_xz(data: memoryview) -> tuple[KBEVector2, memoryview]:
        # 0x40000000 is 0b1000000000000000000000000000000
        x = 0x40000000
        z = 0x40000000

        data_: int = 0

        value_1, offset = UINT8.decode(data)
        data = data[offset:]
        value_2, offset = UINT8.decode(data)
        data = data[offset:]
        value_3, offset = UINT8.decode(data)
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
            _OptimizedXYZReader.int32_to_float32(x) - 2.0  # type: ignore
        )
        z = _OptimizedXYZReader.float32_to_int32(
            _OptimizedXYZReader.int32_to_float32(z) - 2.0  # type: ignore
        )

        # 0x800000 is 0b100000000000000000000000
        # TODO: [2022-08-31 15:29 burov_alexey@mail.ru]:
        # Знак определяется?
        x |= (data_ & 0x800000) << 8
        z |= (data_ & 0x000800) << 20

        return (
            KBEVector2(
                _OptimizedXYZReader.int32_to_float32(x),  # type: ignore
                _OptimizedXYZReader.int32_to_float32(z),  # type: ignore
            ),
            data,
        )

    @staticmethod
    def read_packed_y(data: memoryview) -> tuple[KBEFloat, memoryview]:
        data_, offset = UINT16.decode(data)
        data = data[offset:]

        y = 0x40000000
        y |= (data_ & 0x7FFF) << 12
        y = _OptimizedXYZReader.float32_to_int32(
            _OptimizedXYZReader.int32_to_float32(y) - 2.0  # type: ignore
        )
        y |= (data_ & 0x8000) << 16

        return _OptimizedXYZReader.int32_to_float32(y), data  # type: ignore


@dataclass
class _PosAndDirData:
    """Данные позиции и направления."""

    x: float = KBEVector3.NO_POS_DIR_VALUE
    y: float = KBEVector3.NO_POS_DIR_VALUE
    z: float = KBEVector3.NO_POS_DIR_VALUE
    yaw: float = KBEVector3.NO_POS_DIR_VALUE
    pitch: float = KBEVector3.NO_POS_DIR_VALUE
    roll: float = KBEVector3.NO_POS_DIR_VALUE

    @property
    def position(self) -> Position:
        return Position(self.x, self.y, self.z)

    @property
    def direction(self) -> Direction:
        return Direction(self.roll, self.pitch, self.yaw)

    def update_position(self, new_position: KBEVector3) -> None:
        self.x = new_position.x
        self.y = new_position.y
        self.z = new_position.z

    def update_direction(self, new_direction: KBEVector3) -> None:
        self.roll = new_direction.x
        self.pitch = new_direction.y
        self.yaw = new_direction.z


@dataclass
class _EntityParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения подсистемы сущностей."""

    entity_id: KBEEntityId


@dataclass(frozen=True)
class _EntityMsgParserResult(MsgParserResult):
    """Родительский класс для результата парсинга сообщения для подсистемы сущностей."""

    success: bool
    result: _EntityParsedMsgData | None = None
    msg_id: MsgId = Message.NO_ID
    text: str = ""


class _EntityMsgParser(IMsgParser):
    """Парсер сообщений подсистемы сущностей.

    В начале всех сообщений для подсистемы сущностей идёт значение id сущности.
    Но для этого id есть оптимизации, выставляемые в конфиге. Так же есть
    сообщ5ния с оптимизациями. Поэтому подклассы переопределяют метод получения
    entityId.
    """

    def __init__(self, entity_helper: EntityHelper) -> None:
        self._entity_helper = entity_helper

    def _get_entity_id(
        self, data: memoryview
    ) -> tuple[KBEEntityId, memoryview]:
        """Получить id сущности."""
        entity_id, offset = ENTITY_ID.decode(data)
        data = data[offset:]
        return entity_id, data

    def parse(self, msg: Message) -> _EntityMsgParserResult:
        """Распарсить сообщение для подсистемы сущностей.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            _EntityMsgParserResult: объект результата обработки

        """
        # Пришли сырые байы
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])

        # В начале id сущности
        entity_id, data = self._get_entity_id(data)

        # Затем данные RPC. Парсим их возвращаем результат
        pd, data_tail = self._parse_data(data, entity_id)
        assert not data_tail

        return _EntityMsgParserResult(success=True, result=pd)

    def _parse_data(
        self, data: memoryview, entity_id: KBEEntityId
    ) -> tuple[_EntityParsedMsgData, memoryview]:
        return _EntityParsedMsgData(entity_id), data[:]

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    # def set_pose(self, entity_id: int, pose_data: PoseData):
    #     self._game.update_entity_properties(entity_id, {
    #         'position': pose_data.position,
    #         'direction': pose_data.direction,


class _OptimizedParserMixin:
    """С оптимизациями заложенными серверным движком вычисляются entity_id."""

    def __init__(self, entity_helper: EntityHelper) -> None:
        self._entity_helper = entity_helper

    def _get_entity_id(self, data: memoryview) -> tuple[EntityId, memoryview]:
        alias_id, offset = UINT8.decode(data)
        data = data[offset:]
        entity_id = self._entity_helper.get_entity_id_by(alias_id)

        return entity_id, data


@dataclass
class _OnUpdateData_XYZ_YPR_BaseParsedMsgData(_EntityParsedMsgData):
    """Родительский класс для классов обновления позиции и направления."""


@dataclass(frozen=True)
class _OnUpdateData_XYZ_YPR_BaseMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: _OnUpdateData_XYZ_YPR_BaseParsedMsgData | None = None
    msg_id: int = NoValue.NO_ID


class _OnUpdateData_XYZ_YPR_BaseParser(_EntityMsgParser, _OptimizedParserMixin):
    _parsed_data_cls: ClassVar[type[_OnUpdateData_XYZ_YPR_BaseParsedMsgData]]
    _handler_result_cls: ClassVar[
        type[_OnUpdateData_XYZ_YPR_BaseMsgParserResult]
    ]

    def _parse_data(
        self, data: memoryview, entity_id: KBEEntityId
    ) -> tuple[_OnUpdateData_XYZ_YPR_BaseParsedMsgData, memoryview]:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values = []
        for _ in range(len(dataclasses.fields(self._parsed_data_cls))):
            value, offset = FLOAT.decode(data)
            data = data[offset:]
            values.append(value)
        pd = self._parsed_data_cls(entity_id, *values)
        return pd, data


@dataclass
class OnUpdatePropertysParsedMsgData(_EntityParsedMsgData):
    entity_id: KBEEntityId
    e_properties: dict[str, Any]
    ec_properties: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclass(frozen=True)
class OnUpdatePropertysMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdatePropertysParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdatePropertys.id


class OnUpdatePropertysMsgParser(_EntityMsgParser):
    """Parser of `onUpdatePropertys`."""

    def parse(self, msg: Message) -> OnUpdatePropertysMsgParserResult:
        """Parser of `onUpdatePropertys`."""
        logger.debug("[%s] (%s)", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])
        entity_id, data = self._get_entity_id(data)
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
                component_uid, offset = UINT8.decode(data)
                data = data[offset:]
                property_uid, offset = UINT8.decode(data)
                data = data[offset:]
            else:
                component_uid, offset = UINT16.decode(data)  # type: ignore
                data = data[offset:]
                property_uid, offset = UINT16.decode(data)  # type: ignore
                data = data[offset:]

            prop_id = component_uid or property_uid
            assert prop_id != 0, "There is NO id of the property"

            type_spec = desc.property_desc_by_id[prop_id]
            value, offset = type_spec.decoder.decode(data)
            data = data[offset:]

            if type_spec.name in desc.component_names:
                # Это значит, что свойство на самом деле компонент (т.е. \
                # отдельный тип)
                ec_data: EntityComponentData = value

                comp_desc = self._entity_helper.get_entity_descr_by_uid(
                    ec_data.component_ent_id
                )
                while ec_data.count > 0:
                    if (
                        self._entity_helper.get_kbenginexml().cellapp.entitydefAliasID
                        and len(comp_desc.property_desc_by_id) <= 255
                    ):
                        _component_uid, offset = UINT8.decode(data)
                        data = data[offset:]
                        property_uid, offset = UINT8.decode(data)
                        data = data[offset:]
                    else:
                        _component_uid, offset = UINT16.decode(data)  # type: ignore
                        data = data[offset:]
                        property_uid, offset = UINT16.decode(data)  # type: ignore
                        data = data[offset:]

                    comp_type_spec = comp_desc.property_desc_by_id[property_uid]
                    v, offset = comp_type_spec.decoder.decode(data)
                    data = data[offset:]
                    ec_data.properties[comp_type_spec.name] = v
                    ec_data.count -= 1

                parsed_data.ec_properties[type_spec.name] = ec_data.properties

                # [2026-02-21 18:54 burov_alexey@mail.ru]:
                # Побочный эффект

                # self._game.update_component_properties(
                #     entity_id, component_name, ec_data.properties
                # )

                continue

            parsed_data.e_properties[type_spec.name] = value

        # self._game.update_entity_properties(entity_id, parsed_data.e_properties)

        return OnUpdatePropertysMsgParserResult(
            success=True, result=parsed_data
        )


@dataclass(frozen=True)
class OnUpdatePropertysOptimizedMsgParserResult(
    OnUpdatePropertysMsgParserResult
):
    msg_id: int = msgspec.client.onUpdatePropertysOptimized.id


class OnUpdatePropertysOptimizedParser(
    OnUpdatePropertysMsgParser, _OptimizedParserMixin
):
    def parse(self, msg: Message) -> OnUpdatePropertysMsgParserResult:
        res = super().parse(msg)
        return OnUpdatePropertysOptimizedMsgParserResult(
            success=True, result=res.result
        )


@dataclass
class OnCreatedProxiesParsedMsgData(_EntityParsedMsgData):
    # After each proxy is created, a uuid is generated by the system,
    # which is used for identification when the front-end re-logins
    rnd_uuid: int
    entity_id: KBEEntityId
    cls_name: str  # the class name of the entity


@dataclass(frozen=True)
class OnCreatedProxiesMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnCreatedProxiesParsedMsgData | None = None
    msg_id: int = msgspec.client.onCreatedProxies.id


class OnCreatedProxiesParser(_EntityMsgParser):

    def parse(self, msg: Message) -> OnCreatedProxiesMsgParserResult:
        values: tuple[Any, ...] = msg.get_values()
        pd = OnCreatedProxiesParsedMsgData(
            rnd_uuid=values[0],
            entity_id=values[1],
            cls_name=values[2],
        )
        self._entity_helper.on_entity_created(
            pd.entity_id, pd.cls_name, is_player=True
        )

        # [2026-02-21 16:57 burov_alexey@mail.ru]:
        # Здесь побочные эффекты. См. on_entity_created
        return OnCreatedProxiesMsgParserResult(success=True, result=pd)


@dataclass
class OnRemoteMethodCallParsedMsgData(_EntityParsedMsgData):
    entity_id: KBEEntityId
    method_name: str
    arguments: list
    # Удалённый вызов у компонента сущности
    comp_prop_desc_name: str | None


@dataclass(frozen=True)
class OnRemoteMethodCallMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnRemoteMethodCallParsedMsgData | None = None
    msg_id: int = msgspec.client.onRemoteMethodCall.id


class OnRemoteMethodCallParser(_EntityMsgParser):
    def parse(self, msg: Message) -> OnRemoteMethodCallMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])

        entity_id, data = self._get_entity_id(data)

        cls_name = self._entity_helper.get_entity_cls_name_by_eid(entity_id)
        assert cls_name is not None
        entity_desc = self._entity_helper.get_entity_descr_by_cls_name(cls_name)

        if entity_desc.is_optimized_cl_method_uid:
            # componentPropertyAliasID
            component_prop_id, offset = UINT8.decode(data)
            data = data[offset:]
        else:
            component_prop_id, offset = UINT16.decode(data)  # type: ignore
            data = data[offset:]

        comp_prop_desc = None
        if component_prop_id != NoValue.NO_ID:
            # It's a component remote method call. The call addresses to
            # the entity property. Get descriptsion of this property.
            comp_prop_desc = entity_desc.property_desc_by_id[component_prop_id]
            # It's an instance of the component-entity (e.g "Test" entity in
            # the demo)
            entity_desc = self._entity_helper.get_entity_descr_by_cls_name(
                comp_prop_desc.component_type_name
            )

        if entity_desc.is_optimized_cl_method_uid:
            method_id, offset = UINT8.decode(data)
            data = data[offset:]
        else:
            method_id, offset = UINT16.decode(data)  # type: ignore
            data = data[offset:]

        method_desc = entity_desc.client_methods[method_id]

        arguments = []
        for kbe_type in method_desc.decoders:
            value, offset = kbe_type.decode(data)
            data = data[offset:]
            arguments.append(value)

        parsed_data = OnRemoteMethodCallParsedMsgData(
            entity_id=entity_id,
            method_name=method_desc.name,
            arguments=arguments,
            comp_prop_desc_name=(
                comp_prop_desc.name if comp_prop_desc is not None else None
            ),
        )

        # [2026-02-21 16:32 burov_alexey@mail.ru]:
        # Побочный эффект
        # if comp_prop_desc is None:
        #     self._game.call_entity_method(
        #         entity_id, method_desc.name, *arguments
        #     )
        # else:
        #     self._game.call_component_method(
        #         entity_id, comp_prop_desc.name, method_desc.name, *arguments
        #     )

        return OnRemoteMethodCallMsgParserResult(
            success=True, result=parsed_data
        )


@dataclass
class OnRemoteMethodCallOptimizedParsedMsgData(_EntityParsedMsgData):
    entity_id: KBEEntityId
    method_name: str
    arguments: list


@dataclass(frozen=True)
class OnRemoteMethodCallOptimizedMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnRemoteMethodCallOptimizedParsedMsgData | None = None
    msg_id: int = msgspec.client.onRemoteMethodCallOptimized.id


class OnRemoteMethodCallOptimizedParser(
    OnRemoteMethodCallParser, _OptimizedParserMixin
):
    def parse(self, msg: Message) -> OnRemoteMethodCallMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        return super().parse(msg)


@dataclass
class OnEntityDestroyedParsedMsgData(_EntityParsedMsgData):
    entity_id: KBEEntityId


@dataclass(frozen=True)
class OnEntityDestroyedMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnEntityDestroyedParsedMsgData | None = None
    msg_id: int = msgspec.client.onEntityDestroyed.id


class OnEntityDestroyedParser(_EntityMsgParser):
    def parse(self, msg: Message) -> OnEntityDestroyedMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        entity_id = msg.get_values()[0]
        entity_id = typing.cast("KBEEntityId", entity_id)

        # [2026-02-21 15:40 burov_alexey@mail.ru]:
        # Побочный эффект. Нужно убрать в приложение.
        # desc = self._entity_helper.get_entity_descr_by_eid(entity_id)
        # for comp_name in desc.component_names:
        #     self._game.call_component_method(entity_id, comp_name, "onDetached")
        # self._game.call_entity_destroyed(entity_id)

        self._entity_helper.on_entity_destroyed(entity_id)

        return OnEntityDestroyedMsgParserResult(
            success=True, result=OnEntityDestroyedParsedMsgData(entity_id)
        )


@dataclass
class OnEntityEnterWorldParsedMsgData(_EntityParsedMsgData):
    entity_id: KBEEntityId
    entity_type_id: int
    is_on_ground: KBEBool
    component_names: set[str]


@dataclass(frozen=True)
class OnEntityEnterWorldMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnEntityEnterWorldParsedMsgData | None = None
    msg_id: int = msgspec.client.onEntityEnterWorld.id


class OnEntityEnterWorldParser(_EntityMsgParser):

    def parse(self, msg: Message) -> OnEntityEnterWorldMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        bytes_data = msg.get_values()[0]
        bytes_data = typing.cast("KBERowByteData", bytes_data)
        data = memoryview(bytes_data)

        entity_id, data = self._get_entity_id(data)

        if self._entity_helper.is_entitydefAliasID:
            entity_type_id, offset = UINT8.decode(data)
            data = data[offset:]
        else:
            entity_type_id, offset = UINT16.decode(data)  # type: ignore
            data = data[offset:]

        is_on_ground = KBEBool(False)
        if data:
            is_on_ground, offset = BOOL.decode(data)
            data = data[offset:]

        desc = self._entity_helper.get_entity_descr_by_uid(entity_type_id)

        pd = OnEntityEnterWorldParsedMsgData(
            entity_id,
            entity_type_id,
            is_on_ground,
            component_names=desc.component_names,
        )

        if not self._entity_helper.is_player(entity_id):
            # The proxy entity (aka player) is initialized in
            # the onCreatedProxies message

            # [2026-02-21 15:47 burov_alexey@mail.ru]:
            # Побочный эффект. Убрать в приложение.
            # self.on_entity_created(entity_id, desc.name, False)

            self._entity_helper.on_entity_created(
                pd.entity_id, desc.name, is_player=False
            )

        # [2026-02-21 15:47 burov_alexey@mail.ru]:
        # Побочный эффект. Убрать в приложение.
        # self._game.call_entity_method(entity_id, "onEnterWorld")

        # for comp_name in desc.component_names:
        #     self._game.call_component_method(
        #         entity_id, comp_name, "onEnterWorld"
        #     )

        # self._game.update_entity_properties(
        #     entity_id, {"onGround": pd.is_on_ground}
        # )

        return OnEntityEnterWorldMsgParserResult(success=True, result=pd)


@dataclass
class OnEntityLeaveWorldParsedMsgData(_EntityParsedMsgData):
    entity_id: KBEEntityId


@dataclass(frozen=True)
class OnEntityLeaveWorldMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnEntityLeaveWorldParsedMsgData | None = None
    msg_id: int = msgspec.client.onEntityLeaveWorld.id


class OnEntityLeaveWorldParser(_EntityMsgParser):
    def parse(self, msg: Message) -> OnEntityLeaveWorldMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        bytes_data = msg.get_values()[0]
        bytes_data = typing.cast("KBERowByteData", bytes_data)
        data = memoryview(bytes_data)

        entity_id, data = self._get_entity_id(data)

        self._entity_helper.on_entity_leave_world(entity_id)

        # [2026-02-21 15:58 burov_alexey@mail.ru]:
        # Побочные эффекты. В приложение.
        # desc = self._entity_helper.get_entity_descr_by_eid(entity_id)
        # self._game.call_entity_method(entity_id, "onLeaveWorld")
        # for comp_name in desc.component_names:
        #     self._game.call_component_method(
        #         entity_id, comp_name, "onLeaveWorld"
        #     )

        return OnEntityLeaveWorldMsgParserResult(
            success=True, result=OnEntityLeaveWorldParsedMsgData(entity_id)
        )


@dataclass
class OnEntityLeaveWorldOptimizedParsedMsgData(_EntityParsedMsgData):
    entity_id: KBEEntityId = NoValue.NO_ENTITY_ID


@dataclass(frozen=True)
class OnEntityLeaveWorldOptimizedMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnEntityLeaveWorldOptimizedParsedMsgData | None = None
    msg_id: int = msgspec.client.onEntityLeaveWorldOptimized.id


class OnEntityLeaveWorldOptimizedParser(
    OnEntityLeaveWorldParser, _OptimizedParserMixin
):

    def parse(self, msg: Message) -> OnEntityLeaveWorldMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        res: OnEntityLeaveWorldMsgParserResult = super().parse(msg)

        return res


@dataclass
class OnSetEntityPosAndDirParsedMsgData(_EntityParsedMsgData):
    entity_id: KBEEntityId
    position: KBEVector3
    direction: KBEVector3


@dataclass(frozen=True)
class OnSetEntityPosAndDirMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnSetEntityPosAndDirParsedMsgData | None = None
    msg_id: int = msgspec.client.onSetEntityPosAndDir.id
    text: str = ""


class OnSetEntityPosAndDirParser(_EntityMsgParser):

    def parse(self, msg: Message) -> OnSetEntityPosAndDirMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])
        entity_id, data = self._get_entity_id(data)

        position, offset = VECTOR3.decode(data)
        data = data[offset:]

        direction, offset = VECTOR3.decode(data)
        data = data[offset:]

        pd = OnSetEntityPosAndDirParsedMsgData(entity_id, position, direction)

        # [2026-02-21 16:02 burov_alexey@mail.ru]:
        # Побочный эффект
        # pose_data = _PosAndDirData()
        # pose_data.update_position(poKBEVector3sition)
        # pose_data.update_direction(direction)
        # self.set_pose(entity_id, pose_data)

        return OnSetEntityPosAndDirMsgParserResult(success=True, result=pd)


@dataclass
class OnEntityEnterSpaceParsedMsgData(_EntityParsedMsgData):
    entity_id: KBEEntityId
    space_id: KBESpaceId
    is_on_ground: KBEBool


@dataclass(frozen=True)
class OnEntityEnterSpaceMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnEntityEnterSpaceParsedMsgData | None = None
    msg_id: int = msgspec.client.onEntityEnterSpace.id


class OnEntityEnterSpaceParser(_EntityMsgParser):
    def parse(self, msg: Message) -> OnEntityEnterSpaceMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])

        entity_id, offset = ENTITY_ID.decode(data)
        data = data[offset:]

        space_id, offset = SPACE_ID.decode(data)
        data = data[offset:]

        is_on_ground = KBEBool(False)
        if data:
            is_on_ground, offset = BOOL.decode(data)
            data = data[offset:]

        pd = OnEntityEnterSpaceParsedMsgData(entity_id, space_id, is_on_ground)

        # [2026-02-21 16:04 burov_alexey@mail.ru]:
        # Побочный эффект.
        # desc = self._entity_helper.get_entity_descr_by_eid(entity_id)
        # self._game.update_entity_properties(
        #     entity_id,
        #     {
        #         "spaceID": pd.space_id,
        #         "onGround": pd.is_on_ground,
        #     },
        # )
        # self._game.call_entity_method(entity_id, "onEnterSpace")

        # for comp_name in desc.component_names:
        #     self._game.call_component_method(
        #         entity_id, comp_name, "onEnterSpace"
        #     )

        return OnEntityEnterSpaceMsgParserResult(True, pd)


@dataclass
class OnEntityLeaveSpaceParsedMsgData(_EntityParsedMsgData):
    entity_id: KBEEntityId


@dataclass(frozen=True)
class OnEntityLeaveSpaceMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnEntityLeaveSpaceParsedMsgData | None = None
    msg_id: int = msgspec.client.onEntityLeaveSpace.id


class OnEntityLeaveSpaceParser(_EntityMsgParser):
    def parse(self, msg: Message) -> OnEntityLeaveSpaceMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])

        entity_id, data = self._get_entity_id(data)

        pd = OnEntityLeaveSpaceParsedMsgData(entity_id)

        # [2026-02-21 16:05 burov_alexey@mail.ru]:
        # Побочный эффект
        # desc = self._entity_helper.get_entity_descr_by_eid(entity_id)
        # self._game.call_entity_method(entity_id, "onLeaveSpace")

        # for comp_name in desc.component_names:
        #     self._game.call_component_method(
        #         entity_id, comp_name, "onLeaveSpace"
        #     )

        return OnEntityLeaveSpaceMsgParserResult(True, pd)


@dataclass
class OnUpdateBasePosParsedMsgData(_EntityParsedMsgData):
    position: KBEVector3


@dataclass(frozen=True)
class OnUpdateBasePosMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateBasePosParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateBasePos.id


class OnUpdateBasePosParser(_EntityMsgParser):
    def parse(self, msg: Message) -> OnUpdateBasePosMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())

        # [2026-02-21 16:05 burov_alexey@mail.ru]:
        # Побочный эффект
        # entity_id = self._entity_helper.get_player_id()
        # pose_data = _PosAndDirData(*msg.get_values())
        # self.set_pose(entity_id, pose_data)

        res = OnUpdateBasePosMsgParser().parse(msg)
        assert res.success
        assert res.result is not None

        pd = OnUpdateBasePosParsedMsgData(
            KBEVector3(res.result.x, res.result.y, res.result.z)
        )
        return OnUpdateBasePosMsgParserResult(True, pd)


@dataclass
class OnUpdateBaseDirParsedMsgData(_EntityParsedMsgData):
    direction: KBEVector3


@dataclass(frozen=True)
class OnUpdateBaseDirMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateBaseDirParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateBaseDir.id


class OnUpdateBaseDirParser(_EntityMsgParser):
    def parse(self, msg: Message) -> OnUpdateBaseDirMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())

        res = OnUpdateBasePosMsgParser().parse(msg)
        assert res.success
        assert res.result is not None
        pd: OnUpdateBaseDirParsedMsgData = OnUpdateBaseDirParsedMsgData(
            KBEVector3(res.result.x, res.result.y, res.result.z)
        )

        # [2026-02-21 16:12 burov_alexey@mail.ru]:
        # Побочный эффект
        # entity_id = self._entity_helper.get_player_id()
        # pose_data = _PosAndDirData()
        # pose_data.update_direction(pd.direction)
        # self.set_pose(entity_id, pose_data)

        return OnUpdateBaseDirMsgParserResult(True, pd)


@dataclass
class OnUpdateBasePosXZParsedMsgData(_EntityParsedMsgData):
    x: KBEFloat
    z: KBEFloat


@dataclass(frozen=True)
class OnUpdateBasePosXZMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateBasePosXZParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateBasePosXZ.id


class OnUpdateBasePosXZParser(_EntityMsgParser):
    def parse(self, msg: Message) -> OnUpdateBasePosXZMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnUpdateBasePosXZParsedMsgData(*values)

        # [2026-02-21 16:17 burov_alexey@mail.ru]:
        # Побочный эффект
        # entity_id = self._entity_helper.get_player_id()
        # pose_data = _PosAndDirData(x=pd.x, z=pd.z)
        # self.set_pose(entity_id, pose_data)

        return OnUpdateBasePosXZMsgParserResult(True, pd)


@dataclass
class OnUpdateDataParsedMsgData(_EntityParsedMsgData):
    pass


@dataclass(frozen=True)
class OnUpdateDataMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateDataParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData.id


class OnUpdateDataParser(_EntityMsgParser, _OptimizedParserMixin):
    def parse(self, msg: Message) -> OnUpdateDataMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        res = super().parse(msg)
        return OnUpdateDataMsgParserResult(
            res.success, OnUpdateDataParsedMsgData(), text=res.text
        )


@dataclass
class OnUpdateData_XZ_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float


@dataclass(frozen=True)
class OnUpdateData_XZ_MsgParserResult(
    _OnUpdateData_XYZ_YPR_BaseMsgParserResult
):
    success: bool
    result: OnUpdateData_XZ_ParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xz.id


class OnUpdateData_XZ_Parser(_OnUpdateData_XYZ_YPR_BaseParser):
    _parsed_data_cls = OnUpdateData_XZ_ParsedMsgData
    _handler_result_cls = OnUpdateData_XZ_MsgParserResult


@dataclass
class OnUpdateData_YPR_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    yaw: float
    pitch: float
    roll: float


@dataclass(frozen=True)
class OnUpdateData_YPR_MsgParserResult(
    _OnUpdateData_XYZ_YPR_BaseMsgParserResult
):
    success: bool
    result: OnUpdateData_YPR_ParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_ypr.id


class OnUpdateData_YPR_Parser(_OnUpdateData_XYZ_YPR_BaseParser):
    _parsed_data_cls = OnUpdateData_YPR_ParsedMsgData
    _handler_result_cls = OnUpdateData_YPR_MsgParserResult


@dataclass
class OnUpdateData_YP_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    yaw: float
    pitch: float


@dataclass(frozen=True)
class OnUpdateData_YP_MsgParserResult(
    _OnUpdateData_XYZ_YPR_BaseMsgParserResult
):
    success: bool
    result: OnUpdateData_YP_ParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_yp.id


class OnUpdateData_YP_Parser(_OnUpdateData_XYZ_YPR_BaseParser):
    _parsed_data_cls = OnUpdateData_YP_ParsedMsgData
    _handler_result_cls = OnUpdateData_YP_MsgParserResult


@dataclass
class OnUpdateData_YR_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    yaw: float
    roll: float


@dataclass(frozen=True)
class OnUpdateData_YR_MsgParserResult(
    _OnUpdateData_XYZ_YPR_BaseMsgParserResult
):
    success: bool
    result: OnUpdateData_YR_ParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_yr.id


class OnUpdateData_YR_Parser(_OnUpdateData_XYZ_YPR_BaseParser):
    _parsed_data_cls = OnUpdateData_YR_ParsedMsgData
    _handler_result_cls = OnUpdateData_YR_MsgParserResult


@dataclass
class OnUpdateData_PR_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    pitch: float
    roll: float


@dataclass(frozen=True)
class OnUpdateData_PR_MsgParserResult(
    _OnUpdateData_XYZ_YPR_BaseMsgParserResult
):
    success: bool
    result: OnUpdateData_PR_ParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_pr.id


class OnUpdateData_PR_Parser(_OnUpdateData_XYZ_YPR_BaseParser):
    _parsed_data_cls = OnUpdateData_PR_ParsedMsgData
    _handler_result_cls = OnUpdateData_PR_MsgParserResult


@dataclass
class OnUpdateData_Y_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    yaw: float


@dataclass(frozen=True)
class OnUpdateData_Y_MsgParserResult(_OnUpdateData_XYZ_YPR_BaseMsgParserResult):
    success: bool
    result: OnUpdateData_Y_ParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_y.id


class OnUpdateData_Y_Parser(_OnUpdateData_XYZ_YPR_BaseParser):
    _parsed_data_cls = OnUpdateData_Y_ParsedMsgData
    _handler_result_cls = OnUpdateData_Y_MsgParserResult


@dataclass
class OnUpdateData_P_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    pitch: float


@dataclass(frozen=True)
class OnUpdateData_P_MsgParserResult(_OnUpdateData_XYZ_YPR_BaseMsgParserResult):
    success: bool
    result: OnUpdateData_P_ParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_p.id


class OnUpdateData_P_Parser(_OnUpdateData_XYZ_YPR_BaseParser):
    _parsed_data_cls = OnUpdateData_P_ParsedMsgData
    _handler_result_cls = OnUpdateData_P_MsgParserResult


@dataclass
class OnUpdateData_R_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    roll: float


@dataclass(frozen=True)
class OnUpdateData_R_MsgParserResult(_OnUpdateData_XYZ_YPR_BaseMsgParserResult):
    success: bool
    result: OnUpdateData_R_ParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_r.id


class OnUpdateData_R_Parser(_OnUpdateData_XYZ_YPR_BaseParser):
    _parsed_data_cls = OnUpdateData_R_ParsedMsgData
    _handler_result_cls = OnUpdateData_R_MsgParserResult


@dataclass
class OnUpdateData_XZ_YPR_ParsedMsgData(
    _OnUpdateData_XYZ_YPR_BaseParsedMsgData
):
    x: float
    z: float
    yaw: float
    pitch: float
    roll: float


@dataclass(frozen=True)
class OnUpdateData_XZ_YPR_MsgParserResult(
    _OnUpdateData_XYZ_YPR_BaseMsgParserResult
):
    success: bool
    result: OnUpdateData_XZ_YPR_ParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xz_ypr.id


class OnUpdateData_XZ_YPR_Parser(_OnUpdateData_XYZ_YPR_BaseParser):
    _parsed_data_cls = OnUpdateData_XZ_YPR_ParsedMsgData
    _handler_result_cls = OnUpdateData_XZ_YPR_MsgParserResult


@dataclass
class OnUpdateData_XZ_YP_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float
    yaw: float
    pitch: float


@dataclass(frozen=True)
class OnUpdateData_XZ_YP_MsgParserResult(
    _OnUpdateData_XYZ_YPR_BaseMsgParserResult
):
    success: bool
    result: OnUpdateData_XZ_YP_ParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xz_yp.id


class OnUpdateData_XZ_YP_Parser(_OnUpdateData_XYZ_YPR_BaseParser):
    _parsed_data_cls = OnUpdateData_XZ_YP_ParsedMsgData
    _handler_result_cls = OnUpdateData_XZ_YP_MsgParserResult


@dataclass
class OnUpdateData_XZ_YR_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float
    yaw: float
    roll: float


@dataclass(frozen=True)
class OnUpdateData_XZ_YR_MsgParserResult(
    _OnUpdateData_XYZ_YPR_BaseMsgParserResult
):
    success: bool
    result: OnUpdateData_XZ_YR_ParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xz_yr.id


class OnUpdateData_XZ_YR_Parser(_OnUpdateData_XYZ_YPR_BaseParser):
    _parsed_data_cls = OnUpdateData_XZ_YR_ParsedMsgData
    _handler_result_cls = OnUpdateData_XZ_YR_MsgParserResult


@dataclass
class OnUpdateData_XZ_PR_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float
    yaw: float
    pitch: float
    roll: float


@dataclass(frozen=True)
class OnUpdateData_XZ_PR_MsgParserResult(
    _OnUpdateData_XYZ_YPR_BaseMsgParserResult
):
    success: bool
    result: OnUpdateData_XZ_PR_ParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xz_pr.id


class OnUpdateData_XZ_PR_Parser(_OnUpdateData_XYZ_YPR_BaseParser):
    _parsed_data_cls = OnUpdateData_XZ_PR_ParsedMsgData
    _handler_result_cls = OnUpdateData_XZ_PR_MsgParserResult


@dataclass
class OnUpdateData_XZ_Y_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float
    yaw: float


@dataclass(frozen=True)
class OnUpdateData_XZ_Y_MsgParserResult(
    _OnUpdateData_XYZ_YPR_BaseMsgParserResult
):
    success: bool
    result: OnUpdateData_XZ_Y_ParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xz_y.id


class OnUpdateData_XZ_Y_Parser(_OnUpdateData_XYZ_YPR_BaseParser):
    _parsed_data_cls = OnUpdateData_XZ_Y_ParsedMsgData
    _handler_result_cls = OnUpdateData_XZ_Y_MsgParserResult


@dataclass
class OnUpdateData_XZ_P_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float
    pitch: float


@dataclass(frozen=True)
class OnUpdateData_XZ_P_MsgParserResult(
    _OnUpdateData_XYZ_YPR_BaseMsgParserResult
):
    success: bool
    result: OnUpdateData_XZ_P_ParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xz_p.id


class OnUpdateData_XZ_P_Parser(_OnUpdateData_XYZ_YPR_BaseParser):
    _parsed_data_cls = OnUpdateData_XZ_P_ParsedMsgData
    _handler_result_cls = OnUpdateData_XZ_P_MsgParserResult


@dataclass
class OnUpdateData_XZ_R_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float
    roll: float


@dataclass(frozen=True)
class OnUpdateData_XZ_R_MsgParserResult(
    _OnUpdateData_XYZ_YPR_BaseMsgParserResult
):
    success: bool
    result: OnUpdateData_XZ_R_ParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xz_r.id


class OnUpdateData_XZ_R_Parser(_OnUpdateData_XYZ_YPR_BaseParser):
    _parsed_data_cls = OnUpdateData_XZ_R_ParsedMsgData
    _handler_result_cls = OnUpdateData_XZ_R_MsgParserResult


@dataclass
class OnUpdateData_XYZ_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float
    y: float


@dataclass(frozen=True)
class OnUpdateData_XYZ_MsgParserResult(
    _OnUpdateData_XYZ_YPR_BaseMsgParserResult
):
    success: bool
    result: OnUpdateData_XYZ_ParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xyz.id


class OnUpdateData_XYZ_Parser(_OnUpdateData_XYZ_YPR_BaseParser):
    _parsed_data_cls = OnUpdateData_XYZ_ParsedMsgData
    _handler_result_cls = OnUpdateData_XYZ_MsgParserResult


@dataclass
class OnUpdateData_XYZ_YPR_ParsedMsgData(
    _OnUpdateData_XYZ_YPR_BaseParsedMsgData
):
    x: float
    z: float
    y: float
    yaw: float
    pitch: float
    roll: float


@dataclass(frozen=True)
class OnUpdateData_XYZ_YPR_MsgParserResult(
    _OnUpdateData_XYZ_YPR_BaseMsgParserResult
):
    success: bool
    result: OnUpdateData_XYZ_YPR_ParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xyz_ypr.id


class OnUpdateData_XYZ_YPR_Parser(_OnUpdateData_XYZ_YPR_BaseParser):
    _parsed_data_cls = OnUpdateData_XYZ_YPR_ParsedMsgData
    _handler_result_cls = OnUpdateData_XYZ_YPR_MsgParserResult


@dataclass
class OnUpdateData_XYZ_YP_ParsedMsgData(
    _OnUpdateData_XYZ_YPR_BaseParsedMsgData
):
    x: float
    z: float
    y: float
    yaw: float
    pitch: float


@dataclass(frozen=True)
class OnUpdateData_XYZ_YP_MsgParserResult(
    _OnUpdateData_XYZ_YPR_BaseMsgParserResult
):
    success: bool
    result: OnUpdateData_XYZ_YP_ParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xyz_yp.id


class OnUpdateData_XYZ_YP_Parser(_OnUpdateData_XYZ_YPR_BaseParser):
    _parsed_data_cls = OnUpdateData_XYZ_YP_ParsedMsgData
    _handler_result_cls = OnUpdateData_XYZ_YP_MsgParserResult


@dataclass
class OnUpdateData_XYZ_YR_ParsedMsgData(
    _OnUpdateData_XYZ_YPR_BaseParsedMsgData
):
    x: float
    z: float
    y: float
    yaw: float
    pitch: float


@dataclass(frozen=True)
class OnUpdateData_XYZ_YR_MsgParserResult(
    _OnUpdateData_XYZ_YPR_BaseMsgParserResult
):
    success: bool
    result: OnUpdateData_XYZ_YR_ParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xyz_yr.id


class OnUpdateData_XYZ_YR_Parser(_OnUpdateData_XYZ_YPR_BaseParser):
    _parsed_data_cls = OnUpdateData_XYZ_YR_ParsedMsgData
    _handler_result_cls = OnUpdateData_XYZ_YR_MsgParserResult


@dataclass
class OnUpdateData_XYZ_PR_ParsedMsgData(
    _OnUpdateData_XYZ_YPR_BaseParsedMsgData
):
    x: float
    z: float
    y: float
    pitch: float
    roll: float


@dataclass(frozen=True)
class OnUpdateData_XYZ_PR_MsgParserResult(
    _OnUpdateData_XYZ_YPR_BaseMsgParserResult
):
    success: bool
    result: OnUpdateData_XYZ_PR_ParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xyz_pr.id


class OnUpdateData_XYZ_PR_Parser(_OnUpdateData_XYZ_YPR_BaseParser):
    _parsed_data_cls = OnUpdateData_XYZ_PR_ParsedMsgData
    _handler_result_cls = OnUpdateData_XYZ_PR_MsgParserResult


@dataclass
class OnUpdateData_XYZ_Y_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float
    y: float
    yaw: float


@dataclass(frozen=True)
class OnUpdateData_XYZ_Y_MsgParserResult(
    _OnUpdateData_XYZ_YPR_BaseMsgParserResult
):
    success: bool
    result: OnUpdateData_XYZ_Y_ParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xyz_y.id


class OnUpdateData_XYZ_Y_Parser(_OnUpdateData_XYZ_YPR_BaseParser):
    _parsed_data_cls = OnUpdateData_XYZ_Y_ParsedMsgData
    _handler_result_cls = OnUpdateData_XYZ_Y_MsgParserResult


@dataclass
class OnUpdateData_XYZ_P_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float
    y: float
    pitch: float


@dataclass(frozen=True)
class OnUpdateData_XYZ_P_MsgParserResult(
    _OnUpdateData_XYZ_YPR_BaseMsgParserResult
):
    success: bool
    result: OnUpdateData_XYZ_P_ParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xyz_p.id


class OnUpdateData_XYZ_P_Parser(_OnUpdateData_XYZ_YPR_BaseParser):
    _parsed_data_cls = OnUpdateData_XYZ_P_ParsedMsgData
    _handler_result_cls = OnUpdateData_XYZ_P_MsgParserResult


@dataclass
class OnUpdateData_XYZ_R_ParsedMsgData(_OnUpdateData_XYZ_YPR_BaseParsedMsgData):
    x: float
    z: float
    y: float
    pitch: float


@dataclass(frozen=True)
class OnUpdateData_XYZ_R_MsgParserResult(
    _OnUpdateData_XYZ_YPR_BaseMsgParserResult
):
    success: bool
    result: OnUpdateData_XYZ_R_ParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xyz_r.id


class OnUpdateData_XYZ_R_Parser(_OnUpdateData_XYZ_YPR_BaseParser):
    _parsed_data_cls = OnUpdateData_XYZ_R_ParsedMsgData
    _handler_result_cls = OnUpdateData_XYZ_R_MsgParserResult


@dataclass
class OnUpdateData_Y_OptimizedParsedMsgData(_EntityParsedMsgData):
    yaw: float


@dataclass(frozen=True)
class OnUpdateData_Y_OptimizedMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateData_Y_OptimizedParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_y_optimized.id


class OnUpdateData_Y_OptimizedParser(_EntityMsgParser, _OptimizedParserMixin):
    def _parse_data(
        self, data: memoryview, entity_id: KBEEntityId
    ) -> tuple[OnUpdateData_Y_OptimizedParsedMsgData, memoryview]:
        value, offset = INT8.decode(data)
        data = data[offset:]
        angle = kbemath.int82angle(value)
        pd = OnUpdateData_Y_OptimizedParsedMsgData(angle)
        return pd, data

    def _process_parsed_data(
        self, pd: OnUpdateData_Y_OptimizedParsedMsgData, entity_id: KBEEntityId
    ) -> OnUpdateData_Y_OptimizedMsgParserResult:

        # [2026-02-21 16:19 burov_alexey@mail.ru]:
        # Побочный эффект
        # pose_data = _PosAndDirData(yaw=pd.yaw)
        # self.set_pose(entity_id, pose_data)

        return OnUpdateData_Y_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_R_OptimizedParsedMsgData(_EntityParsedMsgData):
    roll: float


@dataclass(frozen=True)
class OnUpdateData_R_OptimizedMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateData_R_OptimizedParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_r_optimized.id


class OnUpdateData_R_OptimizedParser(_EntityMsgParser, _OptimizedParserMixin):
    def _parse_data(
        self, data: memoryview, entity_id: KBEEntityId
    ) -> tuple[OnUpdateData_R_OptimizedParsedMsgData, memoryview]:
        value, offset = INT8.decode(data)
        data = data[offset:]
        angle = kbemath.int82angle(value)
        pd = OnUpdateData_R_OptimizedParsedMsgData(angle)
        return pd, data

    def _process_parsed_data(
        self, pd: OnUpdateData_R_OptimizedParsedMsgData, entity_id: KBEEntityId
    ) -> OnUpdateData_R_OptimizedMsgParserResult:
        # [2026-02-21 16:19 burov_alexey@mail.ru]:
        # Побочный эффект
        # pose_data = _PosAndDirData(roll=pd.roll)
        # self.set_pose(entity_id, pose_data)

        return OnUpdateData_R_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_P_OptimizedParsedMsgData(_EntityParsedMsgData):
    pitch: float


@dataclass(frozen=True)
class OnUpdateData_P_OptimizedMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateData_P_OptimizedParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_p_optimized.id


class OnUpdateData_P_OptimizedParser(_EntityMsgParser, _OptimizedParserMixin):
    def _parse_data(
        self, data: memoryview, entity_id: KBEEntityId
    ) -> tuple[OnUpdateData_P_OptimizedParsedMsgData, memoryview]:
        value, offset = INT8.decode(data)
        data = data[offset:]
        angle = kbemath.int82angle(value)
        pd = OnUpdateData_P_OptimizedParsedMsgData(angle)
        return pd, data

    def _process_parsed_data(
        self, pd: OnUpdateData_P_OptimizedParsedMsgData, entity_id: KBEEntityId
    ) -> OnUpdateData_P_OptimizedMsgParserResult:
        # [2026-02-21 16:19 burov_alexey@mail.ru]:
        # Побочный эффект
        # pose_data = _PosAndDirData(pitch=pd.pitch)
        # self.set_pose(entity_id, pose_data)

        return OnUpdateData_P_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_YP_OptimizedParsedMsgData(_EntityParsedMsgData):
    yaw: float
    pitch: float


@dataclass(frozen=True)
class OnUpdateData_YP_OptimizedMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateData_YP_OptimizedParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_yp_optimized.id


class OnUpdateData_YP_OptimizedParser(_EntityMsgParser, _OptimizedParserMixin):
    def _parse_data(
        self, data: memoryview, entity_id: KBEEntityId
    ) -> tuple[OnUpdateData_YP_OptimizedParsedMsgData, memoryview]:
        value, offset = INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)
        value, offset = INT8.decode(data)
        data = data[offset:]
        angle_2 = kbemath.int82angle(value)
        pd = OnUpdateData_YP_OptimizedParsedMsgData(angle_1, angle_2)
        return pd, data

    def _process_parsed_data(
        self, pd: OnUpdateData_YP_OptimizedParsedMsgData, entity_id: KBEEntityId
    ) -> OnUpdateData_YP_OptimizedMsgParserResult:
        # [2026-02-21 16:19 burov_alexey@mail.ru]:
        # Побочный эффект
        # pose_data = _PosAndDirData(yaw=pd.yaw, pitch=pd.pitch)
        # self.set_pose(entity_id, pose_data)

        return OnUpdateData_YP_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_YR_OptimizedParsedMsgData(_EntityParsedMsgData):
    yaw: float
    roll: float


@dataclass(frozen=True)
class OnUpdateData_YR_OptimizedMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateData_YR_OptimizedParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_yr_optimized.id


class OnUpdateData_YR_OptimizedParser(_EntityMsgParser, _OptimizedParserMixin):
    def _parse_data(
        self, data: memoryview, entity_id: KBEEntityId
    ) -> tuple[OnUpdateData_YR_OptimizedParsedMsgData, memoryview]:
        value, offset = INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)
        value, offset = INT8.decode(data)
        data = data[offset:]
        angle_2 = kbemath.int82angle(value)
        pd = OnUpdateData_YR_OptimizedParsedMsgData(angle_1, angle_2)
        return pd, data

    def _process_parsed_data(
        self, pd: OnUpdateData_YR_OptimizedParsedMsgData, entity_id: KBEEntityId
    ) -> OnUpdateData_YR_OptimizedMsgParserResult:
        # [2026-02-21 16:19 burov_alexey@mail.ru]:
        # Побочный эффект
        # pose_data = _PosAndDirData(yaw=pd.yaw, roll=pd.roll)
        # self.set_pose(entity_id, pose_data)

        return OnUpdateData_YR_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_PR_OptimizedParsedMsgData(_EntityParsedMsgData):
    pitch: float
    roll: float


@dataclass(frozen=True)
class OnUpdateData_PR_OptimizedMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateData_PR_OptimizedParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_pr_optimized.id


class OnUpdateData_PR_OptimizedParser(_EntityMsgParser, _OptimizedParserMixin):
    def _parse_data(
        self, data: memoryview, entity_id: KBEEntityId
    ) -> tuple[OnUpdateData_PR_OptimizedParsedMsgData, memoryview]:
        value, offset = INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)

        value, offset = INT8.decode(data)
        data = data[offset:]
        angle_2 = kbemath.int82angle(value)

        pd = OnUpdateData_PR_OptimizedParsedMsgData(angle_1, angle_2)
        return pd, data

    def _process_parsed_data(
        self, pd: OnUpdateData_PR_OptimizedParsedMsgData, entity_id: KBEEntityId
    ) -> OnUpdateData_PR_OptimizedMsgParserResult:
        # [2026-02-21 16:19 burov_alexey@mail.ru]:
        # Побочный эффект
        # pose_data = _PosAndDirData(pitch=pd.pitch, roll=pd.roll)
        # self.set_pose(entity_id, pose_data)

        return OnUpdateData_PR_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_YPR_OptimizedParsedMsgData(_EntityParsedMsgData):
    yaw: float
    pitch: float
    roll: float


@dataclass(frozen=True)
class OnUpdateData_YPR_OptimizedMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateData_YPR_OptimizedParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_ypr_optimized.id


class OnUpdateData_YPR_OptimizedParser(_EntityMsgParser, _OptimizedParserMixin):
    def _parse_data(
        self, data: memoryview, entity_id: KBEEntityId
    ) -> tuple[OnUpdateData_YPR_OptimizedParsedMsgData, memoryview]:
        value, offset = INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)

        value, offset = INT8.decode(data)
        data = data[offset:]
        angle_2 = kbemath.int82angle(value)

        value, offset = INT8.decode(data)
        data = data[offset:]
        angle_3 = kbemath.int82angle(value)

        pd = OnUpdateData_YPR_OptimizedParsedMsgData(angle_1, angle_2, angle_3)
        return pd, data

    def _process_parsed_data(
        self,
        pd: OnUpdateData_YPR_OptimizedParsedMsgData,
        entity_id: KBEEntityId,
    ) -> OnUpdateData_YPR_OptimizedMsgParserResult:
        # [2026-02-21 16:19 burov_alexey@mail.ru]:
        # Побочный эффект
        # pose_data = _PosAndDirData(yaw=pd.yaw, pitch=pd.pitch, roll=pd.roll)
        # self.set_pose(entity_id, pose_data)

        return OnUpdateData_YPR_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XZ_OptimizedParsedMsgData(_EntityParsedMsgData):
    x: float
    z: float


@dataclass(frozen=True)
class OnUpdateData_XZ_OptimizedMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateData_XZ_OptimizedParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xz_optimized.id


class OnUpdateData_XZ_OptimizedParser(_EntityMsgParser, _OptimizedParserMixin):
    def _parse_data(
        self, data: memoryview, entity_id: KBEEntityId
    ) -> tuple[OnUpdateData_XZ_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)
        pd = OnUpdateData_XZ_OptimizedParsedMsgData(v2.x, v2.y)
        return pd, data

    def _process_parsed_data(
        self, pd: OnUpdateData_XZ_OptimizedParsedMsgData, entity_id: KBEEntityId
    ) -> OnUpdateData_XZ_OptimizedMsgParserResult:
        # [2026-02-21 16:19 burov_alexey@mail.ru]:
        # Побочный эффект
        # pose_data = _PosAndDirData(x=pd.x, z=pd.z)
        # self.set_pose(entity_id, pose_data)
        return OnUpdateData_XZ_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XZ_YPR_OptimizedParsedMsgData(_EntityParsedMsgData):
    x: float
    z: float
    yaw: float
    pitch: float
    roll: float


@dataclass(frozen=True)
class OnUpdateData_XZ_YPR_OptimizedMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateData_XZ_YPR_OptimizedParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xz_ypr_optimized.id


class OnUpdateData_XZ_YPR_OptimizedParser(
    _EntityMsgParser, _OptimizedParserMixin
):
    def _parse_data(
        self, data: memoryview, entity_id: KBEEntityId
    ) -> tuple[OnUpdateData_XZ_YPR_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)

        value, offset = INT8.decode(data)
        data = data[offset:]
        yaw = kbemath.int82angle(value)

        value, offset = INT8.decode(data)
        data = data[offset:]
        pitch = kbemath.int82angle(value)

        value, offset = INT8.decode(data)
        data = data[offset:]
        roll = kbemath.int82angle(value)

        pd = OnUpdateData_XZ_YPR_OptimizedParsedMsgData(
            v2.x, v2.y, yaw, pitch, roll
        )
        return pd, data

    def _process_parsed_data(
        self,
        pd: OnUpdateData_XZ_YPR_OptimizedParsedMsgData,
        entity_id: KBEEntityId,
    ) -> OnUpdateData_XZ_YPR_OptimizedMsgParserResult:
        # [2026-02-21 16:19 burov_alexey@mail.ru]:
        # Побочный эффект
        # pose_data = _PosAndDirData(
        #     **{f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)}
        # )
        # self.set_pose(entity_id, pose_data)
        return OnUpdateData_XZ_YPR_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XZ_YP_OptimizedParsedMsgData(_EntityParsedMsgData):
    x: float
    z: float
    yaw: float
    pitch: float


@dataclass(frozen=True)
class OnUpdateData_XZ_YP_OptimizedMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateData_XZ_YP_OptimizedParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xz_yp_optimized.id


class OnUpdateData_XZ_YP_OptimizedParser(
    _EntityMsgParser, _OptimizedParserMixin
):
    def _parse_data(
        self, data: memoryview, entity_id: KBEEntityId
    ) -> tuple[OnUpdateData_XZ_YP_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)

        value, offset = INT8.decode(data)
        data = data[offset:]
        yaw = kbemath.int82angle(value)

        value, offset = INT8.decode(data)
        data = data[offset:]
        pitch = kbemath.int82angle(value)

        pd = OnUpdateData_XZ_YP_OptimizedParsedMsgData(v2.x, v2.y, yaw, pitch)
        return pd, data

    def _process_parsed_data(
        self,
        pd: OnUpdateData_XZ_YP_OptimizedParsedMsgData,
        entity_id: KBEEntityId,
    ) -> OnUpdateData_XZ_YP_OptimizedMsgParserResult:
        # [2026-02-21 16:19 burov_alexey@mail.ru]:
        # Побочный эффект
        # pose_data = _PosAndDirData(
        #     **{f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)}
        # )
        # self.set_pose(entity_id, pose_data)
        return OnUpdateData_XZ_YP_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XZ_YR_OptimizedParsedMsgData(_EntityParsedMsgData):
    x: float
    z: float
    yaw: float
    roll: float


@dataclass(frozen=True)
class OnUpdateData_XZ_YR_OptimizedMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateData_XZ_YR_OptimizedParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xz_yr_optimized.id


class OnUpdateData_XZ_YR_OptimizedParser(
    _EntityMsgParser, _OptimizedParserMixin
):
    def _parse_data(
        self, data: memoryview, entity_id: KBEEntityId
    ) -> tuple[OnUpdateData_XZ_YR_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)

        value, offset = INT8.decode(data)
        data = data[offset:]
        yaw = kbemath.int82angle(value)

        value, offset = INT8.decode(data)
        data = data[offset:]
        roll = kbemath.int82angle(value)

        pd = OnUpdateData_XZ_YR_OptimizedParsedMsgData(v2.x, v2.y, yaw, roll)
        return pd, data

    def _process_parsed_data(
        self,
        pd: OnUpdateData_XZ_YR_OptimizedParsedMsgData,
        entity_id: KBEEntityId,
    ) -> OnUpdateData_XZ_YR_OptimizedMsgParserResult:
        # [2026-02-21 16:19 burov_alexey@mail.ru]:
        # Побочный эффект
        # pose_data = _PosAndDirData(
        #     **{f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)}
        # )
        # self.set_pose(entity_id, pose_data)
        return OnUpdateData_XZ_YR_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XZ_PR_OptimizedParsedMsgData(_EntityParsedMsgData):
    x: float
    z: float
    pitch: float
    roll: float


@dataclass(frozen=True)
class OnUpdateData_XZ_PR_OptimizedMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateData_XZ_PR_OptimizedParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xz_pr_optimized.id


class OnUpdateData_XZ_PR_OptimizedParser(
    _EntityMsgParser, _OptimizedParserMixin
):
    def _parse_data(
        self, data: memoryview, entity_id: KBEEntityId
    ) -> tuple[OnUpdateData_XZ_PR_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)

        value, offset = INT8.decode(data)
        data = data[offset:]
        pitch = kbemath.int82angle(value)

        value, offset = INT8.decode(data)
        data = data[offset:]
        roll = kbemath.int82angle(value)

        pd = OnUpdateData_XZ_PR_OptimizedParsedMsgData(v2.x, v2.y, pitch, roll)
        return pd, data

    def _process_parsed_data(
        self,
        pd: OnUpdateData_XZ_PR_OptimizedParsedMsgData,
        entity_id: KBEEntityId,
    ) -> OnUpdateData_XZ_PR_OptimizedMsgParserResult:
        # [2026-02-21 16:19 burov_alexey@mail.ru]:
        # Побочный эффект
        # pose_data = _PosAndDirData(
        #     **{f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)}
        # )
        # self.set_pose(entity_id, pose_data)
        return OnUpdateData_XZ_PR_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XZ_Y_OptimizedParsedMsgData(_EntityParsedMsgData):
    x: float
    z: float
    yaw: float


@dataclass(frozen=True)
class OnUpdateData_XZ_Y_OptimizedMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateData_XZ_Y_OptimizedParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xz_y_optimized.id


class OnUpdateData_XZ_Y_OptimizedParser(
    _EntityMsgParser, _OptimizedParserMixin
):
    def _parse_data(
        self, data: memoryview, entity_id: KBEEntityId
    ) -> tuple[OnUpdateData_XZ_Y_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)

        value, offset = INT8.decode(data)
        data = data[offset:]
        yaw = kbemath.int82angle(value)

        pd = OnUpdateData_XZ_Y_OptimizedParsedMsgData(v2.x, v2.y, yaw)
        return pd, data

    def _process_parsed_data(
        self,
        pd: OnUpdateData_XZ_Y_OptimizedParsedMsgData,
        entity_id: KBEEntityId,
    ) -> OnUpdateData_XZ_Y_OptimizedMsgParserResult:
        # [2026-02-21 16:19 burov_alexey@mail.ru]:
        # Побочный эффект
        # pose_data = _PosAndDirData(
        #     **{f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)}
        # )
        # self.set_pose(entity_id, pose_data)
        return OnUpdateData_XZ_Y_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XZ_P_OptimizedParsedMsgData(_EntityParsedMsgData):
    x: float
    z: float
    pitch: float


@dataclass(frozen=True)
class OnUpdateData_XZ_P_OptimizedMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateData_XZ_P_OptimizedParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xz_p_optimized.id


class OnUpdateData_XZ_P_OptimizedParser(
    _EntityMsgParser, _OptimizedParserMixin
):
    def _parse_data(
        self, data: memoryview, entity_id: KBEEntityId
    ) -> tuple[OnUpdateData_XZ_P_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)

        value, offset = INT8.decode(data)
        data = data[offset:]
        pitch = kbemath.int82angle(value)

        pd = OnUpdateData_XZ_P_OptimizedParsedMsgData(v2.x, v2.y, pitch)
        return pd, data

    def _process_parsed_data(
        self,
        pd: OnUpdateData_XZ_P_OptimizedParsedMsgData,
        entity_id: KBEEntityId,
    ) -> OnUpdateData_XZ_P_OptimizedMsgParserResult:
        # [2026-02-21 16:19 burov_alexey@mail.ru]:
        # Побочный эффект
        # pose_data = _PosAndDirData(
        #     **{f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)}
        # )
        # self.set_pose(entity_id, pose_data)
        return OnUpdateData_XZ_P_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XZ_R_OptimizedParsedMsgData(_EntityParsedMsgData):
    x: float
    z: float
    roll: float


@dataclass(frozen=True)
class OnUpdateData_XZ_R_OptimizedMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateData_XZ_R_OptimizedParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xz_r_optimized.id


class OnUpdateData_XZ_R_OptimizedParser(
    _EntityMsgParser, _OptimizedParserMixin
):
    def _parse_data(
        self, data: memoryview, entity_id: KBEEntityId
    ) -> tuple[OnUpdateData_XZ_R_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)

        value, offset = INT8.decode(data)
        data = data[offset:]
        roll = kbemath.int82angle(value)

        pd: OnUpdateData_XZ_R_OptimizedParsedMsgData = (
            OnUpdateData_XZ_R_OptimizedParsedMsgData(v2.x, v2.y, roll)
        )
        return pd, data

    def _process_parsed_data(
        self,
        pd: OnUpdateData_XZ_R_OptimizedParsedMsgData,
        entity_id: KBEEntityId,
    ) -> OnUpdateData_XZ_R_OptimizedMsgParserResult:
        # [2026-02-21 16:19 burov_alexey@mail.ru]:
        # Побочный эффект
        # pose_data = _PosAndDirData(
        #     **{f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)}
        # )
        # self.set_pose(entity_id, pose_data)
        return OnUpdateData_XZ_R_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XYZ_OptimizedParsedMsgData(_EntityParsedMsgData):
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class OnUpdateData_XYZ_OptimizedMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateData_XYZ_OptimizedParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xyz_optimized.id


class OnUpdateData_XYZ_OptimizedParser(_EntityMsgParser, _OptimizedParserMixin):
    def _parse_data(
        self, data: memoryview, entity_id: KBEEntityId
    ) -> tuple[OnUpdateData_XYZ_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)
        y, data = _OptimizedXYZReader.read_packed_y(data)
        pd = OnUpdateData_XYZ_OptimizedParsedMsgData(v2.x, y, v2.y)
        return pd, data

    def _process_parsed_data(
        self,
        pd: OnUpdateData_XYZ_OptimizedParsedMsgData,
        entity_id: KBEEntityId,
    ) -> OnUpdateData_XYZ_OptimizedMsgParserResult:
        # [2026-02-21 16:19 burov_alexey@mail.ru]:
        # Побочный эффект
        # pose_data = _PosAndDirData(x=pd.x, y=pd.y, z=pd.z)
        # self.set_pose(entity_id, pose_data)
        return OnUpdateData_XYZ_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XYZ_YPR_OptimizedParsedMsgData(_EntityParsedMsgData):
    x: float
    y: float
    z: float
    yaw: float
    pitch: float
    roll: float


@dataclass(frozen=True)
class OnUpdateData_XYZ_YPR_OptimizedMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateData_XYZ_YPR_OptimizedParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xyz_ypr_optimized.id


class OnUpdateData_XYZ_YPR_OptimizedParser(
    _EntityMsgParser, _OptimizedParserMixin
):
    def _parse_data(
        self, data: memoryview, entity_id: KBEEntityId
    ) -> tuple[OnUpdateData_XYZ_YPR_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)
        y, data = _OptimizedXYZReader.read_packed_y(data)

        value, offset = INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)

        value, offset = INT8.decode(data)
        data = data[offset:]
        angle_2 = kbemath.int82angle(value)

        value, offset = INT8.decode(data)
        data = data[offset:]
        angle_3 = kbemath.int82angle(value)

        pd = OnUpdateData_XYZ_YPR_OptimizedParsedMsgData(
            v2.x, y, v2.y, angle_1, angle_2, angle_3
        )
        return pd, data

    def _process_parsed_data(
        self,
        pd: OnUpdateData_XYZ_YPR_OptimizedParsedMsgData,
        entity_id: KBEEntityId,
    ) -> OnUpdateData_XYZ_YPR_OptimizedMsgParserResult:
        # [2026-02-21 16:19 burov_alexey@mail.ru]:
        # Побочный эффект
        # pose_data = _PosAndDirData(
        #     **{f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)}
        # )
        # self.set_pose(entity_id, pose_data)
        return OnUpdateData_XYZ_YPR_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XYZ_YP_OptimizedParsedMsgData(_EntityParsedMsgData):
    x: float
    y: float
    z: float
    yaw: float
    pitch: float


@dataclass(frozen=True)
class OnUpdateData_XYZ_YP_OptimizedMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateData_XYZ_YP_OptimizedParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xyz_yp_optimized.id


class OnUpdateData_XYZ_YP_OptimizedParser(
    _EntityMsgParser, _OptimizedParserMixin
):
    def _parse_data(
        self, data: memoryview, entity_id: KBEEntityId
    ) -> tuple[OnUpdateData_XYZ_YP_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)
        y, data = _OptimizedXYZReader.read_packed_y(data)

        value, offset = INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)

        value, offset = INT8.decode(data)
        data = data[offset:]
        angle_2 = kbemath.int82angle(value)

        pd = OnUpdateData_XYZ_YP_OptimizedParsedMsgData(
            v2.x, y, v2.y, angle_1, angle_2
        )
        return pd, data

    def _process_parsed_data(
        self,
        pd: OnUpdateData_XYZ_YP_OptimizedParsedMsgData,
        entity_id: KBEEntityId,
    ) -> OnUpdateData_XYZ_YP_OptimizedMsgParserResult:
        # [2026-02-21 16:19 burov_alexey@mail.ru]:
        # Побочный эффект
        # pose_data = _PosAndDirData(
        #     **{f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)}
        # )
        # self.set_pose(entity_id, pose_data)
        return OnUpdateData_XYZ_YP_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XYZ_YR_OptimizedParsedMsgData(_EntityParsedMsgData):
    x: float
    y: float
    z: float
    yaw: float
    roll: float


@dataclass(frozen=True)
class OnUpdateData_XYZ_YR_OptimizedMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateData_XYZ_YR_OptimizedParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xyz_yr_optimized.id


class OnUpdateData_XYZ_YR_OptimizedParser(
    _EntityMsgParser, _OptimizedParserMixin
):
    def _parse_data(
        self, data: memoryview, entity_id: KBEEntityId
    ) -> tuple[OnUpdateData_XYZ_YR_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)
        y, data = _OptimizedXYZReader.read_packed_y(data)

        value, offset = INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)

        value, offset = INT8.decode(data)
        data = data[offset:]
        angle_2 = kbemath.int82angle(value)

        pd = OnUpdateData_XYZ_YR_OptimizedParsedMsgData(
            v2.x, y, v2.y, angle_1, angle_2
        )
        return pd, data

    def _process_parsed_data(
        self,
        pd: OnUpdateData_XYZ_YR_OptimizedParsedMsgData,
        entity_id: KBEEntityId,
    ) -> OnUpdateData_XYZ_YR_OptimizedMsgParserResult:
        # [2026-02-21 16:19 burov_alexey@mail.ru]:
        # Побочный эффект
        # pose_data = _PosAndDirData(
        #     **{f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)}
        # )
        # self.set_pose(entity_id, pose_data)
        return OnUpdateData_XYZ_YR_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XYZ_PR_OptimizedParsedMsgData(_EntityParsedMsgData):
    x: float
    y: float
    z: float
    pitch: float
    roll: float


@dataclass(frozen=True)
class OnUpdateData_XYZ_PR_OptimizedMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateData_XYZ_PR_OptimizedParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xyz_pr_optimized.id


class OnUpdateData_XYZ_PR_OptimizedParser(
    _EntityMsgParser, _OptimizedParserMixin
):
    def _parse_data(
        self, data: memoryview, entity_id: KBEEntityId
    ) -> tuple[OnUpdateData_XYZ_PR_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)
        y, data = _OptimizedXYZReader.read_packed_y(data)

        value, offset = INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)

        value, offset = INT8.decode(data)
        data = data[offset:]
        angle_2 = kbemath.int82angle(value)

        pd = OnUpdateData_XYZ_PR_OptimizedParsedMsgData(
            v2.x, y, v2.y, angle_1, angle_2
        )
        return pd, data

    def _process_parsed_data(
        self,
        pd: OnUpdateData_XYZ_PR_OptimizedParsedMsgData,
        entity_id: KBEEntityId,
    ) -> OnUpdateData_XYZ_PR_OptimizedMsgParserResult:
        # [2026-02-21 16:19 burov_alexey@mail.ru]:
        # Побочный эффект
        # pose_data = _PosAndDirData(
        #     **{f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)}
        # )
        # self.set_pose(entity_id, pose_data)
        return OnUpdateData_XYZ_PR_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XYZ_Y_OptimizedParsedMsgData(_EntityParsedMsgData):
    x: float
    y: float
    z: float
    yaw: float


@dataclass(frozen=True)
class OnUpdateData_XYZ_Y_OptimizedMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateData_XYZ_Y_OptimizedParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xyz_y_optimized.id


class OnUpdateData_XYZ_Y_OptimizedParser(
    _EntityMsgParser, _OptimizedParserMixin
):
    def _parse_data(
        self, data: memoryview, entity_id: KBEEntityId
    ) -> tuple[OnUpdateData_XYZ_Y_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)
        y, data = _OptimizedXYZReader.read_packed_y(data)

        value, offset = INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)

        pd = OnUpdateData_XYZ_Y_OptimizedParsedMsgData(v2.x, y, v2.y, angle_1)
        return pd, data

    def _process_parsed_data(
        self,
        pd: OnUpdateData_XYZ_Y_OptimizedParsedMsgData,
        entity_id: KBEEntityId,
    ) -> OnUpdateData_XYZ_Y_OptimizedMsgParserResult:
        # [2026-02-21 16:19 burov_alexey@mail.ru]:
        # Побочный эффект
        # pose_data = _PosAndDirData(
        #     **{f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)}
        # )
        # self.set_pose(entity_id, pose_data)
        return OnUpdateData_XYZ_Y_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XYZ_P_OptimizedParsedMsgData(_EntityParsedMsgData):
    x: float
    y: float
    z: float
    pitch: float


@dataclass(frozen=True)
class OnUpdateData_XYZ_P_OptimizedMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateData_XYZ_P_OptimizedParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xyz_p_optimized.id


class OnUpdateData_XYZ_P_OptimizedParser(
    _EntityMsgParser, _OptimizedParserMixin
):
    def _parse_data(
        self, data: memoryview, entity_id: KBEEntityId
    ) -> tuple[OnUpdateData_XYZ_P_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)
        y, data = _OptimizedXYZReader.read_packed_y(data)

        value, offset = INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)

        pd = OnUpdateData_XYZ_P_OptimizedParsedMsgData(v2.x, y, v2.y, angle_1)
        return pd, data

    def _process_parsed_data(
        self,
        pd: OnUpdateData_XYZ_P_OptimizedParsedMsgData,
        entity_id: KBEEntityId,
    ) -> OnUpdateData_XYZ_P_OptimizedMsgParserResult:
        # [2026-02-21 16:19 burov_alexey@mail.ru]:
        # Побочный эффект
        # pose_data = _PosAndDirData(
        #     **{f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)}
        # )
        # self.set_pose(entity_id, pose_data)
        return OnUpdateData_XYZ_P_OptimizedMsgParserResult(True, pd)


@dataclass
class OnUpdateData_XYZ_R_OptimizedParsedMsgData(_EntityParsedMsgData):
    x: float
    y: float
    z: float
    roll: float


@dataclass(frozen=True)
class OnUpdateData_XYZ_R_OptimizedMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnUpdateData_XYZ_R_OptimizedParsedMsgData | None = None
    msg_id: int = msgspec.client.onUpdateData_xyz_r_optimized.id


class OnUpdateData_XYZ_R_OptimizedParser(
    _EntityMsgParser, _OptimizedParserMixin
):
    def _parse_data(
        self, data: memoryview, entity_id: KBEEntityId
    ) -> tuple[OnUpdateData_XYZ_R_OptimizedParsedMsgData, memoryview]:
        v2, data = _OptimizedXYZReader.read_packed_xz(data)
        y, data = _OptimizedXYZReader.read_packed_y(data)

        value, offset = INT8.decode(data)
        data = data[offset:]
        angle_1 = kbemath.int82angle(value)

        pd = OnUpdateData_XYZ_R_OptimizedParsedMsgData(v2.x, y, v2.y, angle_1)
        return pd, data

    def _process_parsed_data(
        self,
        pd: OnUpdateData_XYZ_R_OptimizedParsedMsgData,
        entity_id: KBEEntityId,
    ) -> OnUpdateData_XYZ_R_OptimizedMsgParserResult:
        # [2026-02-21 16:19 burov_alexey@mail.ru]:
        # Побочный эффект
        # pose_data = _PosAndDirData(
        #     **{f.name: getattr(pd, f.name) for f in dataclasses.fields(pd)}
        # )
        # self.set_pose(entity_id, pose_data)
        return OnUpdateData_XYZ_R_OptimizedMsgParserResult(True, pd)


@dataclass
class OnControlEntityParsedMsgData(_EntityParsedMsgData):
    is_controlled: KBEBool


@dataclass(frozen=True)
class OnControlEntityMsgParserResult(_EntityMsgParserResult):
    success: bool
    result: OnControlEntityParsedMsgData | None = None
    msg_id: int = msgspec.client.onControlEntity.id
    text: str = ""


class OnControlEntityParser(_EntityMsgParser):
    def parse(self, msg: Message) -> OnControlEntityMsgParserResult:
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])
        _entity_id, data = self._get_entity_id(data)
        is_controlled, offset = BOOL.decode(data)
        data = data[offset:]
        # TODO: [2022-09-07 13:44 burov_alexey@mail.ru]:
        # I cannot find the server code that sends the "onControlEntity" message.
        # I think it's legacy code thats why I do nothin in this handler.
        return OnControlEntityMsgParserResult(
            True, OnControlEntityParsedMsgData(is_controlled)
        )


__all__ = [
    "OnControlEntityParser",
    "OnCreatedProxiesParser",
    "OnEntityDestroyedParser",
    "OnEntityEnterSpaceParser",
    "OnEntityEnterWorldParser",
    "OnEntityLeaveSpaceParser",
    "OnEntityLeaveWorldOptimizedParser",
    "OnEntityLeaveWorldParser",
    "OnRemoteMethodCallOptimizedParser",
    "OnRemoteMethodCallParser",
    "OnSetEntityPosAndDirParser",
    "OnUpdateBaseDirParser",
    "OnUpdateBasePosParser",
    "OnUpdateBasePosXZParser",
    "OnUpdateDataParser",
    "OnUpdateData_PR_OptimizedParser",
    "OnUpdateData_PR_Parser",
    "OnUpdateData_P_OptimizedParser",
    "OnUpdateData_P_Parser",
    "OnUpdateData_R_OptimizedParser",
    "OnUpdateData_R_Parser",
    "OnUpdateData_XYZ_OptimizedParser",
    "OnUpdateData_XYZ_PR_OptimizedParser",
    "OnUpdateData_XYZ_PR_Parser",
    "OnUpdateData_XYZ_P_OptimizedParser",
    "OnUpdateData_XYZ_P_Parser",
    "OnUpdateData_XYZ_Parser",
    "OnUpdateData_XYZ_R_OptimizedParser",
    "OnUpdateData_XYZ_R_Parser",
    "OnUpdateData_XYZ_YPR_OptimizedParser",
    "OnUpdateData_XYZ_YPR_Parser",
    "OnUpdateData_XYZ_YP_OptimizedParser",
    "OnUpdateData_XYZ_YP_Parser",
    "OnUpdateData_XYZ_YR_OptimizedParser",
    "OnUpdateData_XYZ_YR_Parser",
    "OnUpdateData_XYZ_Y_OptimizedParser",
    "OnUpdateData_XYZ_Y_Parser",
    "OnUpdateData_XZ_OptimizedParser",
    "OnUpdateData_XZ_PR_OptimizedParser",
    "OnUpdateData_XZ_PR_Parser",
    "OnUpdateData_XZ_P_OptimizedParser",
    "OnUpdateData_XZ_P_Parser",
    "OnUpdateData_XZ_Parser",
    "OnUpdateData_XZ_R_OptimizedParser",
    "OnUpdateData_XZ_R_Parser",
    "OnUpdateData_XZ_YPR_OptimizedParser",
    "OnUpdateData_XZ_YPR_Parser",
    "OnUpdateData_XZ_YP_OptimizedParser",
    "OnUpdateData_XZ_YP_Parser",
    "OnUpdateData_XZ_YR_OptimizedParser",
    "OnUpdateData_XZ_YR_Parser",
    "OnUpdateData_XZ_Y_OptimizedParser",
    "OnUpdateData_XZ_Y_Parser",
    "OnUpdateData_YPR_OptimizedParser",
    "OnUpdateData_YPR_Parser",
    "OnUpdateData_YP_OptimizedParser",
    "OnUpdateData_YP_Parser",
    "OnUpdateData_YR_OptimizedParser",
    "OnUpdateData_YR_Parser",
    "OnUpdateData_Y_OptimizedParser",
    "OnUpdateData_Y_Parser",
    "OnUpdatePropertysMsgParser",
    "OnUpdatePropertysOptimizedParser",
]
