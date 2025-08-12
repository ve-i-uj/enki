"""Обработчик сообщений от компонента Logger."""

import logging
from dataclasses import dataclass
from typing import Any, ClassVar

from enki import msgspec
from enki.kbeenum import ComponentType
from enki.kbetype.decoders.custom_decoders import KBEComponentId, KBEComponentOrderId, KBEComponentType, KBEEndlessBlob, KBEGameTime, KBEUid
from enki.kbetype.pytypes.basic_data_types import KBEInt64, KBEUInt32
from enki.misc import devonly
from enki.msg.message import Message
from enki.msg_parser.common import OnRegisterNewAppParsedMsgData
from enki.msg_parser.imsg_parser import IMsgParser, MsgParserResult, ParsedMsgData

logger = logging.getLogger(__name__)


@dataclass
class OnAppActiveTickParsedMsgData(ParsedMsgData):
    """Распарсенное сообщение Logger::onAppActiveTick."""

    componentType: KBEComponentType  # noqa: N815  # pylint: disable=invalid-name
    componentID: KBEComponentId  # noqa: N815  # pylint: disable=invalid-name

    @property
    def component_type(self) -> ComponentType:
        """Энам отражающий значение componentType.

        Returns:
            ComponentType: тип компонента

        """
        return ComponentType(self.componentType)

    __add_to_dict__: ClassVar = ["component_type"]


@dataclass
class OnAppActiveTickMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Logger::onAppActiveTick."""

    success: bool
    result: OnAppActiveTickParsedMsgData
    msg_id: int = msgspec.logger.onAppActiveTick.id
    text: str = ""


class OnAppActiveTickMsgParser(IMsgParser):
    """Парсер для Logger::onAppActiveTick."""

    def parse(self, msg: Message) -> OnAppActiveTickMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnAppActiveTickParsedMsgData(*values)
        return OnAppActiveTickMsgParserResult(success=True, result=pd)


@dataclass
class OnRegisterNewAppMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Logger::onRegisterNewApp."""

    success: bool
    result: OnRegisterNewAppParsedMsgData
    msg_id: int = msgspec.logger.onRegisterNewApp.id
    text: str = ""


class OnRegisterNewAppMsgParser(IMsgParser):
    """Парсер для Logger::onRegisterNewApp."""

    def parse(self, msg: Message) -> OnRegisterNewAppMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnRegisterNewAppParsedMsgData(*values)
        return OnRegisterNewAppMsgParserResult(True, pd)



@dataclass
class WriteLogParsedMsgData(ParsedMsgData):
    """Распарсенное сообщение Logger::writeLog."""
    uid: KBEUid
    logtype: KBEUInt32
    componentType: KBEComponentType  # noqa: N815  # pylint: disable=invalid-name
    componentID: KBEComponentId  # noqa: N815  # pylint: disable=invalid-name
    globalorderID: KBEComponentOrderId  # noqa: N815  # pylint: disable=invalid-name
    grouporderID: KBEComponentOrderId  # noqa: N815  # pylint: disable=invalid-name
    time: KBEInt64
    kbetime: KBEGameTime
    log_size_and_text: KBEEndlessBlob

    @property
    def component_type(self) -> ComponentType:
        """Энам отражающий значение componentType.

        Returns:
            ComponentType: тип компонента

        """
        return ComponentType(self.componentType)

    __add_to_dict__: ClassVar = ["component_type"]


@dataclass
class WriteLogMsgParserResult(MsgParserResult):
    """Результат парсера Logger::writeLog."""
    success: bool
    result: WriteLogParsedMsgData
    msg_id: int = msgspec.logger.writeLog.id
    text: str = ''


class WriteLogMsgParser(IMsgParser):
    """Парсер для Logger::writeLog."""

    def parse(self, msg: Message) -> WriteLogMsgParserResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = WriteLogParsedMsgData(*values)
        return WriteLogMsgParserResult(success=True, result=pd)
