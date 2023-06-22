"""Обработчик сообщений от компонента CellappMgr."""

import logging
from dataclasses import dataclass

from enki.core import kbeenum, kbemath
from enki.core import enkitype
from enki.core import msgspec
from enki.core.message import Message
from enki.misc import devonly

from ..base import ParsedMsgData, HandlerResult, Handler
from .common import CreateCellEntityInNewSpaceFromBaseappParsedData, \
    CreateCellEntityInNewSpaceFromBaseappParser, LookAppParsedData, \
    OnAppActiveTickParsedData, OnRegisterNewAppParsedData

logger = logging.getLogger(__file__)


@dataclass
class OnAppActiveTickHandlerResult(HandlerResult):
    """Обработчик для DBMgr::onAppActiveTick."""
    success: bool
    result: OnAppActiveTickParsedData
    msg_id: int = msgspec.app.cellappmgr.onAppActiveTick.id
    text: str = ''


class OnAppActiveTickHandler(Handler):

    def handle(self, msg: Message) -> OnAppActiveTickHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnAppActiveTickParsedData(*msg.get_values())
        return OnAppActiveTickHandlerResult(True, pd)


@dataclass
class OnRegisterNewAppHandlerResult(HandlerResult):
    """Обработчик для CellappMgr::onRegisterNewApp."""
    success: bool
    result: OnRegisterNewAppParsedData
    msg_id: int = msgspec.app.cellappmgr.onRegisterNewApp.id
    text: str = ''


class OnRegisterNewAppHandler(Handler):

    def handle(self, msg: Message) -> OnRegisterNewAppHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnRegisterNewAppParsedData(*msg.get_values())
        return OnRegisterNewAppHandlerResult(True, pd)


@dataclass
class LookAppHandlerResult(HandlerResult):
    """Обработчик для CellappMgr::onRegisterNewApp."""
    success: bool
    result: LookAppParsedData
    msg_id: int = msgspec.app.cellappmgr.lookApp.id
    text: str = ''


class LookAppHandler(Handler):

    def handle(self, msg: Message) -> LookAppHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = LookAppParsedData(*msg.get_values())
        return LookAppHandlerResult(True, pd)


@dataclass
class UpdateCellappParsedData(ParsedMsgData):
    componentID: int
    numEntities: int
    load: float
    flags: int


@dataclass
class UpdateCellappHandlerResult(HandlerResult):
    """Обработчик для CellappMgr::updateCellapp."""
    success: bool
    result: UpdateCellappParsedData
    msg_id: int = msgspec.app.cellappmgr.updateCellapp.id
    text: str = ''


class UpdateCellappHandler(Handler):

    def handle(self, msg: Message) -> UpdateCellappHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = UpdateCellappParsedData(*msg.get_values())
        return UpdateCellappHandlerResult(True, pd)


@dataclass
class UpdateSpaceDataParsedData(ParsedMsgData):
    componentID: int
    spaceID: int
    scriptModuleName: str
    delspace: bool
    geomappingPath: str


@dataclass
class UpdateSpaceDataHandlerResult(HandlerResult):
    """Обработчик для CellappMgr::updateSpaceData."""
    success: bool
    result: UpdateSpaceDataParsedData
    msg_id: int = msgspec.app.cellappmgr.updateSpaceData.id
    text: str = ''


class UpdateSpaceDataHandler(Handler):

    def handle(self, msg: Message) -> UpdateSpaceDataHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = UpdateSpaceDataParsedData(*msg.get_values())
        return UpdateSpaceDataHandlerResult(True, pd)


@dataclass
class ReqCreateCellEntityInNewSpaceHandlerResult(HandlerResult):
    """Обработчик для CellappMgr::reqCreateCellEntityInNewSpace."""
    success: bool
    result: CreateCellEntityInNewSpaceFromBaseappParsedData
    msg_id: int = msgspec.app.cellappmgr.reqCreateCellEntityInNewSpace.id
    text: str = ''


class ReqCreateCellEntityInNewSpaceHandler(Handler):

    def handle(self, msg: Message) -> ReqCreateCellEntityInNewSpaceHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = CreateCellEntityInNewSpaceFromBaseappParser().parse(msg)
        return ReqCreateCellEntityInNewSpaceHandlerResult(True, pd)
