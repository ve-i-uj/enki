"""Обработчик сообщений от компонента Cellapp."""

import logging
import pickle
from dataclasses import dataclass
from typing import Any

from enki import msgspec
from enki.core.kbepickle.kbepickle import pickle_global_data_value
from enki.kbetype.decoders.basic_data_type_decoders import (
    BLOB,
    BOOL,
    STRING,
    UINT8_ARRAY,
)
from enki.kbetype.decoders.custom_decoders import (
    COMPONENT_ID,
    ENTITY_ID,
    KBEComponentId,
    KBEEntityId,
)
from enki.kbetype.pytypes.basic_data_types import KBEBool, KBEString
from enki.misc import devonly
from enki.msg.message import Message

from .common import (
    CreateCellEntityInNewSpaceFromBaseappParsedMsgData,
    CreateCellEntityInNewSpaceFromBaseappParser,
    OnAppActiveTickParsedMsgData,
    OnDbmgrInitCompletedParsedMsgData,
    OnGetEntityAppFromDbmgrParsedMsgData,
    OnRegisterNewAppParsedMsgData,
)
from .imsg_parser import IMsgParser, MsgParserResult, ParsedMsgData

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OnDbmgrInitCompletedMsgParserResult(MsgParserResult):
    """Результат парсера Cellapp::onDbmgrInitCompleted."""

    success: bool
    result: OnDbmgrInitCompletedParsedMsgData
    msg_id: int = msgspec.cellapp.onDbmgrInitCompleted.id
    text: str = ""


class OnDbmgrInitCompletedMsgParser(IMsgParser):
    """Парсер для Cellapp::onDbmgrInitCompleted."""

    def parse(self, msg: Message) -> OnDbmgrInitCompletedMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnDbmgrInitCompletedParsedMsgData(*values)
        return OnDbmgrInitCompletedMsgParserResult(True, pd)


@dataclass
class OnBroadcastGlobalDataChangedParsedMsgData(ParsedMsgData):
    isDelete: KBEBool
    key: str
    value: Any = None


@dataclass(frozen=True)
class OnBroadcastGlobalDataChangedMsgParserResult(MsgParserResult):
    """Результат парсера Cellapp::onBroadcastGlobalDataChanged."""

    success: bool
    result: OnBroadcastGlobalDataChangedParsedMsgData
    msg_id: int = msgspec.cellapp.onBroadcastGlobalDataChanged.id
    text: str = ""


class OnBroadcastGlobalDataChangedMsgParser(IMsgParser):
    """Парсер для Cellapp::onBroadcastGlobalDataChanged."""

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


@dataclass(frozen=True)
class OnGetEntityAppFromDbmgrMsgParserResult(MsgParserResult):
    """Результат парсера Cellapp::onGetEntityAppFromDbmgr."""

    success: bool
    result: OnGetEntityAppFromDbmgrParsedMsgData
    msg_id: int = msgspec.cellapp.onGetEntityAppFromDbmgr.id
    text: str = ""


class OnGetEntityAppFromDbmgrMsgParser(IMsgParser):
    """Парсер для Cellapp::onGetEntityAppFromDbmgr."""

    def parse(self, msg: Message) -> OnGetEntityAppFromDbmgrMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnGetEntityAppFromDbmgrParsedMsgData(*values)
        return OnGetEntityAppFromDbmgrMsgParserResult(True, pd)


@dataclass(frozen=True)
class OnAppActiveTickMsgParserResult(MsgParserResult):
    """Результат парсера Cellapp::onAppActiveTick."""

    success: bool
    result: OnAppActiveTickParsedMsgData
    msg_id: int = msgspec.cellapp.onAppActiveTick.id
    text: str = ""


class OnAppActiveTickMsgParser(IMsgParser):
    """Парсер для Cellapp::onAppActiveTick."""

    def parse(self, msg: Message) -> OnAppActiveTickMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnAppActiveTickParsedMsgData(*values)
        return OnAppActiveTickMsgParserResult(True, pd)


@dataclass
class OnBroadcastCellAppDataChangedParsedMsgData(ParsedMsgData):
    isDelete: KBEBool
    key: Any = None
    value: Any = None


@dataclass(frozen=True)
class OnBroadcastCellAppDataChangedMsgParserResult(MsgParserResult):
    """Парсер для Cellapp::OnBroadcastCellAppDataChanged.

    Это колбэк в скрипты на изменение глобальных CellData (onCellAppData,
    onCellAppDataDel).
    """

    success: bool
    result: OnBroadcastCellAppDataChangedParsedMsgData
    msg_id: int = msgspec.cellapp.onBroadcastCellAppDataChanged.id
    text: str = ""


class OnBroadcastCellAppDataChangedMsgParser(IMsgParser):
    def parse(self, msg: Message) -> OnBroadcastCellAppDataChangedMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])
        is_deleted, offset = BOOL.decode(data)
        data = data[offset:]
        pd = OnBroadcastCellAppDataChangedParsedMsgData(is_deleted)
        key_data, offset = BLOB.decode(data)
        data = data[offset:]
        pd.key = pickle.loads(key_data)
        if pd.isDelete:
            # В компоненте на C++ будет вызван колбэк в Python onCellAppDataDel
            return OnBroadcastCellAppDataChangedMsgParserResult(True, pd)

        value_data, offset = BLOB.decode(data)
        data = data[offset:]
        pd.value = pickle.loads(value_data)
        assert not data
        # В компоненте на C++ будет вызван колбэк в Python onCellAppData
        return OnBroadcastCellAppDataChangedMsgParserResult(True, pd)


@dataclass
class OnCreateCellEntityFromBaseappParsedMsgData(ParsedMsgData):
    createToEntityID: KBEEntityId
    entityType: KBEString
    entityID: KBEEntityId
    componentID: KBEComponentId
    hasClient: KBEBool
    inRescore: KBEBool


@dataclass(frozen=True)
class OnCreateCellEntityFromBaseappMsgParserResult(MsgParserResult):
    """Результат парсера Cellapp::onCreateCellEntityFromBaseapp."""

    success: bool
    result: OnCreateCellEntityFromBaseappParsedMsgData
    msg_id: int = msgspec.cellapp.onCreateCellEntityFromBaseapp.id
    text: str = ""


class OnCreateCellEntityFromBaseappMsgParser(IMsgParser):
    """Парсер для Cellapp::onCreateCellEntityFromBaseapp."""

    def parse(self, msg: Message) -> OnCreateCellEntityFromBaseappMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])

        createToEntityID, offset = ENTITY_ID.decode(data)
        data = data[offset:]
        entityType, offset = STRING.decode(data)
        data = data[offset:]
        entityID, offset = ENTITY_ID.decode(data)
        data = data[offset:]
        componentID, offset = COMPONENT_ID.decode(data)
        data = data[offset:]
        hasClient, offset = BOOL.decode(data)
        data = data[offset:]
        inRestore, offset = BOOL.decode(data)
        data = data[offset:]
        # [2023-06-22 15:01 burov_alexey@mail.ru]:
        # Эти данные можно распарсить так же, как парсятся свойства у
        # клиентских методов (с учётом оптимизации через usePropertyDescrAlias)
        _cell_data, offset = UINT8_ARRAY.decode(data)
        data = data[offset:]
        pd = OnCreateCellEntityFromBaseappParsedMsgData(
            createToEntityID,
            entityType,
            entityID,
            componentID,
            hasClient,
            inRestore,
        )
        return OnCreateCellEntityFromBaseappMsgParserResult(True, pd)


@dataclass(frozen=True)
class OnCreateCellEntityInNewSpaceFromBaseappMsgParserResult(MsgParserResult):
    """Результат парсера Cellapp::onCreateCellEntityInNewSpaceFromBaseapp."""

    success: bool
    result: CreateCellEntityInNewSpaceFromBaseappParsedMsgData
    msg_id: int = msgspec.cellapp.onCreateCellEntityInNewSpaceFromBaseapp.id
    text: str = ""


class OnCreateCellEntityInNewSpaceFromBaseappMsgParser(IMsgParser):
    """Парсер для Cellapp::onCreateCellEntityInNewSpaceFromBaseapp."""

    def parse(
        self, msg: Message
    ) -> OnCreateCellEntityInNewSpaceFromBaseappMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        pd = CreateCellEntityInNewSpaceFromBaseappParser().parse(msg)
        return OnCreateCellEntityInNewSpaceFromBaseappMsgParserResult(True, pd)


@dataclass(frozen=True)
class OnRegisterNewAppMsgParserResult(MsgParserResult):
    """Результат парсера Cellapp::onRegisterNewApp."""

    success: bool
    result: OnRegisterNewAppParsedMsgData
    msg_id: int = msgspec.cellapp.onRegisterNewApp.id
    text: str = ""


class OnRegisterNewAppMsgParser(IMsgParser):
    """Парсер для Cellapp::onRegisterNewApp."""

    def parse(self, msg: Message) -> OnRegisterNewAppMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnRegisterNewAppParsedMsgData(*values)
        return OnRegisterNewAppMsgParserResult(True, pd)
