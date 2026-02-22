"""Модуль содержит общие парсеры или его результаты для всех сообщений KBEngine."""

from __future__ import annotations

import logging
import typing
from dataclasses import dataclass
from typing import Any, ClassVar

from enki import msgspec
from enki.kbeenum import (
    COMPONENT_STATE_BY_SHUTDOWN_STATE,
    ComponentState,
    ComponentType,
    ShutdownState,
)
from enki.kbetype.decoders.basic_data_type_decoders import BOOL, STRING, UINT32
from enki.kbetype.decoders.custom_decoders import (
    CALLBACK_ID,
    COMPONENT_ID,
    ENTITY_ID,
    SPACE_ID,
    KBECallbackId,
    KBEComponentId,
    KBEComponentOrderId,
    KBEComponentType,
    KBEEntityId,
    KBEEntityTypeName,
    KBEExtAddrEx,
    KBEGameTime,
    KBEIntAddr,
    KBEIntPort,
    KBEShutdownState,
    KBESpaceId,
    KBEUid_,
    KBEUsername,
)
from enki.misc import devonly
from enki.msg_parser import kbemath
from enki.net.addr import Addr, Port

from .imsg_parser import IMsgParser, MsgParserResult, ParsedMsgData
from .kbepickle import pickle_global_data_value

if typing.TYPE_CHECKING:
    from enki.kbetype.ikbetype import IKBEType
    from enki.kbetype.pytypes.basic_data_types import (
        KBEBool,
        KBERowByteData,
        KBEString,
    )
    from enki.msg.message import Message

logger = logging.getLogger(__name__)


@dataclass
class OnRegisterNewAppParsedMsgData(ParsedMsgData):
    """Данные сообщения ::onRegisterNewApp.

    Поля сообщения одинаковые для всех компонентов KBEngine.
    """

    uid: KBEUid_
    username: KBEUsername
    componentType: KBEComponentType  # pylint: disable=invalid-name
    componentID: KBEComponentId  # noqa: N815  # pylint: disable=invalid-name
    globalorderID: KBEComponentOrderId  # pylint: disable=invalid-name
    grouporderID: KBEComponentOrderId  # pylint: disable=invalid-name
    intaddr: KBEIntAddr
    intport: KBEIntPort
    extaddr: KBEIntAddr
    extport: KBEIntPort
    extaddrEx: KBEExtAddrEx  # noqa: N815  # pylint: disable=invalid-name

    @property
    def component_type(self) -> ComponentType:
        """Возвращает тип компонента в виде enum ComponentType.

        Returns:
            ComponentType: Тип компонента

        """
        return ComponentType(self.componentType)

    @property
    def internal_address(self) -> Addr:
        """Возвращает внутренний адрес в виде объекта Addr.

        Returns:
            Addr: Объект с host и port внутреннего адреса

        """
        return Addr(
            kbemath.int2ip(self.intaddr), Port(kbemath.int2port(self.intport))
        )

    @property
    def external_address(self) -> Addr:
        """Возвращает внешний адрес в виде объекта Addr.

        Returns:
            Addr: Объект с host и port внешнего адреса

        """
        return Addr(
            kbemath.int2ip(self.extaddr), Port(kbemath.int2port(self.extport))
        )

    __add_to_dict__: ClassVar = (
        "component_type",
        "internal_address",
        "external_address",
    )


@dataclass
class OnAppActiveTickParsedMsgData(ParsedMsgData):
    """Данные сообщения ::onAppActiveTick."""

    componentType: KBEComponentType  # pylint: disable=invalid-name
    componentID: KBEComponentId  # noqa: N815  # pylint: disable=invalid-name

    @property
    def component_type(self) -> ComponentType:
        """Возвращает тип компонента в виде enum ComponentType.

        Returns:
            ComponentType: Тип компонента

        """
        return ComponentType(self.componentType)

    @property
    def component_id(self) -> KBEComponentId:
        """Id компонента ("--cid" в строке запуска компонента).

        Returns:
            KBEComponentId: id компонента

        """
        return self.componentID

    __add_to_dict__: ClassVar = (
        "component_type",
        "component_id",
    )


@dataclass
class OnLookAppParsedMsgData(ParsedMsgData):
    """Данные сообщения ::onLookApp."""

    componentType: KBEComponentType  # pylint: disable=invalid-name
    componentID: KBEComponentId  # noqa: N815  # pylint: disable=invalid-name
    shutdownState: KBEShutdownState  # pylint: disable=invalid-name

    @property
    def component_type(self) -> ComponentType:
        """Возвращает тип компонента в виде enum ComponentType.

        Returns:
            ComponentType: Тип компонента

        """
        return ComponentType(self.componentType)

    @property
    def component_id(self) -> KBEComponentId:
        """Id компонента ("--cid" в строке запуска компонента).

        Returns:
            KBEComponentId: id компонента

        """
        return self.componentID

    @property
    def component_state(self) -> ComponentState:
        """Возвращает состояние компонента.

        Returns:
            ComponentType: Тип текущего компонента

        """
        return COMPONENT_STATE_BY_SHUTDOWN_STATE[
            ShutdownState(self.shutdownState)
        ]

    __add_to_dict__: ClassVar = (
        "component_type",
        "component_state",
    )


@dataclass
class LookAppParsedMsgData(ParsedMsgData):
    """Данные сообщения ::lookApp.

    У сообщения нет данных, поэтому и dataclass пустой.
    """


@dataclass
class CreateEntityAnywhereParsedMsgData(ParsedMsgData):
    """Данные сообщения (стрима) ::reqCreateEntityAnywhere."""

    entityType: KBEString  # noqa: N815  # pylint: disable=invalid-name
    initDataLength: int  # noqa: N815  # pylint: disable=invalid-name
    params: dict
    componentID: KBEComponentId  # noqa: N815  # pylint: disable=invalid-name
    callbackID: KBECallbackId  # noqa: N815  # pylint: disable=invalid-name

    @property
    def baseapp_component_id(self) -> KBEComponentId:
        """Поле нужно для документации, что оно означает."""
        return self.componentID

    __add_to_dict__: ClassVar = ("baseapp_component_id",)


@dataclass(frozen=True)
class CreateEntityAnywhereMsgParserResult(MsgParserResult):
    """Парсер для ::reqCreateEntityAnywhere."""

    success: bool
    result: CreateEntityAnywhereParsedMsgData | None = None
    msg_id: int = msgspec.baseappmgr.reqCreateEntityAnywhere.id
    text: str = ""


class CreateEntityAnywhereMsgParser(IMsgParser):
    """Парсер сообщения ::reqCreateEntityAnywhere."""

    def parse(self, msg: Message) -> CreateEntityAnywhereMsgParserResult:
        """Распарсить сообщение ::reqCreateEntityAnywhere.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            ReqCreateEntityAnywhereParsedMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[IKBEType, ...] = msg.get_values()
        if len(values) != 1:
            return CreateEntityAnywhereMsgParserResult(success=False)

        value: KBERowByteData = typing.cast("KBERowByteData", values[0])
        data = memoryview(value)

        entity_type, offset = STRING.decode(data)
        data = data[offset:]

        data_length, offset = UINT32.decode(data)
        data = data[offset:]

        dct: dict = {}
        if data_length != 0:
            d = data[:data_length]
            data = data[data_length:]
            dct = pickle_global_data_value(d)

        component_id, offset = COMPONENT_ID.decode(data)
        data = data[offset:]
        callback_id, offset = CALLBACK_ID.decode(data)
        data = data[offset:]

        assert not data, "Not all data parsed"

        pd = CreateEntityAnywhereParsedMsgData(
            entity_type, data_length, dct, component_id, callback_id
        )
        return CreateEntityAnywhereMsgParserResult(success=True, result=pd)


@dataclass
class OnGetEntityAppFromDbmgrParsedMsgData(ParsedMsgData):
    """Данные сообщения ::onGetEntityAppFromDbmgr."""

    uid: KBEUid_
    username: KBEUsername
    componentType: KBEComponentType  # pylint: disable=invalid-name
    componentID: KBEComponentId  # noqa: N815  # pylint: disable=invalid-name
    globalorderID: KBEComponentOrderId  # pylint: disable=invalid-name
    grouporderID: KBEComponentOrderId  # pylint: disable=invalid-name
    intaddr: KBEIntAddr
    intport: KBEIntPort
    extaddr: KBEIntAddr
    extport: KBEIntPort
    extaddrEx: KBEExtAddrEx  # noqa: N815  # pylint: disable=invalid-name

    @property
    def component_type(self) -> ComponentType:
        """Возвращает тип компонента в виде enum ComponentType.

        Returns:
            ComponentType: Тип компонента

        """
        return ComponentType(self.componentType)

    @property
    def internal_address(self) -> Addr:
        """Возвращает внутренний адрес в виде объекта Addr.

        Returns:
            Addr: Объект с host и port внутреннего адреса

        """
        return Addr(
            kbemath.int2ip(self.intaddr), Port(kbemath.int2port(self.intport))
        )

    @property
    def external_address(self) -> Addr:
        """Возвращает внешний адрес в виде объекта Addr.

        Returns:
            Addr: Объект с host и port внешнего адреса

        """
        return Addr(
            kbemath.int2ip(self.extaddr), Port(kbemath.int2port(self.extport))
        )

    __add_to_dict__: ClassVar = (
        "component_type",
        "internal_address",
        "external_address",
    )


@dataclass
class OnDbmgrInitCompletedParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения ::onDbmgrInitCompleted.

    Сообщение ::onDbmgrInitCompleted отправляется компонентам от DBMgr в ответ
    на Dbmgr::onRegisterNewApp.
    """

    gametime: KBEGameTime
    startID: KBEEntityId  # noqa: N815  # pylint: disable=invalid-name
    endID: KBEEntityId  # noqa: N815  # pylint: disable=invalid-name
    startGlobalOrder: KBEComponentOrderId  # pylint: disable=invalid-name
    startGroupOrder: KBEComponentOrderId  # pylint: disable=invalid-name
    digest: KBEString


@dataclass
class ReqCloseServerParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения ::reqCloseServer."""


# TODO: [2025-08-11 11:30 burov_alexey@mail.ru]:
# Я не понял, что с этим сообщением. Нужно уже вылавливать во время тестов будет.
@dataclass
class CreateCellEntityInNewSpaceFromBaseappParsedMsgData(ParsedMsgData):
    """Распарсенное сообщение ::reqCreateCellEntityInNewSpaceFromBaseapp.

    Это данные стрима.
    """

    entityType: KBEEntityTypeName
    entitycallEntityID: KBEEntityId
    componentID: KBEComponentId
    spaceID: KBESpaceId
    hasClient: KBEBool
    cellData: bytes = b""


class CreateCellEntityInNewSpaceFromBaseappParser:
    def parse(
        self, msg: Message
    ) -> CreateCellEntityInNewSpaceFromBaseappParsedMsgData:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])
        entity_type, offset = STRING.decode(data)
        data = data[offset:]
        entity_id, offset = ENTITY_ID.decode(data)
        data = data[offset:]
        component_id, offset = COMPONENT_ID.decode(data)
        data = data[offset:]
        space_id, offset = SPACE_ID.decode(data)
        data = data[offset:]
        has_client, offset = BOOL.decode(data)
        data = data[offset:]

        return CreateCellEntityInNewSpaceFromBaseappParsedMsgData(
            entity_type,
            entity_id,
            component_id,
            space_id,
            has_client,
            data.tobytes(),
        )
