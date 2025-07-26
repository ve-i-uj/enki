"""Обработчик сообщений от компонента Logger."""

import logging
from dataclasses import dataclass
from typing import Any, ClassVar

from enki import kbeenum
from enki import msgspec
from enki.misc import devonly
from enki.msg.message import Message
from enki.msg_parser.imsg_parser import IMsgParser, MsgParserResult, ParsedMsgData


logger = logging.getLogger(__file__)


@dataclass
class OnAppActiveTickParsedData(ParsedMsgData):
    """Распарсенное сообщение Logger::onAppActiveTick."""

    componentType: int  # noqa: N815  # pylint: disable=invalid-name
    componentID: int  # noqa: N815  # pylint: disable=invalid-name

    @property
    def component_type(self) -> kbeenum.ComponentType:
        """Энам отражающий значение componentType.

        Returns:
            kbeenum.ComponentType: тип компонента
        """
        try:
            return kbeenum.ComponentType(self.componentType)
        except ValueError:
            return kbeenum.ComponentType.UNKNOWN_COMPONENT

    __add_to_dict__: ClassVar = ["component_type"]


@dataclass
class OnAppActiveTickMsgResult(MsgParserResult):
    """Результат парсера сообщения Logger::onAppActiveTick."""

    success: bool
    result: OnAppActiveTickParsedData
    msg_id: int = msgspec.logger.onAppActiveTick.id
    text: str = ""


class OnAppActiveTickMsgParser(IMsgParser):
    """Обработчик для Logger::onAppActiveTick."""

    def parse(self, msg: Message) -> OnAppActiveTickMsgResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnAppActiveTickParsedData(*values)
        return OnAppActiveTickMsgResult(True, pd)


@dataclass
class OnRegisterNewAppParsedData(ParsedMsgData):
    """Распарсенное сообщение Logger::onRegisterNewApp."""

    componentType: int  # noqa: N815  # pylint: disable=invalid-name
    componentID: int  # noqa: N815  # pylint: disable=invalid-name

    @property
    def component_type(self) -> kbeenum.ComponentType:
        """Энам отражающий значение componentType.

        Returns:
            kbeenum.ComponentType: тип компонента
        """
        try:
            return kbeenum.ComponentType(self.componentType)
        except ValueError:
            return kbeenum.ComponentType.UNKNOWN_COMPONENT

    __add_to_dict__: ClassVar = ["component_type"]


@dataclass
class OnRegisterNewAppMsgResult(MsgParserResult):
    """Результат парсера сообщения Logger::onRegisterNewApp."""

    success: bool
    result: OnRegisterNewAppParsedData
    msg_id: int = msgspec.logger.onRegisterNewApp.id
    text: str = ""


class OnRegisterNewAppMsgParser(IMsgParser):
    """Обработчик для Logger::onRegisterNewApp."""

    def parse(self, msg: Message) -> OnRegisterNewAppMsgResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnRegisterNewAppParsedData(*values)
        return OnRegisterNewAppMsgResult(True, pd)
