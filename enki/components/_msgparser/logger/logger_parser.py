
"""Обработчик сообщений от компонента Logger."""

import logging
from dataclasses import dataclass

from enki.core import kbemath
from enki.misc import result
from enki.core import msgspec
from enki.core.message import Message
from enki import kbeenum
from enki.misc import devonly

from ..imsgparser import ParsedMsgData, MsgParserResult, Handler
from .common import OnRegisterNewAppParsedData


logger = logging.getLogger(__file__)


@dataclass
class WriteLogParsedData(ParsedMsgData):
    uid: int
    logtype: int
    componentType: int
    componentID: int
    globalOrder: int
    groupOrder: int
    time: int
    kbetime: int
    msgs: bytes

    @property
    def component_type(self) -> kbeenum.ComponentType:
        try:
            return kbeenum.ComponentType(self.componentType)
        except ValueError:
            return kbeenum.ComponentType.UNKNOWN_COMPONENT

    __add_to_dict__ = [
        'component_type'
    ]


@dataclass
class WriteLogMsgResult(MsgParserResult):
    """Обработчик для Logger::writeLog."""
    success: bool
    result: WriteLogParsedData
    msg_id: int = msgspec.app.logger.writeLog.id
    text: str = ''


class WriteLogMsgParser(IMsgParser):

    def parse(self, msg: Message) -> WriteLogMsgResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = WriteLogParsedData(*msg.get_values())
        return WriteLogMsgResult(True, pd)


@dataclass
class OnAppActiveTickParsedData(ParsedMsgData):
    componentType: int
    componentID: int

    @property
    def component_type(self) -> kbeenum.ComponentType:
        return kbeenum.ComponentType(self.componentType)

    __add_to_dict__ = [
        'component_type'
    ]


@dataclass
class OnRegisterNewAppMsgResult(MsgParserResult):
    """Обработчик для Logger::onRegisterNewApp."""
    success: bool
    result: OnRegisterNewAppParsedData
    msg_id: int = msgspec.app.logger.onRegisterNewApp.id
    text: str = ''


class OnRegisterNewAppMsgParser(IMsgParser):

    def parse(self, msg: Message) -> OnRegisterNewAppMsgResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnRegisterNewAppParsedData(*msg.get_values())
        return OnRegisterNewAppMsgResult(True, pd)


@dataclass
class OnAppActiveTickMsgResult(MsgParserResult):
    """Обработчик для Logger::onAppActiveTick."""
    success: bool
    result: OnAppActiveTickParsedData
    msg_id: int = msgspec.app.logger.onAppActiveTick.id
    text: str = ''


class OnAppActiveTickMsgParser(IMsgParser):

    def parse(self, msg: Message) -> OnAppActiveTickMsgResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnAppActiveTickParsedData(*msg.get_values())
        return OnAppActiveTickMsgResult(True, pd)
