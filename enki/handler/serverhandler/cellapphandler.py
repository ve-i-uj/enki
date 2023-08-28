"""Обработчик сообщений от компонента Cellapp."""

import logging
import pickle
from dataclasses import dataclass
from typing import Any

from enki.core.enkitype import AppAddr
from enki.core.kbeenum import ComponentType
from enki.core import kbemath, kbetype, utils
from enki.core import msgspec
from enki.core.message import Message
from enki.misc import devonly

from ..base import ParsedMsgData, HandlerResult, Handler
from .common import CreateCellEntityInNewSpaceFromBaseappParsedData, \
    CreateCellEntityInNewSpaceFromBaseappParser, OnAppActiveTickParsedData, OnDbmgrInitCompletedParsedData, OnGetEntityAppFromDbmgrParsedData, OnRegisterNewAppParsedData

logger = logging.getLogger(__file__)


@dataclass
class OnDbmgrInitCompletedHandlerResult(HandlerResult):
    """Обработчик для Cellapp::onDbmgrInitCompleted."""
    success: bool
    result: OnDbmgrInitCompletedParsedData
    msg_id: int = msgspec.app.cellapp.onDbmgrInitCompleted.id
    text: str = ''


class OnDbmgrInitCompletedHandler(Handler):

    def handle(self, msg: Message) -> OnDbmgrInitCompletedHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnDbmgrInitCompletedParsedData(*msg.get_values())
        return OnDbmgrInitCompletedHandlerResult(True, pd)


@dataclass
class OnBroadcastGlobalDataChangedParsedData(ParsedMsgData):
    isDelete: bool
    key: str
    value: Any = None


@dataclass
class OnBroadcastGlobalDataChangedHandlerResult(HandlerResult):
    """Обработчик для Cellapp::onBroadcastGlobalDataChanged."""
    success: bool
    result: OnBroadcastGlobalDataChangedParsedData
    msg_id: int = msgspec.app.cellapp.onBroadcastGlobalDataChanged.id
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
class OnGetEntityAppFromDbmgrHandlerResult(HandlerResult):
    """Обработчик для Cellapp::onGetEntityAppFromDbmgr."""
    success: bool
    result: OnGetEntityAppFromDbmgrParsedData
    msg_id: int = msgspec.app.cellapp.onGetEntityAppFromDbmgr.id
    text: str = ''


class OnGetEntityAppFromDbmgrHandler(Handler):

    def handle(self, msg: Message) -> OnGetEntityAppFromDbmgrHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnGetEntityAppFromDbmgrParsedData(*msg.get_values())
        return OnGetEntityAppFromDbmgrHandlerResult(True, pd)


@dataclass
class OnAppActiveTickHandlerResult(HandlerResult):
    """Обработчик для Cellapp::onAppActiveTick."""
    success: bool
    result: OnAppActiveTickParsedData
    msg_id: int = msgspec.app.cellapp.onAppActiveTick.id
    text: str = ''


class OnAppActiveTickHandler(Handler):

    def handle(self, msg: Message) -> OnAppActiveTickHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnAppActiveTickParsedData(*msg.get_values())
        return OnAppActiveTickHandlerResult(True, pd)


@dataclass
class OnBroadcastCellAppDataChangedParsedData(ParsedMsgData):
    isDelete: bool
    key: Any = None
    value: Any = None


@dataclass
class OnBroadcastCellAppDataChangedHandlerResult(HandlerResult):
    """Обработчик для Cellapp::OnBroadcastCellAppDataChanged.

    Это колбэк в скрипты на изменение глобальных CellData (onCellAppData,
    onCellAppDataDel).
    """
    success: bool
    result: OnBroadcastCellAppDataChangedParsedData
    msg_id: int = msgspec.app.cellapp.onBroadcastCellAppDataChanged.id
    text: str = ''


class OnBroadcastCellAppDataChangedHandler(Handler):

    def handle(self, msg: Message) -> OnBroadcastCellAppDataChangedHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        data: memoryview = msg.get_values()[0]
        is_deleted, offset = kbetype.BOOL.decode(data)
        data = data[offset:]
        pd = OnBroadcastCellAppDataChangedParsedData(is_deleted)
        key_data, offset = kbetype.BLOB.decode(data)
        data = data[offset:]
        pd.key = pickle.loads(key_data)
        if pd.isDelete:
            # В компоненте на C++ будет вызван колбэк в Python onCellAppDataDel
            return OnBroadcastCellAppDataChangedHandlerResult(True, pd)
        value_data, offset = kbetype.BLOB.decode(data)
        data = data[offset:]
        pd.value = pickle.loads(value_data)
        assert not data
        # В компоненте на C++ будет вызван колбэк в Python onCellAppData
        return OnBroadcastCellAppDataChangedHandlerResult(True, pd)


@dataclass
class OnCreateCellEntityFromBaseappParsedData(ParsedMsgData):
    createToEntityID: int
    entityType: str
    entityID: int
    componentID: int
    hasClient: bool
    inRescore: bool


@dataclass
class OnCreateCellEntityFromBaseappHandlerResult(HandlerResult):
    """Обработчик для Cellapp::onCreateCellEntityFromBaseapp."""
    success: bool
    result: OnCreateCellEntityFromBaseappParsedData
    msg_id: int = msgspec.app.cellapp.onCreateCellEntityFromBaseapp.id
    text: str = ''


class OnCreateCellEntityFromBaseappHandler(Handler):

    def handle(self, msg: Message) -> OnCreateCellEntityFromBaseappHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
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
            createToEntityID, entityType, entityID, componentID, hasClient,
            inRestore
        )
        return OnCreateCellEntityFromBaseappHandlerResult(True, pd)


@dataclass
class OnCreateCellEntityInNewSpaceFromBaseappHandlerResult(HandlerResult):
    """Обработчик для Cellapp::onCreateCellEntityInNewSpaceFromBaseapp."""
    success: bool
    result: CreateCellEntityInNewSpaceFromBaseappParsedData
    msg_id: int = msgspec.app.cellapp.onCreateCellEntityInNewSpaceFromBaseapp.id
    text: str = ''


class OnCreateCellEntityInNewSpaceFromBaseappHandler(Handler):

    def handle(self, msg: Message) -> OnCreateCellEntityInNewSpaceFromBaseappHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = CreateCellEntityInNewSpaceFromBaseappParser().parse(msg)
        return OnCreateCellEntityInNewSpaceFromBaseappHandlerResult(True, pd)


@dataclass
class OnRegisterNewAppHandlerResult(HandlerResult):
    """Обработчик для Cellapp::onRegisterNewApp."""
    success: bool
    result: OnRegisterNewAppParsedData
    msg_id: int = msgspec.app.cellapp.onRegisterNewApp.id
    text: str = ''


class OnRegisterNewAppHandler(Handler):

    def handle(self, msg: Message) -> OnRegisterNewAppHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnRegisterNewAppParsedData(*msg.get_values())
        return OnRegisterNewAppHandlerResult(True, pd)
