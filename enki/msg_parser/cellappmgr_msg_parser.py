"""Парсер сообщений от компонента CellappMgr."""

import logging
from dataclasses import dataclass
from typing import Any

from enki import msgspec
from enki.misc import devonly
from enki.msg.message import Message

from .common import (
    CreateCellEntityInNewSpaceFromBaseappParsedMsgData,
    CreateCellEntityInNewSpaceFromBaseappParser,
    LookAppParsedMsgData,
    OnAppActiveTickParsedMsgData,
    OnRegisterNewAppParsedMsgData,
)
from .imsg_parser import IMsgParser, MsgParserResult, ParsedMsgData

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OnAppActiveTickMsgParserResult(MsgParserResult):
    """Результат парсинга CellappMgr::onAppActiveTick."""

    success: bool
    result: OnAppActiveTickParsedMsgData
    msg_id: int = msgspec.cellappmgr.onAppActiveTick.id
    text: str = ""


class OnAppActiveTickMsgParser(IMsgParser):
    """Парсер для CellappMgr::onAppActiveTick."""

    def parse(self, msg: Message) -> OnAppActiveTickMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnAppActiveTickParsedMsgData(*values)
        return OnAppActiveTickMsgParserResult(True, pd)


@dataclass(frozen=True)
class OnRegisterNewAppMsgParserResult(MsgParserResult):
    """Результат парсинга CellappMgr::onRegisterNewApp."""

    success: bool
    result: OnRegisterNewAppParsedMsgData
    msg_id: int = msgspec.cellappmgr.onRegisterNewApp.id
    text: str = ""


class OnRegisterNewAppMsgParser(IMsgParser):
    """Парсер для CellappMgr::onRegisterNewApp."""

    def parse(self, msg: Message) -> OnRegisterNewAppMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnRegisterNewAppParsedMsgData(*values)
        return OnRegisterNewAppMsgParserResult(True, pd)


@dataclass(frozen=True)
class LookAppMsgParserResult(MsgParserResult):
    """Результат парсинга CellappMgr::lookApp."""

    success: bool
    result: LookAppParsedMsgData
    msg_id: int = msgspec.cellappmgr.lookApp.id
    text: str = ""


class LookAppMsgParser(IMsgParser):
    """Парсер для CellappMgr::lookApp."""

    def parse(self, msg: Message) -> LookAppMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = LookAppParsedMsgData(*values)
        return LookAppMsgParserResult(True, pd)


@dataclass
class UpdateCellappParsedMsgData(ParsedMsgData):
    """Данные CellappMgr::updateCellapp."""

    componentID: int
    numEntities: int
    load: float
    flags: int


@dataclass(frozen=True)
class UpdateCellappMsgParserResult(MsgParserResult):
    """Результат парсинга CellappMgr::updateCellapp."""

    success: bool
    result: UpdateCellappParsedMsgData
    msg_id: int = msgspec.cellappmgr.updateCellapp.id
    text: str = ""


class UpdateCellappMsgParser(IMsgParser):
    """Парсер для CellappMgr::updateCellapp."""

    def parse(self, msg: Message) -> UpdateCellappMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = UpdateCellappParsedMsgData(*values)
        return UpdateCellappMsgParserResult(True, pd)


@dataclass
class UpdateSpaceDataParsedMsgData(ParsedMsgData):
    """Данные CellappMgr::updateSpaceData."""

    componentID: int
    spaceID: int
    scriptModuleName: str
    delspace: bool
    geomappingPath: str


@dataclass(frozen=True)
class UpdateSpaceDataMsgParserResult(MsgParserResult):
    """Результат парсинга CellappMgr::updateSpaceData."""

    success: bool
    result: UpdateSpaceDataParsedMsgData
    msg_id: int = msgspec.cellappmgr.updateSpaceData.id
    text: str = ""


class UpdateSpaceDataMsgParser(IMsgParser):
    """Парсер для CellappMgr::updateSpaceData."""

    def parse(self, msg: Message) -> UpdateSpaceDataMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = UpdateSpaceDataParsedMsgData(*values)
        return UpdateSpaceDataMsgParserResult(True, pd)


@dataclass(frozen=True)
class ReqCreateCellEntityInNewSpaceMsgParserResult(MsgParserResult):
    """Результат парсинга CellappMgr::reqCreateCellEntityInNewSpace."""

    success: bool
    result: CreateCellEntityInNewSpaceFromBaseappParsedMsgData
    msg_id: int = msgspec.cellappmgr.reqCreateCellEntityInNewSpace.id
    text: str = ""


class ReqCreateCellEntityInNewSpaceMsgParser(IMsgParser):
    """Парсер для CellappMgr::reqCreateCellEntityInNewSpace."""

    def parse(self, msg: Message) -> ReqCreateCellEntityInNewSpaceMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        pd = CreateCellEntityInNewSpaceFromBaseappParser().parse(msg)
        return ReqCreateCellEntityInNewSpaceMsgParserResult(True, pd)
