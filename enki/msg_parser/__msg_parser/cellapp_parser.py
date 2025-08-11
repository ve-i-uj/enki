"""Обработчик сообщений от компонента Cellapp."""

import logging
import pickle
from dataclasses import dataclass
from typing import Any

from enki.net.addr import Addr
from enki.kbeenum import ComponentType
from enki.core import kbemath, kbepickle, kbetype
from enki.core import msgspec
from enki.core.message import Message
from enki.misc import devonly

from ..imsgparser import ParsedMsgData, MsgParserResult, Handler
from .common import (
    CreateCellEntityInNewSpaceFromBaseappParsedMsgData,
    CreateCellEntityInNewSpaceFromBaseappParser,
    OnAppActiveTickParsedData,
    OnDbmgrInitCompletedParsedMsgData,
    OnGetEntityAppFromDbmgrParsedMsgData,
    OnRegisterNewAppParsedData,
)

logger = logging.getLogger(__file__)


@dataclass
class OnDbmgrInitCompletedMsgResult(MsgParserResult):
    """Обработчик для Cellapp::onDbmgrInitCompleted."""

    success: bool
    result: OnDbmgrInitCompletedParsedMsgData
    msg_id: int = msgspec.app.cellapp.onDbmgrInitCompleted.id
    text: str = ""


class OnDbmgrInitCompletedMsgParser(IMsgParser):
    def parse(self, msg: Message) -> OnDbmgrInitCompletedMsgResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        pd = OnDbmgrInitCompletedParsedMsgData(*msg.get_values())
        return OnDbmgrInitCompletedMsgResult(True, pd)


@dataclass
class OnBroadcastGlobalDataChangedParsedData(ParsedMsgData):
    isDelete: bool
    key: str
    value: Any = None


@dataclass
class OnBroadcastGlobalDataChangedMsgResult(MsgParserResult):
    """Обработчик для Cellapp::onBroadcastGlobalDataChanged."""

    success: bool
    result: OnBroadcastGlobalDataChangedParsedData
    msg_id: int = msgspec.app.cellapp.onBroadcastGlobalDataChanged.id
    text: str = ""


class OnBroadcastGlobalDataChangedMsgParser(IMsgParser):
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
class OnGetEntityAppFromDbmgrMsgResult(MsgParserResult):
    """Обработчик для Cellapp::onGetEntityAppFromDbmgr."""

    success: bool
    result: OnGetEntityAppFromDbmgrParsedMsgData
    msg_id: int = msgspec.app.cellapp.onGetEntityAppFromDbmgr.id
    text: str = ""


class OnGetEntityAppFromDbmgrMsgParser(IMsgParser):
    def parse(self, msg: Message) -> OnGetEntityAppFromDbmgrMsgResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        pd = OnGetEntityAppFromDbmgrParsedMsgData(*msg.get_values())
        return OnGetEntityAppFromDbmgrMsgResult(True, pd)


@dataclass
class OnAppActiveTickMsgResult(MsgParserResult):
    """Обработчик для Cellapp::onAppActiveTick."""

    success: bool
    result: OnAppActiveTickParsedData
    msg_id: int = msgspec.app.cellapp.onAppActiveTick.id
    text: str = ""


class OnAppActiveTickMsgParser(IMsgParser):
    def parse(self, msg: Message) -> OnAppActiveTickMsgResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        pd = OnAppActiveTickParsedData(*msg.get_values())
        return OnAppActiveTickMsgResult(True, pd)


@dataclass
class OnBroadcastCellAppDataChangedParsedData(ParsedMsgData):
    isDelete: bool
    key: Any = None
    value: Any = None


@dataclass
class OnBroadcastCellAppDataChangedMsgResult(MsgParserResult):
    """Обработчик для Cellapp::OnBroadcastCellAppDataChanged.

    Это колбэк в скрипты на изменение глобальных CellData (onCellAppData,
    onCellAppDataDel).
    """

    success: bool
    result: OnBroadcastCellAppDataChangedParsedData
    msg_id: int = msgspec.app.cellapp.onBroadcastCellAppDataChanged.id
    text: str = ""


class OnBroadcastCellAppDataChangedMsgParser(IMsgParser):
    def parse(self, msg: Message) -> OnBroadcastCellAppDataChangedMsgResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        data: memoryview = msg.get_values()[0]
        is_deleted, offset = kbetype.BOOL.decode(data)
        data = data[offset:]
        pd = OnBroadcastCellAppDataChangedParsedData(is_deleted)
        key_data, offset = kbetype.BLOB.decode(data)
        data = data[offset:]
        pd.key = pickle.loads(key_data)
        if pd.isDelete:
            # В компоненте на C++ будет вызван колбэк в Python onCellAppDataDel
            return OnBroadcastCellAppDataChangedMsgResult(True, pd)
        value_data, offset = kbetype.BLOB.decode(data)
        data = data[offset:]
        pd.value = pickle.loads(value_data)
        assert not data
        # В компоненте на C++ будет вызван колбэк в Python onCellAppData
        return OnBroadcastCellAppDataChangedMsgResult(True, pd)


@dataclass
class OnCreateCellEntityFromBaseappParsedData(ParsedMsgData):
    createToEntityID: int
    entityType: str
    entityID: int
    componentID: int
    hasClient: bool
    inRescore: bool


@dataclass
class OnCreateCellEntityFromBaseappMsgResult(MsgParserResult):
    """Обработчик для Cellapp::onCreateCellEntityFromBaseapp."""

    success: bool
    result: OnCreateCellEntityFromBaseappParsedData
    msg_id: int = msgspec.app.cellapp.onCreateCellEntityFromBaseapp.id
    text: str = ""


class OnCreateCellEntityFromBaseappMsgParser(IMsgParser):
    def parse(self, msg: Message) -> OnCreateCellEntityFromBaseappMsgResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        data: memoryview = msg.get_values()[0]
        createToEntityID, offset = kbetype.ENTITY_ID.decode(data)
        data = data[offset:]
        entityType, offset = kbetype.STRING.decode(data)
        data = data[offset:]
        entityID, offset = kbetype.ENTITY_ID.decode(data)
        data = data[offset:]
        componentID, offset = kbetype.COMPONENT_ID.decode(data)
        data = data[offset:]
        hasClient, offset = kbetype.BOOL.decode(data)
        data = data[offset:]
        inRestore, offset = kbetype.BOOL.decode(data)
        data = data[offset:]
        # [2023-06-22 15:01 burov_alexey@mail.ru]:
        # Эти данные можно распарсить так же, как парсятся свойства у
        # клиентских методов (с учётом оптимизации через usePropertyDescrAlias)
        cell_data, offset = kbetype.UINT8_ARRAY.decode(data)
        data = data[offset:]
        pd = OnCreateCellEntityFromBaseappParsedData(
            createToEntityID,
            entityType,
            entityID,
            componentID,
            hasClient,
            inRestore,
        )
        return OnCreateCellEntityFromBaseappMsgResult(True, pd)


@dataclass
class OnCreateCellEntityInNewSpaceFromBaseappMsgResult(MsgParserResult):
    """Обработчик для Cellapp::onCreateCellEntityInNewSpaceFromBaseapp."""

    success: bool
    result: CreateCellEntityInNewSpaceFromBaseappParsedMsgData
    msg_id: int = msgspec.app.cellapp.onCreateCellEntityInNewSpaceFromBaseapp.id
    text: str = ""


class OnCreateCellEntityInNewSpaceFromBaseappMsgParser(IMsgParser):
    def parse(
        self, msg: Message
    ) -> OnCreateCellEntityInNewSpaceFromBaseappMsgResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        pd = CreateCellEntityInNewSpaceFromBaseappParser().parse(msg)
        return OnCreateCellEntityInNewSpaceFromBaseappMsgResult(True, pd)


@dataclass
class OnRegisterNewAppMsgResult(MsgParserResult):
    """Обработчик для Cellapp::onRegisterNewApp."""

    success: bool
    result: OnRegisterNewAppParsedData
    msg_id: int = msgspec.app.cellapp.onRegisterNewApp.id
    text: str = ""


class OnRegisterNewAppMsgParser(IMsgParser):
    def parse(self, msg: Message) -> OnRegisterNewAppMsgResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        pd = OnRegisterNewAppParsedData(*msg.get_values())
        return OnRegisterNewAppMsgResult(True, pd)
