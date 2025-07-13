"""Обработчик сообщений от компонента CellappMgr."""

import logging
from dataclasses import dataclass

from enki.core import kbemath
from enki.misc import result
from enki.core import msgspec
from enki.core.message import Message
from enki import kbeenum
from enki.misc import devonly

from ..imsgparser import ParsedMsgData, MsgParserResult, Handler
from .common import CreateCellEntityInNewSpaceFromBaseappParsedData, \
    CreateCellEntityInNewSpaceFromBaseappParser, LookAppParsedData, \
    OnAppActiveTickParsedData, OnRegisterNewAppParsedData

logger = logging.getLogger(__file__)


@dataclass
class OnAppActiveTickMsgResult(MsgParserResult):
    """Обработчик для DBMgr::onAppActiveTick."""
    success: bool
    result: OnAppActiveTickParsedData
    msg_id: int = msgspec.app.cellappmgr.onAppActiveTick.id
    text: str = ''


class OnAppActiveTickMsgParser(IMsgParser):

    def parse(self, msg: Message) -> OnAppActiveTickMsgResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnAppActiveTickParsedData(*msg.get_values())
        return OnAppActiveTickMsgResult(True, pd)


@dataclass
class OnRegisterNewAppMsgResult(MsgParserResult):
    """Обработчик для CellappMgr::onRegisterNewApp."""
    success: bool
    result: OnRegisterNewAppParsedData
    msg_id: int = msgspec.app.cellappmgr.onRegisterNewApp.id
    text: str = ''


class OnRegisterNewAppMsgParser(IMsgParser):

    def parse(self, msg: Message) -> OnRegisterNewAppMsgResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnRegisterNewAppParsedData(*msg.get_values())
        return OnRegisterNewAppMsgResult(True, pd)


@dataclass
class LookAppMsgResult(MsgParserResult):
    """Обработчик для CellappMgr::onRegisterNewApp."""
    success: bool
    result: LookAppParsedData
    msg_id: int = msgspec.app.cellappmgr.lookApp.id
    text: str = ''


class LookAppMsgParser(IMsgParser):

    def parse(self, msg: Message) -> LookAppMsgResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = LookAppParsedData(*msg.get_values())
        return LookAppMsgResult(True, pd)


@dataclass
class UpdateCellappParsedData(ParsedMsgData):
    componentID: int
    numEntities: int
    load: float
    flags: int


@dataclass
class UpdateCellappMsgResult(MsgParserResult):
    """Обработчик для CellappMgr::updateCellapp."""
    success: bool
    result: UpdateCellappParsedData
    msg_id: int = msgspec.app.cellappmgr.updateCellapp.id
    text: str = ''


class UpdateCellappMsgParser(IMsgParser):

    def parse(self, msg: Message) -> UpdateCellappMsgResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = UpdateCellappParsedData(*msg.get_values())
        return UpdateCellappMsgResult(True, pd)


@dataclass
class UpdateSpaceDataParsedData(ParsedMsgData):
    componentID: int
    spaceID: int
    scriptModuleName: str
    delspace: bool
    geomappingPath: str


@dataclass
class UpdateSpaceDataMsgResult(MsgParserResult):
    """Обработчик для CellappMgr::updateSpaceData."""
    success: bool
    result: UpdateSpaceDataParsedData
    msg_id: int = msgspec.app.cellappmgr.updateSpaceData.id
    text: str = ''


class UpdateSpaceDataMsgParser(IMsgParser):

    def parse(self, msg: Message) -> UpdateSpaceDataMsgResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = UpdateSpaceDataParsedData(*msg.get_values())
        return UpdateSpaceDataMsgResult(True, pd)


@dataclass
class ReqCreateCellEntityInNewSpaceMsgResult(MsgParserResult):
    """Обработчик для CellappMgr::reqCreateCellEntityInNewSpace."""
    success: bool
    result: CreateCellEntityInNewSpaceFromBaseappParsedData
    msg_id: int = msgspec.app.cellappmgr.reqCreateCellEntityInNewSpace.id
    text: str = ''


class ReqCreateCellEntityInNewSpaceMsgParser(IMsgParser):

    def parse(self, msg: Message) -> ReqCreateCellEntityInNewSpaceMsgResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = CreateCellEntityInNewSpaceFromBaseappParser().parse(msg)
        return ReqCreateCellEntityInNewSpaceMsgResult(True, pd)
