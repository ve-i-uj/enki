"""Обработчик сообщений от компонента Interfaces."""

import logging
from dataclasses import dataclass

from enki import enkitype, kbeenum, kbemath
from enki.net import msgspec
from enki.net.kbeclient import Message
from enki.misc import devonly

from . import base
from .common import OnAppActiveTickParsedData, OnRegisterNewAppParsedData

logger = logging.getLogger(__file__)


@dataclass
class ReqCloseServerParsedData(base.ParsedMsgData):
    pass


@dataclass
class ReqCloseServerHandlerResult(base.HandlerResult):
    """Обработчик для Interfaces::onRegisterNewApp."""
    success: bool
    result: ReqCloseServerParsedData
    msg_id: int = msgspec.app.interfaces.reqCloseServer.id
    text: str = ''


class ReqCloseServerHandler(base.Handler):

    def handle(self, msg: Message) -> ReqCloseServerHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = ReqCloseServerParsedData(*msg.get_values())
        return ReqCloseServerHandlerResult(True, pd)


@dataclass
class OnRegisterNewAppHandlerResult(base.HandlerResult):
    """Обработчик для Interfaces::onRegisterNewApp."""
    success: bool
    result: OnRegisterNewAppParsedData
    msg_id: int = msgspec.app.interfaces.onRegisterNewApp.id
    text: str = ''


class OnRegisterNewAppHandler(base.Handler):

    def handle(self, msg: Message) -> OnRegisterNewAppHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnRegisterNewAppParsedData(*msg.get_values())
        return OnRegisterNewAppHandlerResult(True, pd)


@dataclass
class OnAppActiveTickHandlerResult(base.HandlerResult):
    """Обработчик для DBMgr::onAppActiveTick."""
    success: bool
    result: OnAppActiveTickParsedData
    msg_id: int = msgspec.app.interfaces.onAppActiveTick.id
    text: str = ''


class OnAppActiveTickHandler(base.Handler):

    def handle(self, msg: Message) -> OnAppActiveTickHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnAppActiveTickParsedData(*msg.get_values())
        return OnAppActiveTickHandlerResult(True, pd)
