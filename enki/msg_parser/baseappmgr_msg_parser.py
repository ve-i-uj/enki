"""Парсер сообщений от компонента BaseappMgr."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar

from enki import msgspec
from enki.core import kbemath
from enki.kbeenum import ClientType
from enki.kbetype.decoders.custom_decoders import KBEDdid
from enki.kbetype.pytypes.basic_data_types import (
    KBEBool,
    KBEInt32,
    KBEString,
    KBEUInt16,
    KBEUInt32,
    KBEUInt64,
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
    from enki.kbetype.decoders.custom_decoders import KBEComponentId
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
    dbid: KBEDdid
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
