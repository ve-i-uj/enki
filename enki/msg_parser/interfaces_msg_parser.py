"""Парсеры сообщений от компонента Interfaces."""

import logging
from dataclasses import dataclass
from typing import Any, ClassVar

from enki import msgspec
from enki.kbeenum import (
    COMPONENT_STATE_BY_SHUTDOWN_STATE,
    AccountType,
    ClientType,
    ComponentState,
    ComponentType,
    ShutdownState,
)
from enki.kbetype.decoders.custom_decoders import (
    KBEComponentId,
    KBEComponentType,
    KBEShutdownState,
)
from enki.kbetype.pytypes.basic_data_types import KBEBlob, KBEString
from enki.misc import devonly
from enki.msg.message import Message

from .common import (
    OnAppActiveTickParsedMsgData,
    OnRegisterNewAppParsedMsgData,
    ReqCloseServerParsedMsgData,
)
from .imsg_parser import IMsgParser, MsgParserResult, ParsedMsgData

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ReqCloseServerParsedMsgParserResult(MsgParserResult):
    """Результат парсинга Interfaces::reqCloseServer."""

    success: bool
    result: ReqCloseServerParsedMsgData
    msg_id: int = msgspec.interfaces.reqCloseServer.id
    text: str = ""


class ReqCloseServerMsgParser(IMsgParser):
    """Парсер для Interfaces::reqCloseServer."""

    def parse(self, msg: Message) -> ReqCloseServerParsedMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = ReqCloseServerParsedMsgData(*values)
        return ReqCloseServerParsedMsgParserResult(success=True, result=pd)


@dataclass(frozen=True)
class OnRegisterNewAppMsgParserResult(MsgParserResult):
    """Результат парсинга Interfaces::onRegisterNewApp."""

    success: bool
    result: OnRegisterNewAppParsedMsgData
    msg_id: int = msgspec.interfaces.onRegisterNewApp.id
    text: str = ""


class OnRegisterNewAppMsgParser(IMsgParser):
    """Парсер для Interfaces::onRegisterNewApp."""

    def parse(self, msg: Message) -> OnRegisterNewAppMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnRegisterNewAppParsedMsgData(*values)
        return OnRegisterNewAppMsgParserResult(success=True, result=pd)


@dataclass(frozen=True)
class OnAppActiveTickMsgParserResult(MsgParserResult):
    """Результат парсинга Interfaces::onAppActiveTick."""

    success: bool
    result: OnAppActiveTickParsedMsgData
    msg_id: int = msgspec.interfaces.onAppActiveTick.id
    text: str = ""


class OnAppActiveTickMsgParser(IMsgParser):
    """Парсер для Interfaces::onAppActiveTick."""

    def parse(self, msg: Message) -> OnAppActiveTickMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnAppActiveTickParsedMsgData(*values)
        return OnAppActiveTickMsgParserResult(success=True, result=pd)


@dataclass
class OnAccountLoginParsedMsgData(ParsedMsgData):
    """Данные парсинга Interfaces::onAccountLogin."""

    component_id: KBEComponentId
    login: KBEString
    password: KBEString
    data: KBEBlob


@dataclass(frozen=True)
class OnAccountLoginMsgParserResult(MsgParserResult):
    """Результат парсинга Interfaces::onAccountLogin."""

    success: bool
    result: OnAccountLoginParsedMsgData
    msg_id: int = msgspec.interfaces.onAccountLogin.id
    text: str = ""


class OnAccountLoginMsgParser(IMsgParser):
    """Парсер для Interfaces::onAccountLogin."""

    def parse(self, msg: Message) -> OnAccountLoginMsgParserResult:
        """Парсинг сообщения Interfaces::onAccountLogin.

        :param msg: Сообщение для парсинга
        :return: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnAccountLoginParsedMsgData(*values)
        return OnAccountLoginMsgParserResult(success=True, result=pd)


@dataclass
class LookAppParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Interfaces::lookApp."""


@dataclass(frozen=True)
class LookAppMsgParserResult(MsgParserResult):
    """Результат парсинга Interfaces::lookApp."""

    success: bool
    result: LookAppParsedMsgData
    msg_id: int = msgspec.interfaces.lookApp.id
    text: str = ""


class LookAppMsgParser(IMsgParser):
    """Парсер для Interfaces::lookApp."""

    def parse(self, msg: Message) -> LookAppMsgParserResult:
        """Распарсить сообщение Interfaces::lookApp.

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
    """Распарсенные данные сообщения Interfaces::onLookApp."""

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
        return COMPONENT_STATE_BY_SHUTDOWN_STATE[ShutdownState(self.shutdownState)]

    __add_to_dict__: ClassVar = ("component_type", "component_state")


@dataclass(frozen=True)
class OnLookAppParserMsgParserResult(MsgParserResult):
    """Парсер для Interfaces::onLookApp."""

    success: bool
    result: OnLookAppParsedMsgData
    msg_id: int = msgspec.interfaces.onLookApp.id
    text: str = ""


class OnLookAppMsgParser(IMsgParser):
    """Парсер для Interfaces::onLookApp."""

    def parse(self, msg: Message) -> OnLookAppParserMsgParserResult:
        """Распарсить сообщение Interfaces::onLookApp.

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
class ReqCreateAccountParsedMsgData(ParsedMsgData):
    """Данные парсинга Interfaces::reqCreateAccount."""

    component_id: KBEComponentId
    registerName: KBEString  # noqa: N815
    password: KBEString
    accountType: int  # noqa: N815
    datas: KBEBlob

    @property
    def account_type(self) -> AccountType:
        """Тип аккаунта.

        Returns:
            AccountType: тип аккаунта.

        """
        return AccountType(self.accountType)

    __add_to_dict__: ClassVar[tuple[str, ...]] = ("account_type",)


@dataclass(frozen=True)
class ReqCreateAccountMsgParserResult(MsgParserResult):
    """Результат парсинга Interfaces::reqCreateAccount."""

    success: bool
    result: ReqCreateAccountParsedMsgData
    msg_id: int = msgspec.interfaces.reqCreateAccount.id
    text: str = ""


class ReqCreateAccountMsgParser(IMsgParser):
    """Парсер для Interfaces::reqCreateAccount."""

    def parse(self, msg: Message) -> ReqCreateAccountMsgParserResult:
        """Парсинг сообщения Interfaces::reqCreateAccount.

        :param msg: Сообщение для парсинга
        :return: Результат парсинга
        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = ReqCreateAccountParsedMsgData(*values)
        return ReqCreateAccountMsgParserResult(success=True, result=pd)


@dataclass
class ChargeParsedMsgData(ParsedMsgData):
    """Данные парсинга Interfaces::charge."""

    orderID: KBEString  # noqa: N815
    dbid: int
    accountName: KBEString  # noqa: N815
    gold: int


@dataclass(frozen=True)
class ChargeMsgParserResult(MsgParserResult):
    """Результат парсинга Interfaces::charge."""

    success: bool
    result: ChargeParsedMsgData
    msg_id: int = msgspec.interfaces.charge.id
    text: str = ""


class ChargeMsgParser(IMsgParser):
    """Парсер для Interfaces::charge."""

    def parse(self, msg: Message) -> ChargeMsgParserResult:
        """Парсинг сообщения Interfaces::charge.

        :param msg: Сообщение для парсинга
        :return: Результат парсинга
        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = ChargeParsedMsgData(*values)
        return ChargeMsgParserResult(success=True, result=pd)


@dataclass
class EraseClientReqParsedMsgData(ParsedMsgData):
    """Данные парсинга Interfaces::eraseClientReq."""

    dbid: int
    accountName: KBEString  # noqa: N815


@dataclass(frozen=True)
class EraseClientReqMsgParserResult(MsgParserResult):
    """Результат парсинга Interfaces::eraseClientReq."""

    success: bool
    result: EraseClientReqParsedMsgData
    msg_id: int = msgspec.interfaces.eraseClientReq.id
    text: str = ""


class EraseClientReqMsgParser(IMsgParser):
    """Парсер для Interfaces::eraseClientReq."""

    def parse(self, msg: Message) -> EraseClientReqMsgParserResult:
        """Парсинг сообщения Interfaces::eraseClientReq.

        :param msg: Сообщение для парсинга
        :return: Результат парсинга
        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = EraseClientReqParsedMsgData(*values)
        return EraseClientReqMsgParserResult(success=True, result=pd)


@dataclass
class ReqKillServerParsedMsgData(ParsedMsgData):
    """Данные парсинга Interfaces::reqKillServer."""

    componentType: KBEString  # noqa: N815
    componentID: int  # noqa: N815


@dataclass(frozen=True)
class ReqKillServerMsgParserResult(MsgParserResult):
    """Результат парсинга Interfaces::reqKillServer."""

    success: bool
    result: ReqKillServerParsedMsgData
    msg_id: int = msgspec.interfaces.reqKillServer.id
    text: str = ""


class ReqKillServerMsgParser(IMsgParser):
    """Парсер для Interfaces::reqKillServer."""

    def parse(self, msg: Message) -> ReqKillServerMsgParserResult:
        """Парсинг сообщения Interfaces::reqKillServer.

        :param msg: Сообщение для парсинга
        :return: Результат парсинга
        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = ReqKillServerParsedMsgData(*values)
        return ReqKillServerMsgParserResult(success=True, result=pd)


@dataclass
class OnExecuteRawDatabaseCommandCBParsedMsgData(ParsedMsgData):
    """Данные парсинга Interfaces::onExecuteRawDatabaseCommandCB."""

    id: int
    result: KBEBlob


@dataclass(frozen=True)
class OnExecuteRawDatabaseCommandCBMsgParserResult(MsgParserResult):
    """Результат парсинга Interfaces::onExecuteRawDatabaseCommandCB."""

    success: bool
    result: OnExecuteRawDatabaseCommandCBParsedMsgData
    msg_id: int = msgspec.interfaces.onExecuteRawDatabaseCommandCB.id
    text: str = ""


class OnExecuteRawDatabaseCommandCBMsgParser(IMsgParser):
    """Парсер для Interfaces::onExecuteRawDatabaseCommandCB."""

    def parse(self, msg: Message) -> OnExecuteRawDatabaseCommandCBMsgParserResult:
        """Парсинг сообщения Interfaces::onExecuteRawDatabaseCommandCB.

        :param msg: Сообщение для парсинга
        :return: Результат парсинга
        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnExecuteRawDatabaseCommandCBParsedMsgData(*values)
        return OnExecuteRawDatabaseCommandCBMsgParserResult(success=True, result=pd)


@dataclass
class QueryWatcherParsedMsgData(ParsedMsgData):
    """Данные парсинга Interfaces::queryWatcher."""

    path: KBEString


@dataclass(frozen=True)
class QueryWatcherMsgParserResult(MsgParserResult):
    """Результат парсинга Interfaces::queryWatcher."""

    success: bool
    result: QueryWatcherParsedMsgData
    msg_id: int = msgspec.interfaces.queryWatcher.id
    text: str = ""


class QueryWatcherMsgParser(IMsgParser):
    """Парсер для Interfaces::queryWatcher."""

    def parse(self, msg: Message) -> QueryWatcherMsgParserResult:
        """Парсинг сообщения Interfaces::queryWatcher.

        :param msg: Сообщение для парсинга
        :return: Результат парсинга
        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = QueryWatcherParsedMsgData(*values)
        return QueryWatcherMsgParserResult(success=True, result=pd)
