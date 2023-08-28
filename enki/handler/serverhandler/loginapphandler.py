"""Обработчик сообщений от компонента Loginapp."""

import logging
from dataclasses import dataclass

from enki.core import msgspec
from enki.core.message import Message
from enki.misc import devonly

from ..base import ParsedMsgData, HandlerResult, Handler
from .common import OnAppActiveTickParsedData, OnDbmgrInitCompletedParsedData


logger = logging.getLogger(__file__)


@dataclass
class OnDbmgrInitCompletedHandlerResult(HandlerResult):
    """Обработчик для Loginapp::onDbmgrInitCompleted."""
    success: bool
    result: OnDbmgrInitCompletedParsedData
    msg_id: int = msgspec.app.loginapp.onDbmgrInitCompleted.id
    text: str = ''


class OnDbmgrInitCompletedHandler(Handler):

    def handle(self, msg: Message) -> OnDbmgrInitCompletedHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnDbmgrInitCompletedParsedData(*msg.get_values())
        return OnDbmgrInitCompletedHandlerResult(True, pd)


@dataclass
class OnBaseappInitProgressParsedData(ParsedMsgData):
    progress: float


@dataclass
class OnBaseappInitProgressHandlerResult(HandlerResult):
    """Обработчик для Loginapp::onBaseappInitProgress."""
    success: bool
    result: OnBaseappInitProgressParsedData
    msg_id: int = msgspec.app.loginapp.onBaseappInitProgress.id
    text: str = ''


class OnBaseappInitProgressHandler(Handler):

    def handle(self, msg: Message) -> OnBaseappInitProgressHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnBaseappInitProgressParsedData(*msg.get_values())
        return OnBaseappInitProgressHandlerResult(True, pd)


@dataclass
class OnAppActiveTickHandlerResult(HandlerResult):
    """Обработчик для Loginapp::onAppActiveTick."""
    success: bool
    result: OnAppActiveTickParsedData
    msg_id: int = msgspec.app.baseapp.onAppActiveTick.id
    text: str = ''


class OnAppActiveTickHandler(Handler):

    def handle(self, msg: Message) -> OnAppActiveTickHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnAppActiveTickParsedData(*msg.get_values())
        return OnAppActiveTickHandlerResult(True, pd)
