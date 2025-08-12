"""Парсеры сообщений от компонента Interfaces."""

import logging
from dataclasses import dataclass
from typing import Any

from enki import msgspec
from enki.misc import devonly
from enki.msg.message import Message

from .common import (
    OnAppActiveTickParsedMsgData,
    OnRegisterNewAppParsedMsgData,
    ReqCloseServerParsedMsgData,
)
from .imsg_parser import IMsgParser, MsgParserResult

logger = logging.getLogger(__name__)


@dataclass
class ReqCloseServerParsedMsgParserResult(MsgParserResult):
    """Результат парсинга Interfaces::reqCloseServer."""

    success: bool
    result: ReqCloseServerParsedMsgData
    msg_id: int = msgspec.interfaces.reqCloseServer.id
    text: str = ""


class ReqCloseServerMsgParser(IMsgParser):
    """Парсер для Interfaces::reqCloseServer."""

    def parse(self, msg: Message) -> ReqCloseServerParsedMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = ReqCloseServerParsedMsgData(*values)
        return ReqCloseServerParsedMsgParserResult(success=True, result=pd)


@dataclass
class OnRegisterNewAppMsgParserResult(MsgParserResult):
    """Результат парсинга Interfaces::onRegisterNewApp."""

    success: bool
    result: OnRegisterNewAppParsedMsgData
    msg_id: int = msgspec.interfaces.onRegisterNewApp.id
    text: str = ""


class OnRegisterNewAppMsgParser(IMsgParser):
    """Парсер для Interfaces::onRegisterNewApp."""

    def parse(self, msg: Message) -> OnRegisterNewAppMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnRegisterNewAppParsedMsgData(*values)
        return OnRegisterNewAppMsgParserResult(success=True, result=pd)


@dataclass
class OnAppActiveTickMsgParserResult(MsgParserResult):
    """Результат парсинга Interfaces::onAppActiveTick."""

    success: bool
    result: OnAppActiveTickParsedMsgData
    msg_id: int = msgspec.interfaces.onAppActiveTick.id
    text: str = ""


class OnAppActiveTickMsgParser(IMsgParser):
    """Парсер для Interfaces::onAppActiveTick."""

    def parse(self, msg: Message) -> OnAppActiveTickMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnAppActiveTickParsedMsgData(*values)
        return OnAppActiveTickMsgParserResult(success=True, result=pd)
