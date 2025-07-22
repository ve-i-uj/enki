"""Обработчик сообщений от компонента BaseappMgr."""

import logging
from dataclasses import dataclass
import pickle

from enki.core import kbemath, kbetype
from enki.misc import result
from enki.core import msgspec
from enki.core.message import Message
from enki import kbeenum
from enki.misc import devonly

from ..imsgparser import ParsedMsgData, MsgParserResult, Handler
from .common import CreateEntityAnywhereParser, CreateEntityAnywhereParsedData, OnAppActiveTickParsedData, OnRegisterNewAppParsedData

logger = logging.getLogger(__file__)


@dataclass
class OnAppActiveTickMsgResult(MsgParserResult):
    """Обработчик для BaseappMgr::onAppActiveTick."""
    success: bool
    result: OnAppActiveTickParsedData
    msg_id: int = msgspec.app.baseappmgr.onAppActiveTick.id
    text: str = ''


class OnAppActiveTickMsgParser(IMsgParser):

    def parse(self, msg: Message) -> OnAppActiveTickMsgResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnAppActiveTickParsedData(*msg.get_values())
        return OnAppActiveTickMsgResult(True, pd)


@dataclass
class OnRegisterNewAppMsgResult(MsgParserResult):
    """Обработчик для BaseappMgr::onRegisterNewApp."""
    success: bool
    result: OnRegisterNewAppParsedData
    msg_id: int = msgspec.app.baseappmgr.onRegisterNewApp.id
    text: str = ''


class OnRegisterNewAppMsgParser(IMsgParser):

    def parse(self, msg: Message) -> OnRegisterNewAppMsgResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnRegisterNewAppParsedData(*msg.get_values())
        return OnRegisterNewAppMsgResult(True, pd)


@dataclass
class UpdateBaseappParsedData(ParsedMsgData):
    componentID: int
    numBases: int
    numProxices: int
    load: float
    flags: int


@dataclass
class UpdateBaseappMsgResult(MsgParserResult):
    """Обработчик для BaseappMgr::updateBaseapp."""
    success: bool
    result: UpdateBaseappParsedData
    msg_id: int = msgspec.app.baseappmgr.updateBaseapp.id
    text: str = ''


class UpdateBaseappMsgParser(IMsgParser):

    def parse(self, msg: Message) -> UpdateBaseappMsgResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = UpdateBaseappParsedData(*msg.get_values())
        return UpdateBaseappMsgResult(True, pd)


@dataclass
class OnBaseappInitProgressParsedData(ParsedMsgData):
    cid: int
    flags: int


@dataclass
class OnBaseappInitProgressMsgResult(MsgParserResult):
    """Обработчик для BaseappMgr::onBaseappInitProgress."""
    success: bool
    result: OnBaseappInitProgressParsedData
    msg_id: int = msgspec.app.baseappmgr.onBaseappInitProgress.id
    text: str = ''


class OnBaseappInitProgressMsgParser(IMsgParser):

    def parse(self, msg: Message) -> OnBaseappInitProgressMsgResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnBaseappInitProgressParsedData(*msg.get_values())
        return OnBaseappInitProgressMsgResult(True, pd)


@dataclass
class ReqCreateEntityAnywhereMsgResult(MsgParserResult):
    """Обработчик для BaseappMgr::reqCreateEntityAnywhere."""
    success: bool
    result: CreateEntityAnywhereParsedData
    msg_id: int = msgspec.app.baseappmgr.reqCreateEntityAnywhere.id
    text: str = ''


class ReqCreateEntityAnywhereMsgParser(IMsgParser):

    def parse(self, msg: Message) -> ReqCreateEntityAnywhereMsgResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = CreateEntityAnywhereParser().parse(msg)
        return ReqCreateEntityAnywhereMsgResult(True, pd)
