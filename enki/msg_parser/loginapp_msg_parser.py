"""Обработчик сообщений от компонента Loginapp."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar

from enki import msgspec
from enki.core import kbemath
from enki.kbeenum import ClientType, ServerError
from enki.kbetype.decoders.custom_decoders import KBEComponentId, KBEEntityId
from enki.kbetype.pytypes.basic_data_types import (
    KBEBool,
    KBEUInt16,
    KBEUInt32,
    KBEUInt64,
)
from enki.misc import devonly
from enki.net.addr import Addr, Port

from .common import (
    OnAppActiveTickParsedMsgData,
    OnDbmgrInitCompletedParsedMsgData,
)
from .imsg_parser import IMsgParser, MsgParserResult, ParsedMsgData

if TYPE_CHECKING:
    from enki.kbetype.pytypes.basic_data_types import KBEBlob, KBEInt8, KBEString
    from enki.msg.message import Message

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OnDbmgrInitCompletedMsgParserResult(MsgParserResult):
    """Результат парсинга Loginapp::onDbmgrInitCompleted."""

    success: bool
    result: OnDbmgrInitCompletedParsedMsgData
    msg_id: int = msgspec.loginapp.onDbmgrInitCompleted.id
    text: str = ""


class OnDbmgrInitCompletedMsgParser(IMsgParser):
    """Парсер для Loginapp::onDbmgrInitCompleted."""

    def parse(self, msg: Message) -> OnDbmgrInitCompletedMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnDbmgrInitCompletedParsedMsgData(*values)
        return OnDbmgrInitCompletedMsgParserResult(True, pd)


@dataclass
class OnBaseappInitProgressParsedMsgData(ParsedMsgData):
    progress: float


@dataclass(frozen=True)
class OnBaseappInitProgressMsgParserResult(MsgParserResult):
    """Результат парсинга Loginapp::onBaseappInitProgress."""

    success: bool
    result: OnBaseappInitProgressParsedMsgData | None
    msg_id: int = msgspec.loginapp.onBaseappInitProgress.id
    text: str = ""


class OnBaseappInitProgressMsgParser(IMsgParser):
    """Парсер для Loginapp::onBaseappInitProgress."""

    def parse(self, msg: Message) -> OnBaseappInitProgressMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnBaseappInitProgressParsedMsgData(*values)
        return OnBaseappInitProgressMsgParserResult(True, pd)


@dataclass(frozen=True)
class OnAppActiveTickMsgParserResult(MsgParserResult):
    """Результат парсинга Loginapp::onAppActiveTick."""

    success: bool
    result: OnAppActiveTickParsedMsgData
    msg_id: int = msgspec.loginapp.onAppActiveTick.id
    text: str = ""


class OnAppActiveTickMsgParser(IMsgParser):
    """Парсер для Loginapp::onAppActiveTick."""

    def parse(self, msg: Message) -> OnAppActiveTickMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnAppActiveTickParsedMsgData(*values)
        return OnAppActiveTickMsgParserResult(True, pd)


@dataclass
class HelloParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Loginapp::hello."""

    kbe_version: KBEString
    script_version: KBEString
    encrypted_key: KBEBlob


@dataclass(frozen=True)
class HelloMsgParserResult(MsgParserResult):
    """Результат парсинга Loginapp::hello."""

    success: bool
    result: HelloParsedMsgData | None
    msg_id: int = msgspec.loginapp.hello.id
    text: str = ""


class HelloMsgParser(IMsgParser):
    """Парсер для Loginapp::hello."""

    def parse(self, msg: Message) -> HelloMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = HelloParsedMsgData(*values)
        return HelloMsgParserResult(True, pd)


@dataclass
class LoginParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Loginapp::login."""

    # client type (see ClientType)
    clientType: KBEInt8  # noqa: N815  # pylint: disable=invalid-name
    # binary data for "onRequestLogin" callback of script layer
    clientData: KBEBlob  # noqa: N815  # pylint: disable=invalid-name
    accountName: KBEString  # noqa: N815  # pylint: disable=invalid-name
    password: KBEString
    digest: KBEString
    # force login for "bots" client type (any not empty value is true)
    forceLogin: KBEString  # noqa: N815  # pylint: disable=invalid-name

    @property
    def client_type(self) -> ClientType:
        """Тип клиента.

        Returns:
            ClientType: тип клиента.

        """
        return ClientType(self.clientType)

    @property
    def force_login(self) -> bool:
        return bool(self.forceLogin)

    __add_to_dict__: ClassVar = (
        "client_type",
        "force_login",
    )


@dataclass(frozen=True)
class LoginMsgParserResult(MsgParserResult):
    """Результат парсинга Loginapp::login."""

    success: bool
    result: LoginParsedMsgData | None
    msg_id: int = msgspec.loginapp.login.id
    text: str = ""


class LoginMsgParser(IMsgParser):
    """Парсер для Loginapp::login."""

    def parse(self, msg: Message) -> LoginMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = LoginParsedMsgData(*values)
        return LoginMsgParserResult(True, pd)


@dataclass
class OnLoginAccountQueryResultFromDbmgrParsedMsgData(ParsedMsgData):
    """Данные парсинга Loginapp::onLoginAccountQueryResultFromDbmgr."""

    retCode: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name
    login: KBEString
    account_name: KBEString
    password: KBEString
    needCheckPassword: KBEBool  # noqa: N815  # pylint: disable=invalid-name
    componentID: KBEComponentId  # noqa: N815  # pylint: disable=invalid-name
    entitiy_id: KBEEntityId
    db_id: KBEUInt64  # dbid
    flags: KBEUInt32  # flags
    deadline: KBEUInt64  # deadline
    data: KBEString

    @property
    def ret_code(self) -> ServerError:
        """Возвращает код ошибки в виде enum ServerError.

        Returns:
            ServerError: Код ошибки

        """
        return ServerError(self.retCode)

    __add_to_dict__: ClassVar = ("ret_code",)


@dataclass(frozen=True)
class OnLoginAccountQueryResultFromDbmgrMsgParserResult(MsgParserResult):
    """Результат парсинга Loginapp::onLoginAccountQueryResultFromDbmgr."""

    success: bool
    result: OnLoginAccountQueryResultFromDbmgrParsedMsgData
    msg_id: int = msgspec.loginapp.onLoginAccountQueryResultFromDbmgr.id
    text: str = ""


class OnLoginAccountQueryResultFromDbmgrMsgParser(IMsgParser):
    """Парсер для Loginapp::onLoginAccountQueryResultFromDbmgr."""

    def parse(
        self, msg: Message
    ) -> OnLoginAccountQueryResultFromDbmgrMsgParserResult:
        """Парсинг сообщения DLoginappBMgr::onLoginAccountQueryResultFromDbmgr.

        :param msg: Сообщение для парсинга
        :return: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnLoginAccountQueryResultFromDbmgrParsedMsgData(*values)
        return OnLoginAccountQueryResultFromDbmgrMsgParserResult(
            success=True, result=pd
        )


@dataclass
class OnLoginAccountQueryBaseappAddrFromBaseappmgrParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения BaseappMgr::onLoginAccountQueryBaseappAddrFromBaseappmgr."""

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
class OnLoginAccountQueryBaseappAddrFromBaseappmgrMsgParserResult(
    MsgParserResult
):
    """Парсер для BaseappMgr::onLoginAccountQueryBaseappAddrFromBaseappmgr."""

    success: bool
    result: OnLoginAccountQueryBaseappAddrFromBaseappmgrParsedMsgData
    msg_id: int = msgspec.loginapp.onLoginAccountQueryBaseappAddrFromBaseappmgr.id
    text: str = ""


class OnLoginAccountQueryBaseappAddrFromBaseappmgrMsgParser(IMsgParser):
    """Парсер для BaseappMgr::onLoginAccountQueryBaseappAddrFromBaseappmgr."""

    def parse(
        self, msg: Message
    ) -> OnLoginAccountQueryBaseappAddrFromBaseappmgrMsgParserResult:
        """Распарсить сообщение BaseappMgr::onLoginAccountQueryBaseappAddrFromBaseappmgr.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnLoginAccountQueryBaseappAddrFromBaseappmgrParserMsgParserResult: объект
                результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnLoginAccountQueryBaseappAddrFromBaseappmgrParsedMsgData(*values)
        return OnLoginAccountQueryBaseappAddrFromBaseappmgrMsgParserResult(
            success=True, result=pd
        )
