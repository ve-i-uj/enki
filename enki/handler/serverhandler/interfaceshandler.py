"""Обработчик сообщений от компонента Interfaces."""

import logging
from dataclasses import dataclass

from enki.core import msgspec
from enki.core.message import Message
from enki.misc import devonly

from ..base import Handler, HandlerResult, ParsedMsgData
from .common import OnAppActiveTickParsedData, OnRegisterNewAppParsedData

logger = logging.getLogger(__file__)


@dataclass
class ReqCloseServerParsedData(ParsedMsgData):
    pass


@dataclass
class ReqCloseServerHandlerResult(HandlerResult):
    """Обработчик для Interfaces::onRegisterNewApp."""
    success: bool
    result: ReqCloseServerParsedData
    msg_id: int = msgspec.app.interfaces.reqCloseServer.id
    text: str = ''


class ReqCloseServerHandler(Handler):

    def handle(self, msg: Message) -> ReqCloseServerHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = ReqCloseServerParsedData(*msg.get_values())
        return ReqCloseServerHandlerResult(True, pd)


@dataclass
class OnRegisterNewAppHandlerResult(HandlerResult):
    """Обработчик для Interfaces::onRegisterNewApp."""
    success: bool
    result: OnRegisterNewAppParsedData
    msg_id: int = msgspec.app.interfaces.onRegisterNewApp.id
    text: str = ''


class OnRegisterNewAppHandler(Handler):

    def handle(self, msg: Message) -> OnRegisterNewAppHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnRegisterNewAppParsedData(*msg.get_values())
        return OnRegisterNewAppHandlerResult(True, pd)


@dataclass
class OnAppActiveTickHandlerResult(HandlerResult):
    """Обработчик для DBMgr::onAppActiveTick."""
    success: bool
    result: OnAppActiveTickParsedData
    msg_id: int = msgspec.app.interfaces.onAppActiveTick.id
    text: str = ''


class OnAppActiveTickHandler(Handler):

    def handle(self, msg: Message) -> OnAppActiveTickHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnAppActiveTickParsedData(*msg.get_values())
        return OnAppActiveTickHandlerResult(True, pd)
