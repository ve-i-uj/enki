"""Парсер сообщений от компонента CellappMgr."""

import logging
from dataclasses import dataclass
from typing import Any

from enki import msgspec
from enki.msg.message import Message
from enki.misc import devonly

from .imsg_parser import ParsedMsgData, MsgParserResult, IMsgParser
from .common import (
    CreateCellEntityInNewSpaceFromBaseappParsedMsgData,
    CreateCellEntityInNewSpaceFromBaseappParser,
    LookAppParsedMsgData,
    OnAppActiveTickParsedMsgData,
    OnRegisterNewAppParsedMsgData,
)

logger = logging.getLogger(__file__)


@dataclass
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


@dataclass
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


@dataclass
class LookAppMsgResult(MsgParserResult):
    """Результат парсинга CellappMgr::lookApp."""

    success: bool
    result: LookAppParsedMsgData
    msg_id: int = msgspec.cellappmgr.lookApp.id
    text: str = ""


class LookAppMsgParser(IMsgParser):
    """Парсер для CellappMgr::lookApp."""
    
    def parse(self, msg: Message) -> LookAppMsgResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = LookAppParsedMsgData(*values)
        return LookAppMsgResult(True, pd)


@dataclass
class UpdateCellappParsedData(ParsedMsgData):
    """Данные CellappMgr::updateCellapp."""
    
    componentID: int
    numEntities: int
    load: float
    flags: int


@dataclass
class UpdateCellappMsgResult(MsgParserResult):
    """Результат парсинга CellappMgr::updateCellapp."""

    success: bool
    result: UpdateCellappParsedData
    msg_id: int = msgspec.cellappmgr.updateCellapp.id
    text: str = ""


class UpdateCellappMsgParser(IMsgParser):
    """Парсер для CellappMgr::updateCellapp."""
    
    def parse(self, msg: Message) -> UpdateCellappMsgResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = UpdateCellappParsedData(*values)
        return UpdateCellappMsgResult(True, pd)


@dataclass
class UpdateSpaceDataParsedData(ParsedMsgData):
    """Данные CellappMgr::updateSpaceData."""
    
    componentID: int
    spaceID: int
    scriptModuleName: str
    delspace: bool
    geomappingPath: str


@dataclass
class UpdateSpaceDataMsgResult(MsgParserResult):
    """Результат парсинга CellappMgr::updateSpaceData."""

    success: bool
    result: UpdateSpaceDataParsedData
    msg_id: int = msgspec.cellappmgr.updateSpaceData.id
    text: str = ""


class UpdateSpaceDataMsgParser(IMsgParser):
    """Парсер для CellappMgr::updateSpaceData."""
    
    def parse(self, msg: Message) -> UpdateSpaceDataMsgResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = UpdateSpaceDataParsedData(*values)
        return UpdateSpaceDataMsgResult(True, pd)


@dataclass
class ReqCreateCellEntityInNewSpaceMsgResult(MsgParserResult):
    """Результат парсинга CellappMgr::reqCreateCellEntityInNewSpace."""

    success: bool
    result: CreateCellEntityInNewSpaceFromBaseappParsedMsgData
    msg_id: int = msgspec.cellappmgr.reqCreateCellEntityInNewSpace.id
    text: str = ""


class ReqCreateCellEntityInNewSpaceMsgParser(IMsgParser):
    """Парсер для CellappMgr::reqCreateCellEntityInNewSpace."""
    
    def parse(self, msg: Message) -> ReqCreateCellEntityInNewSpaceMsgResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        pd = CreateCellEntityInNewSpaceFromBaseappParser().parse(msg)
        return ReqCreateCellEntityInNewSpaceMsgResult(True, pd)
