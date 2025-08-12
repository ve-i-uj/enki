"""Обработчик сообщений от компонента Baseapp."""

import logging
import pickle
from dataclasses import dataclass
from typing import Any

from enki import msgspec
from enki.core.kbepickle.kbepickle import pickle_global_data_value
from enki.kbetype.decoders.basic_data_type_decoders import BLOB, INT32, UINT16
from enki.kbetype.decoders.custom_decoders import BOOL, DBID, ENTITY_SCRIPT_UID, KBEBool
from enki.misc import devonly
from enki.msg.message import Message
from .imsg_parser import (
    IMsgParser,
    MsgParserResult,
    ParsedMsgData,
)

from .common import (
    CreateEntityAnywhereMsgParser,
    CreateEntityAnywhereParsedMsgData,
    OnAppActiveTickParsedMsgData,
    OnDbmgrInitCompletedParsedMsgData,
    OnGetEntityAppFromDbmgrParsedMsgData,
    OnRegisterNewAppParsedMsgData,
)

logger = logging.getLogger(__name__)


@dataclass
class OnCreateEntityAnywhereMsgParserResult(MsgParserResult):
    """Результат парсера сообщения BaseappMgr::reqCreateEntityAnywhere."""

    success: bool
    result: CreateEntityAnywhereParsedMsgData | None
    msg_id: int = msgspec.baseapp.onCreateEntityAnywhere.id
    text: str = ""


class OnCreateEntityAnywhereMsgParser(IMsgParser):
    """Парсер для BaseappMgr::reqCreateEntityAnywhere."""

    def parse(self, msg: Message) -> OnCreateEntityAnywhereMsgParserResult:
        """Обработать сообщение BaseappMgr::reqCreateEntityAnywhere.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnCreateEntityAnywhereMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        res = CreateEntityAnywhereMsgParser().parse(msg)

        return OnCreateEntityAnywhereMsgParserResult(success=res.success, 
                                                     result=res.result, text=res.text)


@dataclass
class OnGetEntityAppFromDbmgrMsgParserResult(MsgParserResult):
    """Парсер для Baseapp::onGetEntityAppFromDbmgr."""

    success: bool
    result: OnGetEntityAppFromDbmgrParsedMsgData
    msg_id: int = msgspec.baseapp.onGetEntityAppFromDbmgr.id
    text: str = ""


class OnGetEntityAppFromDbmgrMsgParser(IMsgParser):
    """Парсер для Baseapp::onGetEntityAppFromDbmgr."""

    def parse(self, msg: Message) -> OnGetEntityAppFromDbmgrMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnGetEntityAppFromDbmgrParsedMsgData(*values)
        return OnGetEntityAppFromDbmgrMsgParserResult(True, pd)


@dataclass
class OnDbmgrInitCompletedMsgParserResult(MsgParserResult):
    """Парсер для Baseapp::onDbmgrInitCompleted."""

    success: bool
    result: OnDbmgrInitCompletedParsedMsgData
    msg_id: int = msgspec.baseapp.onDbmgrInitCompleted.id
    text: str = ""


class OnDbmgrInitCompletedMsgParser(IMsgParser):
    """Парсер для Baseapp::onDbmgrInitCompleted."""
    
    def parse(self, msg: Message) -> OnDbmgrInitCompletedMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnDbmgrInitCompletedParsedMsgData(*values)
        return OnDbmgrInitCompletedMsgParserResult(True, pd)


@dataclass
class OnEntityAutoLoadCBFromDBMgrParsedMsgData(ParsedMsgData):
    dbInterfaceIndex: int
    size: int
    entityType: int
    dbids: list[int]


@dataclass
class OnEntityAutoLoadCBFromDBMgrMsgParserResult(MsgParserResult):
    """Парсер для Baseapp::onEntityAutoLoadCBFromDBMgr."""

    success: bool
    result: OnEntityAutoLoadCBFromDBMgrParsedMsgData
    msg_id: int = msgspec.baseapp.onEntityAutoLoadCBFromDBMgr.id
    text: str = ""


class OnEntityAutoLoadCBFromDBMgrMsgParser(IMsgParser):
    """Парсер для Baseapp::onEntityAutoLoadCBFromDBMgr."""
    def parse(self, msg: Message) -> OnEntityAutoLoadCBFromDBMgrMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])
        dbInterfaceIndex, offset = UINT16.decode(data)
        data = data[offset:]
        size, offset = INT32.decode(data)
        data = data[offset:]
        entityType, offset = ENTITY_SCRIPT_UID.decode(data)
        data = data[offset:]
        dbids: list[int] = []
        for _ in range(size):
            dbid, offset = DBID.decode(data)
            data = data[offset:]
            dbids.append(dbid)

        pd = OnEntityAutoLoadCBFromDBMgrParsedMsgData(
            dbInterfaceIndex, size, entityType, dbids
        )
        return OnEntityAutoLoadCBFromDBMgrMsgParserResult(True, pd)


@dataclass
class OnBroadcastGlobalDataChangedParsedMsgData(ParsedMsgData):
    isDelete: KBEBool
    key: str
    value: Any = None


@dataclass
class OnBroadcastGlobalDataChangedMsgParserResult(MsgParserResult):
    """Парсер для Baseapp::onBroadcastGlobalDataChanged."""

    success: bool
    result: OnBroadcastGlobalDataChangedParsedMsgData
    msg_id: int = msgspec.baseapp.onBroadcastGlobalDataChanged.id
    text: str = ""


class OnBroadcastGlobalDataChangedMsgParser(IMsgParser):
    """Парсер для Baseapp::onBroadcastGlobalDataChanged."""
    
    def parse(self, msg: Message) -> OnBroadcastGlobalDataChangedMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])
        isDelete, offset = BOOL.decode(data)
        data = data[offset:]

        key_data, offset = BLOB.decode(data)
        data = data[offset:]
        key = pickle.loads(key_data)
        pd = OnBroadcastGlobalDataChangedParsedMsgData(isDelete, key)
        if isDelete:
            return OnBroadcastGlobalDataChangedMsgParserResult(True, pd)
        value_data, offset = BLOB.decode(data)
        data = data[offset:]
        pd.value = pickle_global_data_value(value_data)
        assert not data

        return OnBroadcastGlobalDataChangedMsgParserResult(True, pd)


@dataclass
class OnAppActiveTickMsgParserResult(MsgParserResult):
    """Парсер для Baseapp::onAppActiveTick."""

    success: bool
    result: OnAppActiveTickParsedMsgData
    msg_id: int = msgspec.baseapp.onAppActiveTick.id
    text: str = ""


class OnAppActiveTickMsgParser(IMsgParser):
    """Парсер для Baseapp::onAppActiveTick."""
    
    def parse(self, msg: Message) -> OnAppActiveTickMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnAppActiveTickParsedMsgData(*values)
        return OnAppActiveTickMsgParserResult(True, pd)


@dataclass
class OnRegisterNewAppMsgParserResult(MsgParserResult):
    """Парсер для Baseappp::onRegisterNewApp."""

    success: bool
    result: OnRegisterNewAppParsedMsgData
    msg_id: int = msgspec.baseapp.onRegisterNewApp.id
    text: str = ""


class OnRegisterNewAppMsgParser(IMsgParser):
    """Парсер для Baseappp::onRegisterNewApp."""
    
    def parse(self, msg: Message) -> OnRegisterNewAppMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnRegisterNewAppParsedMsgData(*values)
        return OnRegisterNewAppMsgParserResult(True, pd)


@dataclass
class OnEntityGetCellParsedMsgData(ParsedMsgData):
    entity_id: int
    componentID: int
    spaceID: int


@dataclass
class OnEntityGetCellMsgParserResult(MsgParserResult):
    """Парсер для Baseapp::onEntityGetCell."""

    success: bool
    result: OnEntityGetCellParsedMsgData
    msg_id: int = msgspec.baseapp.onEntityGetCell.id
    text: str = ""


class OnEntityGetCellMsgParser(IMsgParser):
    """Парсер для Baseapp::onEntityGetCell."""
    
    def parse(self, msg: Message) -> OnEntityGetCellMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnEntityGetCellParsedMsgData(*values)
        return OnEntityGetCellMsgParserResult(True, pd)
