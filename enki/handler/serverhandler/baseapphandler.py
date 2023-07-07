"""Обработчик сообщений от компонента Baseapp."""

import logging
from dataclasses import dataclass
import pickle
from typing import Any

from enki.core import kbeenum, kbemath, kbetype, utils
from enki.core import enkitype
from enki.core import msgspec
from enki.core.message import Message
from enki.misc import devonly

from ..base import ParsedMsgData, HandlerResult, Handler
from .common import CreateEntityAnywhereParsedData, CreateEntityAnywhereParser, LookAppParsedData, OnAppActiveTickParsedData, OnDbmgrInitCompletedParsedData, OnGetEntityAppFromDbmgrParsedData, OnLookAppParsedData, OnRegisterNewAppParsedData

logger = logging.getLogger(__file__)


@dataclass
class OnCreateEntityAnywhereHandlerResult(HandlerResult):
    """Обработчик для BaseappMgr::reqCreateEntityAnywhere."""
    success: bool
    result: CreateEntityAnywhereParsedData
    msg_id: int = msgspec.app.baseapp.onCreateEntityAnywhere.id
    text: str = ''


class OnCreateEntityAnywhereHandler(Handler):

    def handle(self, msg: Message) -> OnCreateEntityAnywhereHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = CreateEntityAnywhereParser().parse(msg)
        return OnCreateEntityAnywhereHandlerResult(True, pd)


@dataclass
class OnGetEntityAppFromDbmgrHandlerResult(HandlerResult):
    """Обработчик для Baseapp::onGetEntityAppFromDbmgr."""
    success: bool
    result: OnGetEntityAppFromDbmgrParsedData
    msg_id: int = msgspec.app.baseapp.onGetEntityAppFromDbmgr.id
    text: str = ''


class OnGetEntityAppFromDbmgrHandler(Handler):

    def handle(self, msg: Message) -> OnGetEntityAppFromDbmgrHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnGetEntityAppFromDbmgrParsedData(*msg.get_values())
        return OnGetEntityAppFromDbmgrHandlerResult(True, pd)


@dataclass
class OnDbmgrInitCompletedHandlerResult(HandlerResult):
    """Обработчик для Baseapp::onDbmgrInitCompleted."""
    success: bool
    result: OnDbmgrInitCompletedParsedData
    msg_id: int = msgspec.app.baseapp.onDbmgrInitCompleted.id
    text: str = ''


class OnDbmgrInitCompletedHandler(Handler):

    def handle(self, msg: Message) -> OnDbmgrInitCompletedHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnDbmgrInitCompletedParsedData(*msg.get_values())
        return OnDbmgrInitCompletedHandlerResult(True, pd)


@dataclass
class OnEntityAutoLoadCBFromDBMgrParsedData(ParsedMsgData):
    dbInterfaceIndex: int
    size: int
    entityType: int
    dbids: list[int]


@dataclass
class OnEntityAutoLoadCBFromDBMgrHandlerResult(HandlerResult):
    """Обработчик для Baseapp::onEntityAutoLoadCBFromDBMgr."""
    success: bool
    result: OnEntityAutoLoadCBFromDBMgrParsedData
    msg_id: int = msgspec.app.baseapp.onEntityAutoLoadCBFromDBMgr.id
    text: str = ''


class OnEntityAutoLoadCBFromDBMgrHandler(Handler):

    def handle(self, msg: Message) -> OnEntityAutoLoadCBFromDBMgrHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        data: memoryview = msg.get_values()[0]
        dbInterfaceIndex, offset = kbetype.UINT16.decode(data)
        data = data[offset:]
        size, offset = kbetype.INT32.decode(data)
        data = data[offset:]
        entityType, offset = kbetype.ENTITY_SCRIPT_UID.decode(data)
        data = data[offset:]
        dbids: list[int] = []
        for _ in range(size):
            dbid, offset = kbetype.DBID.decode(data)
            data = data[offset:]
            dbids.append(dbid)

        pd = OnEntityAutoLoadCBFromDBMgrParsedData(
            dbInterfaceIndex, size, entityType, dbids
        )
        return OnEntityAutoLoadCBFromDBMgrHandlerResult(True, pd)


@dataclass
class OnBroadcastGlobalDataChangedParsedData(ParsedMsgData):
    isDelete: bool
    key: str
    value: Any = None


@dataclass
class OnBroadcastGlobalDataChangedHandlerResult(HandlerResult):
    """Обработчик для Baseapp::onBroadcastGlobalDataChanged."""
    success: bool
    result: OnBroadcastGlobalDataChangedParsedData
    msg_id: int = msgspec.app.baseapp.onBroadcastGlobalDataChanged.id
    text: str = ''


class OnBroadcastGlobalDataChangedHandler(Handler):

    def handle(self, msg: Message) -> OnBroadcastGlobalDataChangedHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        data: memoryview = msg.get_values()[0]
        isDelete, offset = kbetype.BOOL.decode(data)
        data = data[offset:]

        key_data, offset = kbetype.BLOB.decode(data)
        data = data[offset:]
        key = pickle.loads(key_data)
        pd = OnBroadcastGlobalDataChangedParsedData(isDelete, key)
        if isDelete:
            return OnBroadcastGlobalDataChangedHandlerResult(True, pd)
        value_data, offset = kbetype.BLOB.decode(data)
        data = data[offset:]
        pd.value = utils.pickle_global_data_value(value_data)
        assert not data

        return OnBroadcastGlobalDataChangedHandlerResult(True, pd)


@dataclass
class OnAppActiveTickHandlerResult(HandlerResult):
    """Обработчик для Baseapp::onAppActiveTick."""
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


@dataclass
class OnRegisterNewAppHandlerResult(HandlerResult):
    """Обработчик для Baseappp::onRegisterNewApp."""
    success: bool
    result: OnRegisterNewAppParsedData
    msg_id: int = msgspec.app.baseapp.onRegisterNewApp.id
    text: str = ''


class OnRegisterNewAppHandler(Handler):

    def handle(self, msg: Message) -> OnRegisterNewAppHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnRegisterNewAppParsedData(*msg.get_values())
        return OnRegisterNewAppHandlerResult(True, pd)


@dataclass
class OnEntityGetCellParsedData(ParsedMsgData):
    entity_id: int
    componentID: int
    spaceID: int


@dataclass
class OnEntityGetCellHandlerResult(HandlerResult):
    """Обработчик для Baseapp::onEntityGetCell."""
    success: bool
    result: OnEntityGetCellParsedData
    msg_id: int = msgspec.app.baseapp.onEntityGetCell.id
    text: str = ''


class OnEntityGetCellHandler(Handler):

    def handle(self, msg: Message) -> OnEntityGetCellHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnEntityGetCellParsedData(*msg.get_values())
        return OnEntityGetCellHandlerResult(True, pd)
