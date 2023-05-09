"""Обработчик сообщений от компонента DBMgr."""

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
class OnRegisterNewAppHandlerResult(base.HandlerResult):
    """Обработчик для DBMgr::onRegisterNewApp."""
    success: bool
    result: OnRegisterNewAppParsedData
    msg_id: int = msgspec.app.dbmgr.onRegisterNewApp.id
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
    msg_id: int = msgspec.app.dbmgr.onAppActiveTick.id
    text: str = ''


class OnAppActiveTickHandler(base.Handler):

    def handle(self, msg: Message) -> OnAppActiveTickHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnAppActiveTickParsedData(*msg.get_values())
        return OnAppActiveTickHandlerResult(True, pd)
