"""Обработчик сообщений от компонента BaseappMgr."""

import logging
from dataclasses import dataclass
import pickle

from enki.core import kbeenum, kbemath, kbetype
from enki.core import enkitype
from enki.core import msgspec
from enki.core.message import Message
from enki.misc import devonly

from ..base import ParsedMsgData, HandlerResult, Handler
from .common import CreateEntityAnywhereParser, CreateEntityAnywhereParsedData, OnAppActiveTickParsedData, OnRegisterNewAppParsedData

logger = logging.getLogger(__file__)


@dataclass
class OnAppActiveTickHandlerResult(HandlerResult):
    """Обработчик для BaseappMgr::onAppActiveTick."""
    success: bool
    result: OnAppActiveTickParsedData
    msg_id: int = msgspec.app.baseappmgr.onAppActiveTick.id
    text: str = ''


class OnAppActiveTickHandler(Handler):

    def handle(self, msg: Message) -> OnAppActiveTickHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnAppActiveTickParsedData(*msg.get_values())
        return OnAppActiveTickHandlerResult(True, pd)


@dataclass
class OnRegisterNewAppHandlerResult(HandlerResult):
    """Обработчик для BaseappMgr::onRegisterNewApp."""
    success: bool
    result: OnRegisterNewAppParsedData
    msg_id: int = msgspec.app.baseappmgr.onRegisterNewApp.id
    text: str = ''


class OnRegisterNewAppHandler(Handler):

    def handle(self, msg: Message) -> OnRegisterNewAppHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnRegisterNewAppParsedData(*msg.get_values())
        return OnRegisterNewAppHandlerResult(True, pd)


@dataclass
class UpdateBaseappParsedData(ParsedMsgData):
    componentID: int
    numBases: int
    numProxices: int
    load: float
    flags: int


@dataclass
class UpdateBaseappHandlerResult(HandlerResult):
    """Обработчик для BaseappMgr::updateBaseapp."""
    success: bool
    result: UpdateBaseappParsedData
    msg_id: int = msgspec.app.baseappmgr.updateBaseapp.id
    text: str = ''


class UpdateBaseappHandler(Handler):

    def handle(self, msg: Message) -> UpdateBaseappHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = UpdateBaseappParsedData(*msg.get_values())
        return UpdateBaseappHandlerResult(True, pd)


@dataclass
class OnBaseappInitProgressParsedData(ParsedMsgData):
    cid: int
    flags: int


@dataclass
class OnBaseappInitProgressHandlerResult(HandlerResult):
    """Обработчик для BaseappMgr::onBaseappInitProgress."""
    success: bool
    result: OnBaseappInitProgressParsedData
    msg_id: int = msgspec.app.baseappmgr.onBaseappInitProgress.id
    text: str = ''


class OnBaseappInitProgressHandler(Handler):

    def handle(self, msg: Message) -> OnBaseappInitProgressHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnBaseappInitProgressParsedData(*msg.get_values())
        return OnBaseappInitProgressHandlerResult(True, pd)


@dataclass
class ReqCreateEntityAnywhereHandlerResult(HandlerResult):
    """Обработчик для BaseappMgr::reqCreateEntityAnywhere."""
    success: bool
    result: CreateEntityAnywhereParsedData
    msg_id: int = msgspec.app.baseappmgr.reqCreateEntityAnywhere.id
    text: str = ''


class ReqCreateEntityAnywhereHandler(Handler):

    def handle(self, msg: Message) -> ReqCreateEntityAnywhereHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = CreateEntityAnywhereParser().parse(msg)
        return ReqCreateEntityAnywhereHandlerResult(True, pd)
