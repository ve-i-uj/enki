"""Парсер сообщений от компонента BaseappMgr."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar

from enki import msgspec
from enki.core import kbemath
from enki.kbeenum import (
    COMPONENT_STATE_BY_SHUTDOWN_STATE,
    ClientType,
    ComponentState,
    ComponentType,
    ShutdownState,
)
from enki.misc import devonly
from enki.msg_parser.common import (
    CreateEntityAnywhereMsgParser,
    CreateEntityAnywhereParsedMsgData,
    OnAppActiveTickParsedMsgData,
    OnRegisterNewAppParsedMsgData,
)
from enki.net.addr import Addr, Port

from .imsg_parser import IMsgParser, MsgParserResult, ParsedMsgData

if TYPE_CHECKING:
    from enki.kbetype.decoders.custom_decoders import (
        KBEComponentId,
        KBEComponentType,
        KBEDbid,
        KBEShutdownState,
    )
    from enki.kbetype.pytypes.basic_data_types import (
        KBEBool,
        KBEInt8,
        KBEInt32,
        KBERowByteData,
        KBEString,
        KBEUInt16,
        KBEUInt32,
        KBEUInt64,
    )
    from enki.msg.message import Message

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OnAppActiveTickMsgParserResult(MsgParserResult):
    """Результат парсинга BaseappMgr::onAppActiveTick."""

    success: bool
    result: OnAppActiveTickParsedMsgData
    msg_id: int = msgspec.baseappmgr.onAppActiveTick.id
    text: str = ""


class OnAppActiveTickMsgParser(IMsgParser):
    """Парсер для BaseappMgr::onAppActiveTick."""

    def parse(self, msg: Message) -> OnAppActiveTickMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnAppActiveTickParsedMsgData(*values)
        return OnAppActiveTickMsgParserResult(True, pd)


@dataclass(frozen=True)
class OnRegisterNewAppMsgParserResult(MsgParserResult):
    """Результат парсинга BaseappMgr::onRegisterNewApp."""

    success: bool
    result: OnRegisterNewAppParsedMsgData
    msg_id: int = msgspec.baseappmgr.onRegisterNewApp.id
    text: str = ""


class OnRegisterNewAppMsgParser(IMsgParser):
    """Парсер BaseappMgr::onRegisterNewApp."""

    def parse(self, msg: Message) -> OnRegisterNewAppMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnRegisterNewAppParsedMsgData(*values)
        return OnRegisterNewAppMsgParserResult(True, pd)


@dataclass
class UpdateBaseappParsedMsgData(ParsedMsgData):
    componentID: KBEComponentId  # noqa: N815  # pylint: disable=invalid-name
    numBases: int  # noqa: N815  # pylint: disable=invalid-name
    numProxices: int  # noqa: N815  # pylint: disable=invalid-name
    load: float
    flags: int


@dataclass(frozen=True)
class UpdateBaseappMsgParserResult(MsgParserResult):
    """Парсер для BaseappMgr::updateBaseapp."""

    success: bool
    result: UpdateBaseappParsedMsgData
    msg_id: int = msgspec.baseappmgr.updateBaseapp.id
    text: str = ""


class UpdateBaseappMsgParser(IMsgParser):
    """Парсер для BaseappMgr::updateBaseapp."""

    def parse(self, msg: Message) -> UpdateBaseappMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = UpdateBaseappParsedMsgData(*values)
        return UpdateBaseappMsgParserResult(True, pd)


@dataclass
class OnBaseappInitProgressParsedMsgData(ParsedMsgData):
    cid: int
    flags: int


@dataclass(frozen=True)
class OnBaseappInitProgressMsgParserResult(MsgParserResult):
    """Парсер для BaseappMgr::onBaseappInitProgress."""

    success: bool
    result: OnBaseappInitProgressParsedMsgData
    msg_id: int = msgspec.baseappmgr.onBaseappInitProgress.id
    text: str = ""


class OnBaseappInitProgressMsgParser(IMsgParser):
    def parse(self, msg: Message) -> OnBaseappInitProgressMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnBaseappInitProgressParsedMsgData(*values)
        return OnBaseappInitProgressMsgParserResult(True, pd)


@dataclass(frozen=True)
class ReqCreateEntityAnywhereMsgParserResult(MsgParserResult):
    """Парсер для BaseappMgr::reqCreateEntityAnywhere."""

    success: bool
    result: CreateEntityAnywhereParsedMsgData | None
    msg_id: int = msgspec.baseappmgr.reqCreateEntityAnywhere.id
    text: str = ""


class ReqCreateEntityAnywhereMsgParser(IMsgParser):
    """Парсер для BaseappMgr::reqCreateEntityAnywhere."""

    def parse(self, msg: Message) -> ReqCreateEntityAnywhereMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        result = CreateEntityAnywhereMsgParser().parse(msg)
        return ReqCreateEntityAnywhereMsgParserResult(
            success=result.success, result=result.result, text=result.text
        )


@dataclass
class OnPendingAccountGetBaseappAddrParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения BaseappMgr::onPendingAccountGetBaseappAddr."""

    loginName: KBEString  # noqa: N815  # pylint: disable=invalid-name
    accountName: KBEString  # noqa: N815  # pylint: disable=invalid-name
    addr: KBEString
    tcp_port: KBEUInt16
    udp_port: KBEUInt16

    @property
    def external_baseapp_tcp_address(self) -> Addr:
        """Возвращает внешний адрес в виде объекта Addr.

        Returns:
            Addr: Объект с host и port внешнего адреса

        """
        return Addr(self.addr, Port(kbemath.int2port(self.tcp_port)))

    @property
    def external_baseapp_udp_address(self) -> Addr:
        """Возвращает внешний адрес в виде объекта Addr.

        Returns:
            Addr: Объект с host и port внешнего адреса

        """
        return Addr(self.addr, Port(kbemath.int2port(self.udp_port)))

    __add_to_dict__: ClassVar[tuple[str, ...]] = (
        "external_baseapp_tcp_address",
        "external_baseapp_udp_address",
    )


@dataclass(frozen=True)
class OnPendingAccountGetBaseappAddrMsgParserResult(MsgParserResult):
    """Парсер для BaseappMgr::onPendingAccountGetBaseappAddr."""

    success: bool
    result: OnPendingAccountGetBaseappAddrParsedMsgData
    msg_id: int = msgspec.baseappmgr.onPendingAccountGetBaseappAddr.id
    text: str = ""


class OnPendingAccountGetBaseappAddrMsgParser(IMsgParser):
    """Парсер для BaseappMgr::onPendingAccountGetBaseappAddr."""

    def parse(
        self, msg: Message
    ) -> OnPendingAccountGetBaseappAddrMsgParserResult:
        """Распарсить сообщение BaseappMgr::onPendingAccountGetBaseappAddr.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnPendingAccountGetBaseappAddrParserMsgParserResult: объект
                результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnPendingAccountGetBaseappAddrParsedMsgData(*values)
        return OnPendingAccountGetBaseappAddrMsgParserResult(
            success=True, result=pd
        )


@dataclass
class RegisterPendingAccountToBaseappParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения BaseappMgr::registerPendingAccountToBaseapp."""

    login: KBEString
    account_name: KBEString
    password: KBEString
    needCheckPassword: KBEBool  # noqa: N815  # pylint: disable=invalid-name
    dbid: KBEDbid
    flags: KBEUInt32
    deadline: KBEUInt64
    clientType: KBEInt32  # noqa: N815  # pylint: disable=invalid-name
    forceInternalLogin: KBEBool  # noqa: N815  # pylint: disable=invalid-name
    datas: KBEString

    @property
    def client_type(self) -> ClientType:
        """Тип клиента.

        Returns:
            ClientType: тип клиента.

        """
        return ClientType(self.clientType)

    __add_to_dict__: ClassVar[tuple[str, ...]] = ("client_type",)


@dataclass(frozen=True)
class RegisterPendingAccountToBaseappMsgParserResult(MsgParserResult):
    """Парсер для BaseappMgr::registerPendingAccountToBaseapp."""

    success: bool
    result: RegisterPendingAccountToBaseappParsedMsgData
    msg_id: int = msgspec.baseappmgr.registerPendingAccountToBaseapp.id
    text: str = ""


class RegisterPendingAccountToBaseappMsgParser(IMsgParser):
    """Парсер для BaseappMgr::registerPendingAccountToBaseapp."""

    def parse(
        self, msg: Message
    ) -> RegisterPendingAccountToBaseappMsgParserResult:
        """Распарсить сообщение BaseappMgr::registerPendingAccountToBaseapp.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            RegisterPendingAccountToBaseappParserMsgParserResult: объект
                результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = RegisterPendingAccountToBaseappParsedMsgData(*values)
        return RegisterPendingAccountToBaseappMsgParserResult(
            success=True, result=pd
        )


@dataclass
class LookAppParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения BaseappMgr::lookApp."""


@dataclass(frozen=True)
class LookAppMsgParserResult(MsgParserResult):
    """Результат парсинга BaseappMgr::lookApp."""

    success: bool
    result: LookAppParsedMsgData
    msg_id: int = msgspec.baseappmgr.lookApp.id
    text: str = ""


class LookAppMsgParser(IMsgParser):
    """Парсер для BaseappMgr::lookApp."""

    def parse(self, msg: Message) -> LookAppMsgParserResult:
        """Распарсить сообщение BaseappMgr::lookApp.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            LookAppMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        pd = LookAppParsedMsgData(*values)
        return LookAppMsgParserResult(success=True, result=pd)


@dataclass
class OnLookAppParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения BaseappMgr::onLookApp."""

    componentType: KBEComponentType  # noqa: N815
    componentId: KBEComponentId  # noqa: N815
    shutdownState: KBEShutdownState  # noqa: N815

    @property
    def component_type(self) -> ComponentType:
        """Возвращает тип компонента в виде enum ComponentType.

        Returns:
            ComponentType: Тип текущего компонента

        """
        return ComponentType(self.componentType)

    @property
    def component_state(self) -> ComponentState:
        """Возвращает состояние компонента.

        Returns:
            ComponentType: Тип текущего компонента

        """
        return COMPONENT_STATE_BY_SHUTDOWN_STATE[
            ShutdownState(self.shutdownState)
        ]

    __add_to_dict__: ClassVar = ("component_type", "component_state")


@dataclass(frozen=True)
class OnLookAppParserMsgParserResult(MsgParserResult):
    """Парсер для BaseappMgr::onLookApp."""

    success: bool
    result: OnLookAppParsedMsgData
    msg_id: int = msgspec.baseappmgr.onLookApp.id
    text: str = ""


class OnLookAppMsgParser(IMsgParser):
    """Парсер для BaseappMgr::onLookApp."""

    def parse(self, msg: Message) -> OnLookAppParserMsgParserResult:
        """Распарсить сообщение BaseappMgr::onLookApp.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnLookAppParserMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnLookAppParsedMsgData(*values)
        return OnLookAppParserMsgParserResult(success=True, result=pd)


@dataclass
class QueryLoadParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения BaseappMgr::queryLoad."""


@dataclass(frozen=True)
class QueryLoadMsgParserResult(MsgParserResult):
    """Результат парсинга BaseappMgr::queryLoad."""

    success: bool
    result: QueryLoadParsedMsgData
    msg_id: int = msgspec.baseappmgr.queryLoad.id
    text: str = ""


class QueryLoadMsgParser(IMsgParser):
    """Парсер для BaseappMgr::queryLoad."""

    def parse(self, msg: Message) -> QueryLoadMsgParserResult:
        """Распарсить сообщение BaseappMgr::queryLoad."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = QueryLoadParsedMsgData(*values)
        return QueryLoadMsgParserResult(success=True, result=pd)


@dataclass
class ReqCreateEntityRemotelyParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения BaseappMgr::reqCreateEntityRemotely."""

    data: KBERowByteData


@dataclass(frozen=True)
class ReqCreateEntityRemotelyMsgParserResult(MsgParserResult):
    """Результат парсинга BaseappMgr::reqCreateEntityRemotely."""

    success: bool
    result: ReqCreateEntityRemotelyParsedMsgData
    msg_id: int = msgspec.baseappmgr.reqCreateEntityRemotely.id
    text: str = ""


class ReqCreateEntityRemotelyMsgParser(IMsgParser):
    """Парсер для BaseappMgr::reqCreateEntityRemotely."""

    def parse(self, msg: Message) -> ReqCreateEntityRemotelyMsgParserResult:
        """Распарсить сообщение BaseappMgr::reqCreateEntityRemotely."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = ReqCreateEntityRemotelyParsedMsgData(*values)
        return ReqCreateEntityRemotelyMsgParserResult(success=True, result=pd)


@dataclass
class ReqCreateEntityAnywhereFromDBIDQueryBestBaseappIDParsedMsgData(
    ParsedMsgData
):
    """Распарсенные данные сообщения BaseappMgr::reqCreateEntityAnywhereFromDBIDQueryBestBaseappID."""  # noqa: E501

    data: KBERowByteData


@dataclass(frozen=True)
class ReqCreateEntityAnywhereFromDBIDQueryBestBaseappIDMsgParserResult(
    MsgParserResult
):
    """Результат парсинга BaseappMgr::reqCreateEntityAnywhereFromDBIDQueryBestBaseappID."""  # noqa: E501

    success: bool
    result: ReqCreateEntityAnywhereFromDBIDQueryBestBaseappIDParsedMsgData
    msg_id: int = (
        msgspec.baseappmgr.reqCreateEntityAnywhereFromDBIDQueryBestBaseappID.id
    )
    text: str = ""


class ReqCreateEntityAnywhereFromDBIDQueryBestBaseappIDMsgParser(IMsgParser):
    """Парсер для BaseappMgr::reqCreateEntityAnywhereFromDBIDQueryBestBaseappID."""  # noqa: E501

    def parse(
        self, msg: Message
    ) -> ReqCreateEntityAnywhereFromDBIDQueryBestBaseappIDMsgParserResult:
        """Распарсить сообщение BaseappMgr::reqCreateEntityAnywhereFromDBIDQueryBestBaseappID."""  # noqa: E501
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = ReqCreateEntityAnywhereFromDBIDQueryBestBaseappIDParsedMsgData(
            *values
        )
        return ReqCreateEntityAnywhereFromDBIDQueryBestBaseappIDMsgParserResult(
            success=True, result=pd
        )


@dataclass
class ReqCreateEntityAnywhereFromDBIDParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения BaseappMgr::reqCreateEntityAnywhereFromDBID."""

    data: KBERowByteData


@dataclass(frozen=True)
class ReqCreateEntityAnywhereFromDBIDMsgParserResult(MsgParserResult):
    """Результат парсинга BaseappMgr::reqCreateEntityAnywhereFromDBID."""

    success: bool
    result: ReqCreateEntityAnywhereFromDBIDParsedMsgData
    msg_id: int = msgspec.baseappmgr.reqCreateEntityAnywhereFromDBID.id
    text: str = ""


class ReqCreateEntityAnywhereFromDBIDMsgParser(IMsgParser):
    """Парсер для BaseappMgr::reqCreateEntityAnywhereFromDBID."""

    def parse(
        self, msg: Message
    ) -> ReqCreateEntityAnywhereFromDBIDMsgParserResult:
        """Распарсить сообщение BaseappMgr::reqCreateEntityAnywhereFromDBID."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = ReqCreateEntityAnywhereFromDBIDParsedMsgData(*values)
        return ReqCreateEntityAnywhereFromDBIDMsgParserResult(
            success=True, result=pd
        )


@dataclass
class ReqCreateEntityRemotelyFromDBIDParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения BaseappMgr::reqCreateEntityRemotelyFromDBID."""

    data: KBERowByteData


@dataclass(frozen=True)
class ReqCreateEntityRemotelyFromDBIDMsgParserResult(MsgParserResult):
    """Результат парсинга BaseappMgr::reqCreateEntityRemotelyFromDBID."""

    success: bool
    result: ReqCreateEntityRemotelyFromDBIDParsedMsgData
    msg_id: int = msgspec.baseappmgr.reqCreateEntityRemotelyFromDBID.id
    text: str = ""


class ReqCreateEntityRemotelyFromDBIDMsgParser(IMsgParser):
    """Парсер для BaseappMgr::reqCreateEntityRemotelyFromDBID."""

    def parse(
        self, msg: Message
    ) -> ReqCreateEntityRemotelyFromDBIDMsgParserResult:
        """Распарсить сообщение BaseappMgr::reqCreateEntityRemotelyFromDBID."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = ReqCreateEntityRemotelyFromDBIDParsedMsgData(*values)
        return ReqCreateEntityRemotelyFromDBIDMsgParserResult(
            success=True, result=pd
        )


@dataclass
class ForwardMessageParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения BaseappMgr::forwardMessage."""

    data: KBERowByteData


@dataclass(frozen=True)
class ForwardMessageMsgParserResult(MsgParserResult):
    """Результат парсинга BaseappMgr::forwardMessage."""

    success: bool
    result: ForwardMessageParsedMsgData
    msg_id: int = msgspec.baseappmgr.forwardMessage.id
    text: str = ""


class ForwardMessageMsgParser(IMsgParser):
    """Парсер для BaseappMgr::forwardMessage."""

    def parse(self, msg: Message) -> ForwardMessageMsgParserResult:
        """Распарсить сообщение BaseappMgr::forwardMessage."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = ForwardMessageParsedMsgData(*values)
        return ForwardMessageMsgParserResult(success=True, result=pd)


@dataclass
class RegisterPendingAccountToBaseappAddrParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения BaseappMgr::registerPendingAccountToBaseappAddr."""

    data: KBERowByteData


@dataclass(frozen=True)
class RegisterPendingAccountToBaseappAddrMsgParserResult(MsgParserResult):
    """Результат парсинга BaseappMgr::registerPendingAccountToBaseappAddr."""

    success: bool
    result: RegisterPendingAccountToBaseappAddrParsedMsgData
    msg_id: int = msgspec.baseappmgr.registerPendingAccountToBaseappAddr.id
    text: str = ""


class RegisterPendingAccountToBaseappAddrMsgParser(IMsgParser):
    """Парсер для BaseappMgr::registerPendingAccountToBaseappAddr."""

    def parse(
        self, msg: Message
    ) -> RegisterPendingAccountToBaseappAddrMsgParserResult:
        """Распарсить сообщение BaseappMgr::registerPendingAccountToBaseappAddr."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = RegisterPendingAccountToBaseappAddrParsedMsgData(*values)
        return RegisterPendingAccountToBaseappAddrMsgParserResult(
            success=True, result=pd
        )


@dataclass
class ReqKillServerParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения BaseappMgr::reqKillServer."""


@dataclass(frozen=True)
class ReqKillServerMsgParserResult(MsgParserResult):
    """Результат парсинга BaseappMgr::reqKillServer."""

    success: bool
    result: ReqKillServerParsedMsgData
    msg_id: int = msgspec.baseappmgr.reqKillServer.id
    text: str = ""


class ReqKillServerMsgParser(IMsgParser):
    """Парсер для BaseappMgr::reqKillServer."""

    def parse(self, msg: Message) -> ReqKillServerMsgParserResult:
        """Распарсить сообщение BaseappMgr::reqKillServer."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = ReqKillServerParsedMsgData(*values)
        return ReqKillServerMsgParserResult(success=True, result=pd)


@dataclass
class StartProfileParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения BaseappMgr::startProfile."""

    profileName: KBEString  # noqa: N815  # pylint: disable=invalid-name
    profileType: KBEInt8  # noqa: N815  # pylint: disable=invalid-name
    timelen: KBEUInt32


@dataclass(frozen=True)
class StartProfileMsgParserResult(MsgParserResult):
    """Результат парсинга BaseappMgr::startProfile."""

    success: bool
    result: StartProfileParsedMsgData
    msg_id: int = msgspec.baseappmgr.startProfile.id
    text: str = ""


class StartProfileMsgParser(IMsgParser):
    """Парсер для BaseappMgr::startProfile."""

    def parse(self, msg: Message) -> StartProfileMsgParserResult:
        """Распарсить сообщение BaseappMgr::startProfile."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = StartProfileParsedMsgData(*values)
        return StartProfileMsgParserResult(success=True, result=pd)


@dataclass
class QueryWatcherParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения BaseappMgr::queryWatcher."""

    data: KBERowByteData


@dataclass(frozen=True)
class QueryWatcherMsgParserResult(MsgParserResult):
    """Результат парсинга BaseappMgr::queryWatcher."""

    success: bool
    result: QueryWatcherParsedMsgData
    msg_id: int = msgspec.baseappmgr.queryWatcher.id
    text: str = ""


class QueryWatcherMsgParser(IMsgParser):
    """Парсер для BaseappMgr::queryWatcher."""

    def parse(self, msg: Message) -> QueryWatcherMsgParserResult:
        """Распарсить сообщение BaseappMgr::queryWatcher."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = QueryWatcherParsedMsgData(*values)
        return QueryWatcherMsgParserResult(success=True, result=pd)


@dataclass
class QueryAppsLoadsParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения BaseappMgr::queryAppsLoads."""


@dataclass(frozen=True)
class QueryAppsLoadsMsgParserResult(MsgParserResult):
    """Результат парсинга BaseappMgr::queryAppsLoads."""

    success: bool
    result: QueryAppsLoadsParsedMsgData
    msg_id: int = msgspec.baseappmgr.queryAppsLoads.id
    text: str = ""


class QueryAppsLoadsMsgParser(IMsgParser):
    """Парсер для BaseappMgr::queryAppsLoads."""

    def parse(self, msg: Message) -> QueryAppsLoadsMsgParserResult:
        """Распарсить сообщение BaseappMgr::queryAppsLoads."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = QueryAppsLoadsParsedMsgData(*values)
        return QueryAppsLoadsMsgParserResult(success=True, result=pd)


@dataclass
class ReqAccountBindEmailAllocCallbackLoginappParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения BaseappMgr::reqAccountBindEmailAllocCallbackLoginapp."""

    data: KBERowByteData


@dataclass(frozen=True)
class ReqAccountBindEmailAllocCallbackLoginappMsgParserResult(MsgParserResult):
    """Результат парсинга BaseappMgr::reqAccountBindEmailAllocCallbackLoginapp."""

    success: bool
    result: ReqAccountBindEmailAllocCallbackLoginappParsedMsgData
    msg_id: int = msgspec.baseappmgr.reqAccountBindEmailAllocCallbackLoginapp.id
    text: str = ""


class ReqAccountBindEmailAllocCallbackLoginappMsgParser(IMsgParser):
    """Парсер для BaseappMgr::reqAccountBindEmailAllocCallbackLoginapp."""

    def parse(
        self, msg: Message
    ) -> ReqAccountBindEmailAllocCallbackLoginappMsgParserResult:
        """Распарсить сообщение BaseappMgr::reqAccountBindEmailAllocCallbackLoginapp."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = ReqAccountBindEmailAllocCallbackLoginappParsedMsgData(*values)
        return ReqAccountBindEmailAllocCallbackLoginappMsgParserResult(
            success=True, result=pd
        )


@dataclass
class OnReqAccountBindEmailCBFromLoginappParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения BaseappMgr::onReqAccountBindEmailCBFromLoginapp."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnReqAccountBindEmailCBFromLoginappMsgParserResult(MsgParserResult):
    """Результат парсинга BaseappMgr::onReqAccountBindEmailCBFromLoginapp."""

    success: bool
    result: OnReqAccountBindEmailCBFromLoginappParsedMsgData
    msg_id: int = msgspec.baseappmgr.onReqAccountBindEmailCBFromLoginapp.id
    text: str = ""


class OnReqAccountBindEmailCBFromLoginappMsgParser(IMsgParser):
    """Парсер для BaseappMgr::onReqAccountBindEmailCBFromLoginapp."""

    def parse(
        self, msg: Message
    ) -> OnReqAccountBindEmailCBFromLoginappMsgParserResult:
        """Распарсить сообщение BaseappMgr::onReqAccountBindEmailCBFromLoginapp."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnReqAccountBindEmailCBFromLoginappParsedMsgData(*values)
        return OnReqAccountBindEmailCBFromLoginappMsgParserResult(
            success=True, result=pd
        )


@dataclass
class ReqCloseServerParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения BaseappMgr::reqCloseServer."""


@dataclass(frozen=True)
class ReqCloseServerMsgParserResult(MsgParserResult):
    """Результат парсинга BaseappMgr::reqCloseServer."""

    success: bool
    result: ReqCloseServerParsedMsgData
    msg_id: int = msgspec.baseappmgr.reqCloseServer.id
    text: str = ""


class ReqCloseServerMsgParser(IMsgParser):
    """Парсер для BaseappMgr::reqCloseServer."""

    def parse(self, msg: Message) -> ReqCloseServerMsgParserResult:
        """Распарсить сообщение BaseappMgr::reqCloseServer."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = ReqCloseServerParsedMsgData(*values)
        return ReqCloseServerMsgParserResult(success=True, result=pd)
