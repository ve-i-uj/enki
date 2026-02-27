"""Обработчик сообщений от компонента Loginapp."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar

from enki import msgspec
from enki.kbeenum import (
    COMPONENT_STATE_BY_SHUTDOWN_STATE,
    ClientType,
    ComponentState,
    ComponentType,
    ServerError,
    ShutdownState,
)
from enki.misc import devonly
from enki.msg_parser import kbemath
from enki.net.addr import Addr, Port

from .common import (
    OnAppActiveTickParsedMsgData,
    OnDbmgrInitCompletedParsedMsgData,
)
from .imsg_parser import IMsgParser, MsgParserResult, ParsedMsgData

if TYPE_CHECKING:
    from enki.kbetype.decoders.custom_decoders import (
        KBEComponentId,
        KBEComponentType,
        KBEEntityId,
        KBEServerErrorCode,
    )
    from enki.kbetype.pytypes.basic_data_types import (
        KBEBlob,
        KBEBool,
        KBEFloat,
        KBEInt8,
        KBEInt32,
        KBEString,
        KBEUInt16,
        KBEUInt32,
        KBEUInt64,
    )
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
        """Распарсить сообщение Loginapp::onDbmgrInitCompleted.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnDbmgrInitCompletedMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        pd = OnDbmgrInitCompletedParsedMsgData(*values)
        return OnDbmgrInitCompletedMsgParserResult(success=True, result=pd)


@dataclass
class OnBaseappInitProgressParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Loginapp::onBaseappInitProgress."""

    progress: KBEFloat


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
        """Распарсить сообщение Loginapp::onBaseappInitProgress.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnBaseappInitProgressMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        pd = OnBaseappInitProgressParsedMsgData(*values)
        return OnBaseappInitProgressMsgParserResult(success=True, result=pd)


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
        return OnAppActiveTickMsgParserResult(success=True, result=pd)


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
        """Распарсить сообщение Loginapp::hello.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            HelloMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        pd = HelloParsedMsgData(*values)
        return HelloMsgParserResult(success=True, result=pd)


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
        """Флаг того нужен ли принудительный логин.

        Returns:
            bool: Флаг того нужен ли принудительный логин

        """
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
        """Распарсить сообщение Loginapp::login.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            LoginMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        pd = LoginParsedMsgData(*values)
        return LoginMsgParserResult(success=True, result=pd)


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
    """Распарсенные данные сообщения Loginapp::onLoginAccountQueryBaseappAddrFromBaseappmgr."""  # noqa: E501

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
    """Парсер для Loginapp::onLoginAccountQueryBaseappAddrFromBaseappmgr."""

    success: bool
    result: OnLoginAccountQueryBaseappAddrFromBaseappmgrParsedMsgData
    msg_id: int = (
        msgspec.loginapp.onLoginAccountQueryBaseappAddrFromBaseappmgr.id
    )
    text: str = ""


class OnLoginAccountQueryBaseappAddrFromBaseappmgrMsgParser(IMsgParser):
    """Парсер для Loginapp::onLoginAccountQueryBaseappAddrFromBaseappmgr."""

    def parse(
        self, msg: Message
    ) -> OnLoginAccountQueryBaseappAddrFromBaseappmgrMsgParserResult:
        """Распарсить сообщение Loginapp::onLoginAccountQueryBaseappAddrFromBaseappmgr.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnLoginAccountQueryBaseappAddrFromBaseappmgrParserMsgParserResult:
                объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnLoginAccountQueryBaseappAddrFromBaseappmgrParsedMsgData(*values)
        return OnLoginAccountQueryBaseappAddrFromBaseappmgrMsgParserResult(
            success=True, result=pd
        )


@dataclass
class ImportServerErrorsDescrParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Loginapp::importServerErrorsDescr."""


@dataclass(frozen=True)
class ImportServerErrorsDescrMsgParserResult(MsgParserResult):
    """Парсер для Loginapp::importServerErrorsDescr."""

    success: bool
    result: ImportServerErrorsDescrParsedMsgData
    msg_id: int = msgspec.loginapp.importServerErrorsDescr.id
    text: str = ""


class ImportServerErrorsDescrMsgParser(IMsgParser):
    """Парсер для Loginapp::importServerErrorsDescr."""

    def parse(self, msg: Message) -> ImportServerErrorsDescrMsgParserResult:
        """Распарсить сообщение Loginapp::importServerErrorsDescr.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            ImportServerErrorsDescrParserMsgParserResult: объект
                результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = ImportServerErrorsDescrParsedMsgData(*values)
        return ImportServerErrorsDescrMsgParserResult(success=True, result=pd)


@dataclass
class ReqCloseParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Loginapp::reqClose."""


@dataclass(frozen=True)
class ReqCloseMsgParserResult(MsgParserResult):
    """Результат парсинга Loginapp::reqClose."""

    success: bool
    result: ReqCloseParsedMsgData
    msg_id: int = msgspec.loginapp.reqClose.id
    text: str = ""


class ReqCloseMsgParser(IMsgParser):
    """Парсер для Loginapp::reqClose."""

    def parse(self, msg: Message) -> ReqCloseMsgParserResult:
        """Распарсить сообщение Loginapp::reqClose.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            ReqCloseMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        pd = ReqCloseParsedMsgData(*values)
        return ReqCloseMsgParserResult(success=True, result=pd)


@dataclass
class OnClientActiveTickParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Loginapp::onClientActiveTick."""


@dataclass(frozen=True)
class OnClientActiveTickMsgParserResult(MsgParserResult):
    """Результат парсинга Loginapp::onClientActiveTick."""

    success: bool
    result: OnClientActiveTickParsedMsgData
    msg_id: int = msgspec.loginapp.onClientActiveTick.id
    text: str = ""


class OnClientActiveTickMsgParser(IMsgParser):
    """Парсер для Loginapp::onClientActiveTickonClientActiveTick."""

    def parse(self, msg: Message) -> OnClientActiveTickMsgParserResult:
        """Распарсить сообщение Loginapp::onClientActiveTickonClientActiveTick.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnClientActiveTickMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        pd = OnClientActiveTickParsedMsgData(*values)
        return OnClientActiveTickMsgParserResult(success=True, result=pd)


@dataclass
class ImportClientMessagesParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Loginapp::importClientMessages."""


@dataclass(frozen=True)
class ImportClientMessagesMsgParserResult(MsgParserResult):
    """Результат парсинга Loginapp::importClientMessages."""

    success: bool
    result: ImportClientMessagesParsedMsgData
    msg_id: int = msgspec.loginapp.importClientMessages.id
    text: str = ""


class ImportClientMessagesMsgParser(IMsgParser):
    """Парсер для Loginapp::importClientMessages."""

    def parse(self, msg: Message) -> ImportClientMessagesMsgParserResult:
        """Распарсить сообщение Loginapp::importClientMessages.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            ImportClientMessagesMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        pd = ImportClientMessagesParsedMsgData(*values)
        return ImportClientMessagesMsgParserResult(success=True, result=pd)


@dataclass
class ReqCreateAccountParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Loginapp::reqCreateAccount."""

    account_name: KBEString
    password: KBEString
    client_data: KBEBlob


@dataclass(frozen=True)
class ReqCreateAccountMsgParserResult(MsgParserResult):
    """Результат парсинга Loginapp::reqCreateAccount."""

    success: bool
    result: ReqCreateAccountParsedMsgData
    msg_id: int = msgspec.loginapp.reqCreateAccount.id
    text: str = ""


class ReqCreateAccountMsgParser(IMsgParser):
    """Парсер для Loginapp::reqCreateAccount."""

    def parse(self, msg: Message) -> ReqCreateAccountMsgParserResult:
        """Распарсить сообщение Loginapp::reqCreateAccount.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            ReqCreateAccountMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        pd = ReqCreateAccountParsedMsgData(*values)
        return ReqCreateAccountMsgParserResult(success=True, result=pd)


@dataclass
class ReqCreateMailAccountParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Loginapp::reqCreateMailAccount."""

    account_name: KBEString
    password: KBEString
    client_data: KBEBlob


@dataclass(frozen=True)
class ReqCreateMailAccountMsgParserResult(MsgParserResult):
    """Результат парсинга Loginapp::reqCreateMailAccount."""

    success: bool
    result: ReqCreateMailAccountParsedMsgData
    msg_id: int = msgspec.loginapp.reqCreateMailAccount.id
    text: str = ""


class ReqCreateMailAccountMsgParser(IMsgParser):
    """Парсер для Loginapp::reqCreateMailAccount."""

    def parse(self, msg: Message) -> ReqCreateMailAccountMsgParserResult:
        """Распарсить сообщение Loginapp::reqCreateMailAccount.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            ReqCreateMailAccountMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        pd = ReqCreateMailAccountParsedMsgData(*values)
        return ReqCreateMailAccountMsgParserResult(success=True, result=pd)


@dataclass
class ImportClientSDKParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Loginapp::importClientSDK."""

    options: KBEString
    clientWindowSize: KBEInt32  # noqa: N815  # pylint: disable=invalid-name
    callbackIP: KBEString  # noqa: N815  # pylint: disable=invalid-name
    callbackPort: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name


@dataclass(frozen=True)
class ImportClientSDKMsgParserResult(MsgParserResult):
    """Результат парсинга Loginapp::importClientSDK."""

    success: bool
    result: ImportClientSDKParsedMsgData
    msg_id: int = msgspec.loginapp.importClientSDK.id
    text: str = ""


class ImportClientSDKMsgParser(IMsgParser):
    """Парсер для Loginapp::importClientSDK."""

    def parse(self, msg: Message) -> ImportClientSDKMsgParserResult:
        """Распарсить сообщение Loginapp::importClientSDK.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            ImportClientSDKMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        pd = ImportClientSDKParsedMsgData(*values)
        return ImportClientSDKMsgParserResult(success=True, result=pd)


@dataclass
class LookAppParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Loginapp::lookApp."""


@dataclass(frozen=True)
class LookAppMsgParserResult(MsgParserResult):
    """Результат парсинга Loginapp::lookApp."""

    success: bool
    result: LookAppParsedMsgData
    msg_id: int = msgspec.loginapp.lookApp.id
    text: str = ""


class LookAppMsgParser(IMsgParser):
    """Парсер для Loginapp::lookApp."""

    def parse(self, msg: Message) -> LookAppMsgParserResult:
        """Распарсить сообщение Loginapp::lookApp.

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
class QueryLoadParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Loginapp::queryLoad."""


@dataclass(frozen=True)
class QueryLoadMsgParserResult(MsgParserResult):
    """Результат парсинга Loginapp::queryLoad."""

    success: bool
    result: QueryLoadParsedMsgData
    msg_id: int = msgspec.loginapp.queryLoad.id
    text: str = ""


class QueryLoadMsgParser(IMsgParser):
    """Парсер для Loginapp::queryLoad."""

    def parse(self, msg: Message) -> QueryLoadMsgParserResult:
        """Распарсить сообщение Loginapp::queryLoad.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            QueryLoadMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        pd = QueryLoadParsedMsgData(*values)
        return QueryLoadMsgParserResult(success=True, result=pd)


@dataclass
class ReqCloseServerParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Loginapp::reqCloseServer."""


@dataclass(frozen=True)
class ReqCloseServerMsgParserResult(MsgParserResult):
    """Результат парсинга Loginapp::reqCloseServer."""

    success: bool
    result: ReqCloseServerParsedMsgData
    msg_id: int = msgspec.loginapp.reqCloseServer.id
    text: str = ""


class ReqCloseServerMsgParser(IMsgParser):
    """Парсер для Loginapp::reqCloseServer."""

    def parse(self, msg: Message) -> ReqCloseServerMsgParserResult:
        """Распарсить сообщение Loginapp::reqCloseServer.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            ReqCloseServerMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        pd = ReqCloseServerParsedMsgData(*values)
        return ReqCloseServerMsgParserResult(success=True, result=pd)


@dataclass
class ReqAccountResetPasswordParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Loginapp::reqAccountResetPassword."""

    account_name: KBEString


@dataclass(frozen=True)
class ReqAccountResetPasswordMsgParserResult(MsgParserResult):
    """Результат парсинга Loginapp::reqAccountResetPassword."""

    success: bool
    result: ReqAccountResetPasswordParsedMsgData
    msg_id: int = msgspec.loginapp.reqAccountResetPassword.id
    text: str = ""


class ReqAccountResetPasswordMsgParser(IMsgParser):
    """Парсер для Loginapp::reqAccountResetPassword."""

    def parse(self, msg: Message) -> ReqAccountResetPasswordMsgParserResult:
        """Распарсить сообщение Loginapp::reqAccountResetPassword.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            ReqAccountResetPasswordMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        pd = ReqAccountResetPasswordParsedMsgData(*values)
        return ReqAccountResetPasswordMsgParserResult(success=True, result=pd)


@dataclass
class OnReqAccountResetPasswordCBParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Loginapp::onReqAccountResetPasswordCB."""

    account_name: KBEString
    email: KBEString
    failedcode: KBEServerErrorCode
    code: KBEString

    @property
    def ret_code(self) -> ServerError:
        """Код возврата от сервера.

        Returns:
            ServerError: Код возврата от сервера

        """
        return ServerError(self.failedcode)

    __add_to_dict__: ClassVar = ("ret_code",)


@dataclass(frozen=True)
class OnReqAccountResetPasswordCBMsgParserResult(MsgParserResult):
    """Результат парсинга Loginapp::onReqAccountResetPasswordCB."""

    success: bool
    result: OnReqAccountResetPasswordCBParsedMsgData
    msg_id: int = msgspec.loginapp.onReqAccountResetPasswordCB.id
    text: str = ""


class OnReqAccountResetPasswordCBMsgParser(IMsgParser):
    """Парсер для Loginapp::onReqAccountResetPasswordCB."""

    def parse(self, msg: Message) -> OnReqAccountResetPasswordCBMsgParserResult:
        """Распарсить сообщение Loginapp::onReqAccountResetPasswordCB.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnReqAccountResetPasswordCBMsgParserResult: объект результата
                обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        pd = OnReqAccountResetPasswordCBParsedMsgData(*values)
        return OnReqAccountResetPasswordCBMsgParserResult(
            success=True, result=pd
        )


@dataclass
class OnReqCreateAccountResultParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Loginapp::onReqCreateAccountResult."""

    failedcode: KBEServerErrorCode
    register_name: KBEString
    password: KBEString
    getdatas: KBEString

    @property
    def ret_code(self) -> ServerError:
        """Код возврата от сервера.

        Returns:
            ServerError: Код возврата от сервера

        """
        return ServerError(self.failedcode)

    __add_to_dict__: ClassVar = ("ret_code",)


@dataclass(frozen=True)
class OnReqCreateAccountResultMsgParserResult(MsgParserResult):
    """Результат парсинга Loginapp::onReqCreateAccountResult."""

    success: bool
    result: OnReqCreateAccountResultParsedMsgData
    msg_id: int = msgspec.loginapp.onReqCreateAccountResult.id
    text: str = ""


class OnReqCreateAccountResultMsgParser(IMsgParser):
    """Парсер для Loginapp::onReqCreateAccountResult."""

    def parse(self, msg: Message) -> OnReqCreateAccountResultMsgParserResult:
        """Распарсить сообщение Loginapp::onReqCreateAccountResult.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnReqCreateAccountResultMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        pd = OnReqCreateAccountResultParsedMsgData(*values)
        return OnReqCreateAccountResultMsgParserResult(success=True, result=pd)


@dataclass
class OnReqCreateMailAccountResultParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Loginapp::onReqCreateMailAccountResult."""

    failedcode: KBEServerErrorCode
    register_name: KBEString
    password: KBEString
    getdatas: KBEString

    @property
    def ret_code(self) -> ServerError:
        """Код возврата от сервера.

        Returns:
            ServerError: Код возврата от сервера

        """
        return ServerError(self.failedcode)

    __add_to_dict__: ClassVar = ("ret_code",)


@dataclass(frozen=True)
class OnReqCreateMailAccountResultMsgParserResult(MsgParserResult):
    """Результат парсинга Loginapp::onReqCreateMailAccountResult."""

    success: bool
    result: OnReqCreateMailAccountResultParsedMsgData
    msg_id: int = msgspec.loginapp.onReqCreateMailAccountResult.id
    text: str = ""


class OnReqCreateMailAccountResultMsgParser(IMsgParser):
    """Парсер для Loginapp::onReqCreateMailAccountResult."""

    def parse(
        self, msg: Message
    ) -> OnReqCreateMailAccountResultMsgParserResult:
        """Распарсить сообщение Loginapp::onReqCreateMailAccountResult.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnReqCreateMailAccountResultMsgParserResult: объект результата
                обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        pd = OnReqCreateMailAccountResultParsedMsgData(*values)
        return OnReqCreateMailAccountResultMsgParserResult(
            success=True, result=pd
        )


@dataclass
class OnAccountActivatedParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Loginapp::onAccountActivated."""

    code: KBEString
    success: KBEBool

    __add_to_dict__: ClassVar = ()


@dataclass(frozen=True)
class OnAccountActivatedMsgParserResult(MsgParserResult):
    """Результат парсинга Loginapp::onAccountActivated."""

    success: bool
    result: OnAccountActivatedParsedMsgData
    msg_id: int = msgspec.loginapp.onAccountActivated.id
    text: str = ""


class OnAccountActivatedMsgParser(IMsgParser):
    """Парсер для Loginapp::onAccountActivated."""

    def parse(self, msg: Message) -> OnAccountActivatedMsgParserResult:
        """Распарсить сообщение Loginapp::onAccountActivated.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnAccountActivatedMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        pd = OnAccountActivatedParsedMsgData(*values)
        return OnAccountActivatedMsgParserResult(success=True, result=pd)


@dataclass
class OnAccountBindedEmailParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Loginapp::onAccountBindedEmail."""

    code: KBEString
    success: KBEBool

    __add_to_dict__: ClassVar = ()


@dataclass(frozen=True)
class OnAccountBindedEmailMsgParserResult(MsgParserResult):
    """Результат парсинга Loginapp::onAccountBindedEmail."""

    success: bool
    result: OnAccountBindedEmailParsedMsgData
    msg_id: int = msgspec.loginapp.onAccountBindedEmail.id
    text: str = ""


class OnAccountBindedEmailMsgParser(IMsgParser):
    """Парсер для Loginapp::onAccountBindedEmail."""

    def parse(self, msg: Message) -> OnAccountBindedEmailMsgParserResult:
        """Распарсить сообщение Loginapp::onAccountBindedEmail.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnAccountBindedEmailMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        pd = OnAccountBindedEmailParsedMsgData(*values)
        return OnAccountBindedEmailMsgParserResult(success=True, result=pd)


@dataclass
class OnAccountResetPasswordParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Loginapp::onAccountResetPassword."""

    code: KBEString
    success: KBEBool

    __add_to_dict__: ClassVar = ()


@dataclass(frozen=True)
class OnAccountResetPasswordMsgParserResult(MsgParserResult):
    """Результат парсинга Loginapp::onAccountResetPassword."""

    success: bool
    result: OnAccountResetPasswordParsedMsgData
    msg_id: int = msgspec.loginapp.onAccountResetPassword.id
    text: str = ""


class OnAccountResetPasswordMsgParser(IMsgParser):
    """Парсер для Loginapp::onAccountResetPassword."""

    def parse(self, msg: Message) -> OnAccountResetPasswordMsgParserResult:
        """Распарсить сообщение Loginapp::onAccountResetPassword.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnAccountResetPasswordMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        pd = OnAccountResetPasswordParsedMsgData(*values)
        return OnAccountResetPasswordMsgParserResult(success=True, result=pd)


@dataclass
class OnReqAccountBindEmailAllocCallbackLoginappParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Loginapp::onReqAccountBindEmailAllocCallbackLoginapp."""  # noqa: E501

    reqBaseappID: KBEComponentId  # noqa: N815  # pylint: disable=invalid-name
    entityID: KBEEntityId  # noqa: N815  # pylint: disable=invalid-name
    accountName: KBEString  # noqa: N815  # pylint: disable=invalid-name
    email: KBEString
    failedcode: KBEServerErrorCode
    code: KBEString

    @property
    def ret_code(self) -> ServerError:
        """Код возврата от сервера.

        Returns:
            ServerError: Код возврата от сервера

        """
        return ServerError(self.failedcode)

    __add_to_dict__: ClassVar = ("ret_code",)


@dataclass(frozen=True)
class OnReqAccountBindEmailAllocCallbackLoginappMsgParserResult(
    MsgParserResult
):
    """Результат парсинга Loginapp::onReqAccountBindEmailAllocCallbackLoginapp."""

    success: bool
    result: OnReqAccountBindEmailAllocCallbackLoginappParsedMsgData
    msg_id: int = msgspec.loginapp.onReqAccountBindEmailAllocCallbackLoginapp.id
    text: str = ""


class OnReqAccountBindEmailAllocCallbackLoginappMsgParser(IMsgParser):
    """Парсер для Loginapp::onReqAccountBindEmailAllocCallbackLoginapp."""

    def parse(
        self, msg: Message
    ) -> OnReqAccountBindEmailAllocCallbackLoginappMsgParserResult:
        """Распарсить сообщение Loginapp::onReqAccountBindEmailAllocCallbackLoginapp.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnReqAccountBindEmailAllocCallbackLoginappMsgParserResult: объект
                результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnReqAccountBindEmailAllocCallbackLoginappParsedMsgData(*values)
        return OnReqAccountBindEmailAllocCallbackLoginappMsgParserResult(
            success=True, result=pd
        )


@dataclass
class StartProfileParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Loginapp::startProfile."""

    profileName: KBEString  # noqa: N815  # pylint: disable=invalid-name
    profileType: KBEInt8  # noqa: N815  # pylint: disable=invalid-name
    timelen: KBEUInt32


@dataclass(frozen=True)
class StartProfileMsgParserResult(MsgParserResult):
    """Результат парсинга Loginapp::startProfile."""

    success: bool
    result: StartProfileParsedMsgData
    msg_id: int = msgspec.loginapp.startProfile.id
    text: str = ""


class StartProfileMsgParser(IMsgParser):
    """Парсер для Loginapp::startProfile."""

    def parse(self, msg: Message) -> StartProfileMsgParserResult:
        """Распарсить сообщение Loginapp::startProfile.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            StartProfileMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        pd = StartProfileParsedMsgData(*values)
        return StartProfileMsgParserResult(success=True, result=pd)


@dataclass
class ReqKillServerParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Loginapp::reqKillServer."""

    component_id: KBEComponentId
    componentType: (
        KBEComponentType  # pylint: disable=invalid-name
    )
    username: KBEString
    uid: KBEInt32
    reason: KBEString

    @property
    def component_type(self) -> ComponentType:
        """Энам типа компонента.

        Returns:
            ComponentType: энам типа компонента

        """
        return ComponentType(self.componentType)

    __add_to_dict__: ClassVar = ("component_type",)


@dataclass(frozen=True)
class ReqKillServerMsgParserResult(MsgParserResult):
    """Результат парсинга Loginapp::reqKillServer."""

    success: bool
    result: ReqKillServerParsedMsgData
    msg_id: int = msgspec.loginapp.reqKillServer.id
    text: str = ""


class ReqKillServerMsgParser(IMsgParser):
    """Парсер для Loginapp::reqKillServer."""

    def parse(self, msg: Message) -> ReqKillServerMsgParserResult:
        """Распарсить сообщение Loginapp::reqKillServer.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            ReqKillServerMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        pd = ReqKillServerParsedMsgData(*values)
        return ReqKillServerMsgParserResult(success=True, result=pd)


@dataclass
class QueryWatcherParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Loginapp::queryWatcher."""

    path: KBEString


@dataclass(frozen=True)
class QueryWatcherMsgParserResult(MsgParserResult):
    """Результат парсинга Loginapp::queryWatcher."""

    success: bool
    result: QueryWatcherParsedMsgData
    msg_id: int = msgspec.loginapp.queryWatcher.id
    text: str = ""


class QueryWatcherMsgParser(IMsgParser):
    """Парсер для Loginapp::queryWatcher."""

    def parse(self, msg: Message) -> QueryWatcherMsgParserResult:
        """Распарсить сообщение Loginapp::queryWatcher.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            QueryWatcherMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        pd = QueryWatcherParsedMsgData(*values)
        return QueryWatcherMsgParserResult(success=True, result=pd)


@dataclass
class OnLookAppParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Loginapp::onLookApp."""

    componentType: KBEComponentType  # noqa: N815
    componentId: KBEComponentId  # noqa: N815
    shutdownState: KBEInt8  # noqa: N815

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
class OnLookAppMsgParserResult(MsgParserResult):
    """Парсер для Loginapp::onLookApp."""

    success: bool
    result: OnLookAppParsedMsgData
    msg_id: int = msgspec.loginapp.onLookApp.id
    text: str = ""


class OnLookAppMsgParser(IMsgParser):
    """Парсер для Loginapp::onLookApp."""

    def parse(self, msg: Message) -> OnLookAppMsgParserResult:
        """Распарсить сообщение Loginapp::onLookApp.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnLookAppParserMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnLookAppParsedMsgData(*values)
        return OnLookAppMsgParserResult(success=True, result=pd)
