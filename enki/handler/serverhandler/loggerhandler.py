"""Обработчик сообщений от компонента Logger."""

import logging
from dataclasses import dataclass

from enki.core import kbeenum, kbemath
from enki.core import enkitype
from enki.core import msgspec
from enki.core.message import Message
from enki.misc import devonly

from ..base import ParsedMsgData, HandlerResult, Handler
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
class WriteLogHandlerResult(HandlerResult):
    """Обработчик для Logger::writeLog."""
    success: bool
    result: WriteLogParsedData
    msg_id: int = msgspec.app.logger.writeLog.id
    text: str = ''


class WriteLogHandler(Handler):

    def handle(self, msg: Message) -> WriteLogHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = WriteLogParsedData(*msg.get_values())
        return WriteLogHandlerResult(True, pd)


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
class OnAppActiveTickHandlerResult(HandlerResult):
    """Обработчик для DBMgr::onAppActiveTick."""
    success: bool
    result: OnAppActiveTickParsedData
    msg_id: int = msgspec.app.dbmgr.onAppActiveTick.id
    text: str = ''


class OnAppActiveTickHandler(Handler):

    def handle(self, msg: Message) -> OnAppActiveTickHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnAppActiveTickParsedData(*msg.get_values())
        return OnAppActiveTickHandlerResult(True, pd)


@dataclass
class OnRegisterNewAppHandlerResult(HandlerResult):
    """Обработчик для Logger::onRegisterNewApp."""
    success: bool
    result: OnRegisterNewAppParsedData
    msg_id: int = msgspec.app.logger.onRegisterNewApp.id
    text: str = ''


class OnRegisterNewAppHandler(Handler):

    def handle(self, msg: Message) -> OnRegisterNewAppHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnRegisterNewAppParsedData(*msg.get_values())
        return OnRegisterNewAppHandlerResult(True, pd)
