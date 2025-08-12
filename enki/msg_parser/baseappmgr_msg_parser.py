"""Парсер сообщений от компонента BaseappMgr."""

import logging
from dataclasses import dataclass
from typing import Any

from enki import msgspec
from enki.kbetype.decoders.custom_decoders import KBEComponentId
from enki.msg.message import Message
from enki.misc import devonly
from enki.msg_parser.common import CreateEntityAnywhereMsgParser, \
    OnAppActiveTickParsedMsgData, OnRegisterNewAppParsedMsgData, \
        CreateEntityAnywhereParsedMsgData

from .imsg_parser import ParsedMsgData, MsgParserResult, IMsgParser

logger = logging.getLogger(__file__)


@dataclass
class OnAppActiveTickMsgParserResult(MsgParserResult):
    """Результат парсинга BaseappMgr::onAppActiveTick."""
    success: bool
    result: OnAppActiveTickParsedMsgData
    msg_id: int = msgspec.baseappmgr.onAppActiveTick.id
    text: str = ''


class OnAppActiveTickMsgParser(IMsgParser):
    """Парсер для BaseappMgr::onAppActiveTick."""

    def parse(self, msg: Message) -> OnAppActiveTickMsgParserResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnAppActiveTickParsedMsgData(*values)
        return OnAppActiveTickMsgParserResult(True, pd)


@dataclass
class OnRegisterNewAppMsgParserResult(MsgParserResult):
    """Результат парсинга BaseappMgr::onRegisterNewApp."""
    success: bool
    result: OnRegisterNewAppParsedMsgData
    msg_id: int = msgspec.baseappmgr.onRegisterNewApp.id
    text: str = ''


class OnRegisterNewAppMsgParser(IMsgParser):
    """Парсер BaseappMgr::onRegisterNewApp."""

    def parse(self, msg: Message) -> OnRegisterNewAppMsgParserResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnRegisterNewAppParsedMsgData(*values)
        return OnRegisterNewAppMsgParserResult(True, pd)


@dataclass
class UpdateBaseappParsedMsgData(ParsedMsgData):
    componentID: KBEComponentId
    numBases: int
    numProxices: int
    load: float
    flags: int


@dataclass
class UpdateBaseappMsgParserResult(MsgParserResult):
    """Парсер для BaseappMgr::updateBaseapp."""
    success: bool
    result: UpdateBaseappParsedMsgData
    msg_id: int = msgspec.baseappmgr.updateBaseapp.id
    text: str = ''


class UpdateBaseappMsgParser(IMsgParser):
    """Парсер для BaseappMgr::updateBaseapp."""

    def parse(self, msg: Message) -> UpdateBaseappMsgParserResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = UpdateBaseappParsedMsgData(*values)
        return UpdateBaseappMsgParserResult(True, pd)


@dataclass
class OnBaseappInitProgressParsedMsgData(ParsedMsgData):
    cid: int
    flags: int


@dataclass
class OnBaseappInitProgressMsgParserResult(MsgParserResult):
    """Парсер для BaseappMgr::onBaseappInitProgress."""
    success: bool
    result: OnBaseappInitProgressParsedMsgData
    msg_id: int = msgspec.baseappmgr.onBaseappInitProgress.id
    text: str = ''


class OnBaseappInitProgressMsgParser(IMsgParser):

    def parse(self, msg: Message) -> OnBaseappInitProgressMsgParserResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnBaseappInitProgressParsedMsgData(*values)
        return OnBaseappInitProgressMsgParserResult(True, pd)


@dataclass
class ReqCreateEntityAnywhereMsgParserResult(MsgParserResult):
    """Парсер для BaseappMgr::reqCreateEntityAnywhere."""
    success: bool
    result: CreateEntityAnywhereParsedMsgData | None
    msg_id: int = msgspec.baseappmgr.reqCreateEntityAnywhere.id
    text: str = ''


class ReqCreateEntityAnywhereMsgParser(IMsgParser):
    """Парсер для BaseappMgr::reqCreateEntityAnywhere."""

    def parse(self, msg: Message) -> ReqCreateEntityAnywhereMsgParserResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        result = CreateEntityAnywhereMsgParser().parse(msg)
        return ReqCreateEntityAnywhereMsgParserResult(
            success=result.success, 
            result=result.result,
            text=result.text
        )
