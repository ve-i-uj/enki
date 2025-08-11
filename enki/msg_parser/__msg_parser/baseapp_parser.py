"""Обработчик сообщений от компонента Baseapp."""

import logging
import pickle
from dataclasses import dataclass
from typing import Any

from enki import kbetype
from enki.core import kbepickle, msgspec
from enki.misc import devonly
from enki.msg.message import Message
from enki.msg.msg_parser.imsg_parser import (
    IMsgParser,
    MsgParserResult,
    ParsedMsgData,
)

from ..common import (
    CreateEntityAnywhereParsedData,
    CreateEntityAnywhereParser,
    OnAppActiveTickParsedMsgData,
    OnDbmgrInitCompletedParsedMsgData,
    OnGetEntityAppFromDbmgrParsedMsgData,
    OnRegisterNewAppParsedMsgData,
)

logger = logging.getLogger(__name__)


@dataclass
class OnCreateEntityAnywhereMsgResult(MsgParserResult):
    """Результат обработчика сообщения BaseappMgr::reqCreateEntityAnywhere."""

    success: bool
    result: CreateEntityAnywhereParsedData
    msg_id: int = msgspec.app.baseapp.onCreateEntityAnywhere.id
    text: str = ""


class OnCreateEntityAnywhereHandler(IMsgParser):
    """Обработчик для BaseappMgr::reqCreateEntityAnywhere."""

    def parse(self, msg: Message) -> OnCreateEntityAnywhereMsgResult:
        """Обработать сообщение BaseappMgr::reqCreateEntityAnywhere.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnCreateEntityAnywhereMsgResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        pd = CreateEntityAnywhereParser().parse(msg)

        return OnCreateEntityAnywhereMsgResult(success=True, result=pd)


@dataclass
class OnGetEntityAppFromDbmgrMsgResult(MsgParserResult):
    """Обработчик для Baseapp::onGetEntityAppFromDbmgr."""

    success: bool
    result: OnGetEntityAppFromDbmgrParsedMsgData
    msg_id: int = msgspec.app.baseapp.onGetEntityAppFromDbmgr.id
    text: str = ""


class OnGetEntityAppFromDbmgrHandler(IMsgParser):
    def parse(self, msg: Message) -> OnGetEntityAppFromDbmgrMsgResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        pd = OnGetEntityAppFromDbmgrParsedMsgData(*msg.get_values())
        return OnGetEntityAppFromDbmgrMsgResult(True, pd)


@dataclass
class OnDbmgrInitCompletedMsgResult(MsgParserResult):
    """Обработчик для Baseapp::onDbmgrInitCompleted."""

    success: bool
    result: OnDbmgrInitCompletedParsedMsgData
    msg_id: int = msgspec.app.baseapp.onDbmgrInitCompleted.id
    text: str = ""


class OnDbmgrInitCompletedHandler(IMsgParser):
    def parse(self, msg: Message) -> OnDbmgrInitCompletedMsgResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        pd = OnDbmgrInitCompletedParsedMsgData(*msg.get_values())
        return OnDbmgrInitCompletedMsgResult(True, pd)


@dataclass
class OnEntityAutoLoadCBFromDBMgrParsedData(ParsedMsgData):
    dbInterfaceIndex: int
    size: int
    entityType: int
    dbids: list[int]


@dataclass
class OnEntityAutoLoadCBFromDBMgrMsgResult(MsgParserResult):
    """Обработчик для Baseapp::onEntityAutoLoadCBFromDBMgr."""

    success: bool
    result: OnEntityAutoLoadCBFromDBMgrParsedData
    msg_id: int = msgspec.app.baseapp.onEntityAutoLoadCBFromDBMgr.id
    text: str = ""


class OnEntityAutoLoadCBFromDBMgrHandler(IMsgParser):
    def parse(self, msg: Message) -> OnEntityAutoLoadCBFromDBMgrMsgResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
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
        return OnEntityAutoLoadCBFromDBMgrMsgResult(True, pd)


@dataclass
class OnBroadcastGlobalDataChangedParsedData(ParsedMsgData):
    isDelete: bool
    key: str
    value: Any = None


@dataclass
class OnBroadcastGlobalDataChangedMsgResult(MsgParserResult):
    """Обработчик для Baseapp::onBroadcastGlobalDataChanged."""

    success: bool
    result: OnBroadcastGlobalDataChangedParsedData
    msg_id: int = msgspec.app.baseapp.onBroadcastGlobalDataChanged.id
    text: str = ""


class OnBroadcastGlobalDataChangedHandler(IMsgParser):
    def parse(self, msg: Message) -> OnBroadcastGlobalDataChangedMsgResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        data: memoryview = msg.get_values()[0]
        isDelete, offset = kbetype.BOOL.decode(data)
        data = data[offset:]

        key_data, offset = kbetype.BLOB.decode(data)
        data = data[offset:]
        key = pickle.loads(key_data)
        pd = OnBroadcastGlobalDataChangedParsedData(isDelete, key)
        if isDelete:
            return OnBroadcastGlobalDataChangedMsgResult(True, pd)
        value_data, offset = kbetype.BLOB.decode(data)
        data = data[offset:]
        pd.value = kbepickle.pickle_global_data_value(value_data)
        assert not data

        return OnBroadcastGlobalDataChangedMsgResult(True, pd)


@dataclass
class OnAppActiveTickMsgResult(MsgParserResult):
    """Обработчик для Baseapp::onAppActiveTick."""

    success: bool
    result: OnAppActiveTickParsedMsgData
    msg_id: int = msgspec.app.baseapp.onAppActiveTick.id
    text: str = ""


class OnAppActiveTickHandler(IMsgParser):
    def parse(self, msg: Message) -> OnAppActiveTickMsgResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        pd = OnAppActiveTickParsedMsgData(*msg.get_values())
        return OnAppActiveTickMsgResult(True, pd)


@dataclass
class OnRegisterNewAppMsgResult(MsgParserResult):
    """Обработчик для Baseappp::onRegisterNewApp."""

    success: bool
    result: OnRegisterNewAppParsedMsgData
    msg_id: int = msgspec.app.baseapp.onRegisterNewApp.id
    text: str = ""


class OnRegisterNewAppHandler(IMsgParser):
    def parse(self, msg: Message) -> OnRegisterNewAppMsgResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        pd = OnRegisterNewAppParsedMsgData(*msg.get_values())
        return OnRegisterNewAppMsgResult(True, pd)


@dataclass
class OnEntityGetCellParsedData(ParsedMsgData):
    entity_id: int
    componentID: int
    spaceID: int


@dataclass
class OnEntityGetCellMsgResult(MsgParserResult):
    """Обработчик для Baseapp::onEntityGetCell."""

    success: bool
    result: OnEntityGetCellParsedData
    msg_id: int = msgspec.app.baseapp.onEntityGetCell.id
    text: str = ""


class OnEntityGetCellHandler(IMsgParser):
    def parse(self, msg: Message) -> OnEntityGetCellMsgResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        pd = OnEntityGetCellParsedData(*msg.get_values())
        return OnEntityGetCellMsgResult(True, pd)
