"""Обработчик сообщений от компонента Interfaces."""

import logging
from dataclasses import dataclass

from enki.core import msgspec
from enki.core.message import Message
from enki.misc import devonly

from ..imsgparser import Handler, MsgParserResult, ParsedMsgData
from .common import OnAppActiveTickParsedData, OnRegisterNewAppParsedData

logger = logging.getLogger(__file__)


@dataclass
class ReqCloseServerParsedData(ParsedMsgData):
    pass


@dataclass
class ReqCloseServerMsgResult(MsgParserResult):
    """Обработчик для Interfaces::onRegisterNewApp."""
    success: bool
    result: ReqCloseServerParsedData
    msg_id: int = msgspec.app.interfaces.reqCloseServer.id
    text: str = ''


class ReqCloseServerMsgParser(IMsgParser):

    def parse(self, msg: Message) -> ReqCloseServerMsgResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = ReqCloseServerParsedData(*msg.get_values())
        return ReqCloseServerMsgResult(True, pd)


@dataclass
class OnRegisterNewAppMsgResult(MsgParserResult):
    """Обработчик для Interfaces::onRegisterNewApp."""
    success: bool
    result: OnRegisterNewAppParsedData
    msg_id: int = msgspec.app.interfaces.onRegisterNewApp.id
    text: str = ''


class OnRegisterNewAppMsgParser(IMsgParser):

    def parse(self, msg: Message) -> OnRegisterNewAppMsgResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnRegisterNewAppParsedData(*msg.get_values())
        return OnRegisterNewAppMsgResult(True, pd)


@dataclass
class OnAppActiveTickMsgResult(MsgParserResult):
    """Обработчик для Interfaces::onAppActiveTick."""
    success: bool
    result: OnAppActiveTickParsedData
    msg_id: int = msgspec.app.interfaces.onAppActiveTick.id
    text: str = ''


class OnAppActiveTickMsgParser(IMsgParser):

    def parse(self, msg: Message) -> OnAppActiveTickMsgResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnAppActiveTickParsedData(*msg.get_values())
        return OnAppActiveTickMsgResult(True, pd)
