"""Обработчик сообщений от компонента Loginapp."""

import logging
from dataclasses import dataclass

from enki.core import msgspec
from enki.core.message import Message
from enki.misc import devonly

from ..imsgparser import ParsedMsgData, MsgParserResult, Handler
from .common import OnAppActiveTickParsedData, OnDbmgrInitCompletedParsedData


logger = logging.getLogger(__file__)


@dataclass
class OnDbmgrInitCompletedMsgResult(MsgParserResult):
    """Обработчик для Loginapp::onDbmgrInitCompleted."""
    success: bool
    result: OnDbmgrInitCompletedParsedData
    msg_id: int = msgspec.app.loginapp.onDbmgrInitCompleted.id
    text: str = ''


class OnDbmgrInitCompletedMsgParser(IMsgParser):

    def parse(self, msg: Message) -> OnDbmgrInitCompletedMsgResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnDbmgrInitCompletedParsedData(*msg.get_values())
        return OnDbmgrInitCompletedMsgResult(True, pd)


@dataclass
class OnBaseappInitProgressParsedData(ParsedMsgData):
    progress: float


@dataclass
class OnBaseappInitProgressMsgResult(MsgParserResult):
    """Обработчик для Loginapp::onBaseappInitProgress."""
    success: bool
    result: OnBaseappInitProgressParsedData
    msg_id: int = msgspec.app.loginapp.onBaseappInitProgress.id
    text: str = ''


class OnBaseappInitProgressMsgParser(IMsgParser):

    def parse(self, msg: Message) -> OnBaseappInitProgressMsgResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnBaseappInitProgressParsedData(*msg.get_values())
        return OnBaseappInitProgressMsgResult(True, pd)


@dataclass
class OnAppActiveTickMsgResult(MsgParserResult):
    """Обработчик для Loginapp::onAppActiveTick."""
    success: bool
    result: OnAppActiveTickParsedData
    msg_id: int = msgspec.app.baseapp.onAppActiveTick.id
    text: str = ''


class OnAppActiveTickMsgParser(IMsgParser):

    def parse(self, msg: Message) -> OnAppActiveTickMsgResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnAppActiveTickParsedData(*msg.get_values())
        return OnAppActiveTickMsgResult(True, pd)
