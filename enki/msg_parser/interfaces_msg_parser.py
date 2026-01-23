"""Парсеры сообщений от компонента Interfaces."""

import logging
from dataclasses import dataclass
from typing import Any, ClassVar

from enki import msgspec
from enki.kbeenum import (
    COMPONENT_STATE_BY_SHUTDOWN_STATE,
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
        return COMPONENT_STATE_BY_SHUTDOWN_STATE[
            ShutdownState(self.shutdownState)
        ]

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
