"""Обработчик сообщений от компонента Cellapp."""

import logging
import pickle
from dataclasses import dataclass
from typing import Any, ClassVar

from enki import msgspec
from enki.core.kbepickle.kbepickle import pickle_global_data_value
from enki.kbeenum import (
    COMPONENT_STATE_BY_SHUTDOWN_STATE,
    ComponentState,
    ComponentType,
    ShutdownState,
)
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
    KBEComponentType,
    KBEEntityId,
    KBEShutdownState,
)
from enki.kbetype.pytypes.basic_data_types import (
    KBEBool,
    KBERowByteData,
    KBEString,
)
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

    def parse(
        self, msg: Message
    ) -> OnBroadcastGlobalDataChangedMsgParserResult:
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
    def parse(
        self, msg: Message
    ) -> OnBroadcastCellAppDataChangedMsgParserResult:
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

    def parse(
        self, msg: Message
    ) -> OnCreateCellEntityFromBaseappMsgParserResult:
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


@dataclass
class ReqBackupEntityCellDataParsedMsgData(ParsedMsgData):
    """Распарсенные данные для Cellapp::reqBackupEntityCellData."""

    entity_cell_data: (
        KBERowByteData  # Бинарные данные сущности для резервного копирования
    )


@dataclass(frozen=True)
class ReqBackupEntityCellDataMsgParserResult(MsgParserResult):
    """Результат парсера Cellapp::reqBackupEntityCellData."""

    success: bool
    result: ReqBackupEntityCellDataParsedMsgData
    msg_id: int = msgspec.cellapp.reqBackupEntityCellData.id
    text: str = ""


class ReqBackupEntityCellDataMsgParser(IMsgParser):
    """Парсер для Cellapp::reqBackupEntityCellData."""

    def parse(self, msg: Message) -> ReqBackupEntityCellDataMsgParserResult:
        """Обработка сообщения резервного копирования данных клетки сущности."""
        logger.debug("[%s] %s", self, devonly.func_args_values())

        # Получаем UINT8_ARRAY из сообщения
        values: tuple[Any, ...] = msg.get_values()

        # Извлекаем бинарные данные
        entity_cell_data = KBERowByteData(values[0])

        # Создаем объект с распарсенными данными
        pd = ReqBackupEntityCellDataParsedMsgData(entity_cell_data)

        # Логируем размер данных для отладки
        logger.debug(
            "[%s] Backup data size: %d bytes", self, len(entity_cell_data)
        )

        return ReqBackupEntityCellDataMsgParserResult(True, pd)


@dataclass
class QueryLoadParsedMsgData(ParsedMsgData):
    """Parsed data for Cellapp::queryLoad."""

    load_data: KBERowByteData  # Binary load data


@dataclass(frozen=True)
class QueryLoadMsgParserResult(MsgParserResult):
    """Result parser for Cellapp::queryLoad."""

    success: bool
    result: QueryLoadParsedMsgData
    msg_id: int = msgspec.cellapp.queryLoad.id
    text: str = ""


class QueryLoadMsgParser(IMsgParser):
    """Parser for Cellapp::queryLoad."""

    def parse(self, msg: Message) -> QueryLoadMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        load_data = KBERowByteData(values[0])
        pd = QueryLoadParsedMsgData(load_data)
        return QueryLoadMsgParserResult(True, pd)


@dataclass
class OnExecScriptCommandParsedMsgData(ParsedMsgData):
    """Parsed data for Cellapp::onExecScriptCommand."""

    script_data: KBERowByteData  # Binary script command data


@dataclass(frozen=True)
class OnExecScriptCommandMsgParserResult(MsgParserResult):
    """Result parser for Cellapp::onExecScriptCommand."""

    success: bool
    result: OnExecScriptCommandParsedMsgData
    msg_id: int = msgspec.cellapp.onExecScriptCommand.id
    text: str = ""


class OnExecScriptCommandMsgParser(IMsgParser):
    """Parser for Cellapp::onExecScriptCommand."""

    def parse(self, msg: Message) -> OnExecScriptCommandMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        script_data = KBERowByteData(values[0])
        pd = OnExecScriptCommandParsedMsgData(script_data)
        return OnExecScriptCommandMsgParserResult(True, pd)


@dataclass
class OnReqAllocEntityIDParsedMsgData(ParsedMsgData):
    """Parsed data for Cellapp::onReqAllocEntityID."""

    alloc_data: KBERowByteData  # Binary allocation data


@dataclass(frozen=True)
class OnReqAllocEntityIDMsgParserResult(MsgParserResult):
    """Result parser for Cellapp::onReqAllocEntityID."""

    success: bool
    result: OnReqAllocEntityIDParsedMsgData
    msg_id: int = msgspec.cellapp.onReqAllocEntityID.id
    text: str = ""


class OnReqAllocEntityIDMsgParser(IMsgParser):
    """Parser for Cellapp::onReqAllocEntityID."""

    def parse(self, msg: Message) -> OnReqAllocEntityIDMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        alloc_data = KBERowByteData(values[0])
        pd = OnReqAllocEntityIDParsedMsgData(alloc_data)
        return OnReqAllocEntityIDMsgParserResult(True, pd)


@dataclass
class OnRestoreSpaceInCellFromBaseappParsedMsgData(ParsedMsgData):
    """Parsed data for Cellapp::onRestoreSpaceInCellFromBaseapp."""

    restore_data: KBERowByteData  # Binary space restore data


@dataclass(frozen=True)
class OnRestoreSpaceInCellFromBaseappMsgParserResult(MsgParserResult):
    """Result parser for Cellapp::onRestoreSpaceInCellFromBaseapp."""

    success: bool
    result: OnRestoreSpaceInCellFromBaseappParsedMsgData
    msg_id: int = msgspec.cellapp.onRestoreSpaceInCellFromBaseapp.id
    text: str = ""


class OnRestoreSpaceInCellFromBaseappMsgParser(IMsgParser):
    """Parser for Cellapp::onRestoreSpaceInCellFromBaseapp."""

    def parse(
        self, msg: Message
    ) -> OnRestoreSpaceInCellFromBaseappMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        restore_data = KBERowByteData(values[0])
        pd = OnRestoreSpaceInCellFromBaseappParsedMsgData(restore_data)
        return OnRestoreSpaceInCellFromBaseappMsgParserResult(True, pd)


@dataclass
class RequestRestoreParsedMsgData(ParsedMsgData):
    """Parsed data for Cellapp::requestRestore."""

    request_data: KBERowByteData  # Binary restore request data


@dataclass(frozen=True)
class RequestRestoreMsgParserResult(MsgParserResult):
    """Result parser for Cellapp::requestRestore."""

    success: bool
    result: RequestRestoreParsedMsgData
    msg_id: int = msgspec.cellapp.requestRestore.id
    text: str = ""


class RequestRestoreMsgParser(IMsgParser):
    """Parser for Cellapp::requestRestore."""

    def parse(self, msg: Message) -> RequestRestoreMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        request_data = KBERowByteData(values[0])
        pd = RequestRestoreParsedMsgData(request_data)
        return RequestRestoreMsgParserResult(True, pd)


@dataclass
class OnDestroyCellEntityFromBaseappParsedMsgData(ParsedMsgData):
    """Parsed data for Cellapp::onDestroyCellEntityFromBaseapp."""

    destroy_data: KBERowByteData  # Binary entity destruction data


@dataclass(frozen=True)
class OnDestroyCellEntityFromBaseappMsgParserResult(MsgParserResult):
    """Result parser for Cellapp::onDestroyCellEntityFromBaseapp."""

    success: bool
    result: OnDestroyCellEntityFromBaseappParsedMsgData
    msg_id: int = msgspec.cellapp.onDestroyCellEntityFromBaseapp.id
    text: str = ""


class OnDestroyCellEntityFromBaseappMsgParser(IMsgParser):
    """Parser for Cellapp::onDestroyCellEntityFromBaseapp."""

    def parse(
        self, msg: Message
    ) -> OnDestroyCellEntityFromBaseappMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        destroy_data = KBERowByteData(values[0])
        pd = OnDestroyCellEntityFromBaseappParsedMsgData(destroy_data)
        return OnDestroyCellEntityFromBaseappMsgParserResult(True, pd)


@dataclass
class OnEntityCallParsedMsgData(ParsedMsgData):
    """Parsed data for Cellapp::onEntityCall."""

    entity_call_data: KBERowByteData  # Binary entity call data


@dataclass(frozen=True)
class OnEntityCallMsgParserResult(MsgParserResult):
    """Result parser for Cellapp::onEntityCall."""

    success: bool
    result: OnEntityCallParsedMsgData
    msg_id: int = msgspec.cellapp.onEntityCall.id
    text: str = ""


class OnEntityCallMsgParser(IMsgParser):
    """Parser for Cellapp::onEntityCall."""

    def parse(self, msg: Message) -> OnEntityCallMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        entity_call_data = KBERowByteData(values[0])
        pd = OnEntityCallParsedMsgData(entity_call_data)
        return OnEntityCallMsgParserResult(True, pd)


@dataclass
class OnRemoteCallMethodFromClientParsedMsgData(ParsedMsgData):
    """Parsed data for Cellapp::onRemoteCallMethodFromClient."""

    remote_call_data: (
        KBERowByteData  # Binary remote method call data from client
    )


@dataclass(frozen=True)
class OnRemoteCallMethodFromClientMsgParserResult(MsgParserResult):
    """Result parser for Cellapp::onRemoteCallMethodFromClient."""

    success: bool
    result: OnRemoteCallMethodFromClientParsedMsgData
    msg_id: int = msgspec.cellapp.onRemoteCallMethodFromClient.id
    text: str = ""


class OnRemoteCallMethodFromClientMsgParser(IMsgParser):
    """Parser for Cellapp::onRemoteCallMethodFromClient."""

    def parse(
        self, msg: Message
    ) -> OnRemoteCallMethodFromClientMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        remote_call_data = KBERowByteData(values[0])
        pd = OnRemoteCallMethodFromClientParsedMsgData(remote_call_data)
        return OnRemoteCallMethodFromClientMsgParserResult(True, pd)


@dataclass
class OnUpdateDataFromClientParsedMsgData(ParsedMsgData):
    """Parsed data for Cellapp::onUpdateDataFromClient."""

    update_data: KBERowByteData  # Binary entity data update from client


@dataclass(frozen=True)
class OnUpdateDataFromClientMsgParserResult(MsgParserResult):
    """Result parser for Cellapp::onUpdateDataFromClient."""

    success: bool
    result: OnUpdateDataFromClientParsedMsgData
    msg_id: int = msgspec.cellapp.onUpdateDataFromClient.id
    text: str = ""


class OnUpdateDataFromClientMsgParser(IMsgParser):
    """Parser for Cellapp::onUpdateDataFromClient."""

    def parse(self, msg: Message) -> OnUpdateDataFromClientMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        update_data = KBERowByteData(values[0])
        pd = OnUpdateDataFromClientParsedMsgData(update_data)
        return OnUpdateDataFromClientMsgParserResult(True, pd)


@dataclass
class OnUpdateDataFromClientForControlledEntityParsedMsgData(ParsedMsgData):
    """Parsed data for Cellapp::onUpdateDataFromClientForControlledEntity."""

    controlled_update_data: (
        KBERowByteData  # Binary controlled entity update data
    )


@dataclass(frozen=True)
class OnUpdateDataFromClientForControlledEntityMsgParserResult(MsgParserResult):
    """Result parser for Cellapp::onUpdateDataFromClientForControlledEntity."""

    success: bool
    result: OnUpdateDataFromClientForControlledEntityParsedMsgData
    msg_id: int = msgspec.cellapp.onUpdateDataFromClientForControlledEntity.id
    text: str = ""


class OnUpdateDataFromClientForControlledEntityMsgParser(IMsgParser):
    """Parser for Cellapp::onUpdateDataFromClientForControlledEntity."""

    def parse(
        self, msg: Message
    ) -> OnUpdateDataFromClientForControlledEntityMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        controlled_update_data = KBERowByteData(values[0])
        pd = OnUpdateDataFromClientForControlledEntityParsedMsgData(
            controlled_update_data
        )
        return OnUpdateDataFromClientForControlledEntityMsgParserResult(
            True, pd
        )


@dataclass
class OnExecuteRawDatabaseCommandCBParsedMsgData(ParsedMsgData):
    """Parsed data for Cellapp::onExecuteRawDatabaseCommandCB."""

    db_command_data: KBERowByteData  # Binary database command callback data


@dataclass(frozen=True)
class OnExecuteRawDatabaseCommandCBMsgParserResult(MsgParserResult):
    """Result parser for Cellapp::onExecuteRawDatabaseCommandCB."""

    success: bool
    result: OnExecuteRawDatabaseCommandCBParsedMsgData
    msg_id: int = msgspec.cellapp.onExecuteRawDatabaseCommandCB.id
    text: str = ""


class OnExecuteRawDatabaseCommandCBMsgParser(IMsgParser):
    """Parser for Cellapp::onExecuteRawDatabaseCommandCB."""

    def parse(
        self, msg: Message
    ) -> OnExecuteRawDatabaseCommandCBMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        db_command_data = KBERowByteData(values[0])
        pd = OnExecuteRawDatabaseCommandCBParsedMsgData(db_command_data)
        return OnExecuteRawDatabaseCommandCBMsgParserResult(True, pd)


@dataclass
class ReqWriteToDBFromBaseappParsedMsgData(ParsedMsgData):
    """Parsed data for Cellapp::reqWriteToDBFromBaseapp."""

    write_db_data: KBERowByteData  # Binary write to database data from BaseApp


@dataclass(frozen=True)
class ReqWriteToDBFromBaseappMsgParserResult(MsgParserResult):
    """Result parser for Cellapp::reqWriteToDBFromBaseapp."""

    success: bool
    result: ReqWriteToDBFromBaseappParsedMsgData
    msg_id: int = msgspec.cellapp.reqWriteToDBFromBaseapp.id
    text: str = ""


class ReqWriteToDBFromBaseappMsgParser(IMsgParser):
    """Parser for Cellapp::reqWriteToDBFromBaseapp."""

    def parse(self, msg: Message) -> ReqWriteToDBFromBaseappMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        write_db_data = KBERowByteData(values[0])
        pd = ReqWriteToDBFromBaseappParsedMsgData(write_db_data)
        return ReqWriteToDBFromBaseappMsgParserResult(True, pd)


@dataclass
class ForwardEntityMessageToCellappFromClientParsedMsgData(ParsedMsgData):
    """Parsed data for Cellapp::forwardEntityMessageToCellappFromClient."""

    forwarded_message_data: (
        KBERowByteData  # Binary forwarded entity message data
    )


@dataclass(frozen=True)
class ForwardEntityMessageToCellappFromClientMsgParserResult(MsgParserResult):
    """Result parser for Cellapp::forwardEntityMessageToCellappFromClient."""

    success: bool
    result: ForwardEntityMessageToCellappFromClientParsedMsgData
    msg_id: int = msgspec.cellapp.forwardEntityMessageToCellappFromClient.id
    text: str = ""


class ForwardEntityMessageToCellappFromClientMsgParser(IMsgParser):
    """Parser for Cellapp::forwardEntityMessageToCellappFromClient."""

    def parse(
        self, msg: Message
    ) -> ForwardEntityMessageToCellappFromClientMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        forwarded_message_data = KBERowByteData(values[0])
        pd = ForwardEntityMessageToCellappFromClientParsedMsgData(
            forwarded_message_data
        )
        return ForwardEntityMessageToCellappFromClientMsgParserResult(True, pd)


@dataclass
class QueryWatcherParsedMsgData(ParsedMsgData):
    """Parsed data for Cellapp::queryWatcher."""

    watcher_query_data: KBERowByteData  # Binary watcher query data


@dataclass(frozen=True)
class QueryWatcherMsgParserResult(MsgParserResult):
    """Result parser for Cellapp::queryWatcher."""

    success: bool
    result: QueryWatcherParsedMsgData
    msg_id: int = msgspec.cellapp.queryWatcher.id
    text: str = ""


class QueryWatcherMsgParser(IMsgParser):
    """Parser for Cellapp::queryWatcher."""

    def parse(self, msg: Message) -> QueryWatcherMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        watcher_query_data = KBERowByteData(values[0])
        pd = QueryWatcherParsedMsgData(watcher_query_data)
        return QueryWatcherMsgParserResult(True, pd)


@dataclass
class StartProfileParsedMsgData(ParsedMsgData):
    """Parsed data for Cellapp::startProfile."""

    profile_data: KBERowByteData  # Binary profiling data


@dataclass(frozen=True)
class StartProfileMsgParserResult(MsgParserResult):
    """Result parser for Cellapp::startProfile."""

    success: bool
    result: StartProfileParsedMsgData
    msg_id: int = msgspec.cellapp.startProfile.id
    text: str = ""


class StartProfileMsgParser(IMsgParser):
    """Parser for Cellapp::startProfile."""

    def parse(self, msg: Message) -> StartProfileMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        profile_data = KBERowByteData(values[0])
        pd = StartProfileParsedMsgData(profile_data)
        return StartProfileMsgParserResult(True, pd)


@dataclass
class ReqTeleportToCellAppParsedMsgData(ParsedMsgData):
    """Parsed data for Cellapp::reqTeleportToCellApp."""

    teleport_data: KBERowByteData  # Binary teleport request data


@dataclass(frozen=True)
class ReqTeleportToCellAppMsgParserResult(MsgParserResult):
    """Result parser for Cellapp::reqTeleportToCellApp."""

    success: bool
    result: ReqTeleportToCellAppParsedMsgData
    msg_id: int = msgspec.cellapp.reqTeleportToCellApp.id
    text: str = ""


class ReqTeleportToCellAppMsgParser(IMsgParser):
    """Parser for Cellapp::reqTeleportToCellApp."""

    def parse(self, msg: Message) -> ReqTeleportToCellAppMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        teleport_data = KBERowByteData(values[0])
        pd = ReqTeleportToCellAppParsedMsgData(teleport_data)
        return ReqTeleportToCellAppMsgParserResult(True, pd)


@dataclass
class ReqTeleportToCellAppCBParsedMsgData(ParsedMsgData):
    """Parsed data for Cellapp::reqTeleportToCellAppCB."""

    teleport_callback_data: KBERowByteData  # Binary teleport callback data


@dataclass(frozen=True)
class ReqTeleportToCellAppCBMsgParserResult(MsgParserResult):
    """Result parser for Cellapp::reqTeleportToCellAppCB."""

    success: bool
    result: ReqTeleportToCellAppCBParsedMsgData
    msg_id: int = msgspec.cellapp.reqTeleportToCellAppCB.id
    text: str = ""


class ReqTeleportToCellAppCBMsgParser(IMsgParser):
    """Parser for Cellapp::reqTeleportToCellAppCB."""

    def parse(self, msg: Message) -> ReqTeleportToCellAppCBMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        teleport_callback_data = KBERowByteData(values[0])
        pd = ReqTeleportToCellAppCBParsedMsgData(teleport_callback_data)
        return ReqTeleportToCellAppCBMsgParserResult(True, pd)


@dataclass
class ReqTeleportToCellAppOverParsedMsgData(ParsedMsgData):
    """Parsed data for Cellapp::reqTeleportToCellAppOver."""

    teleport_complete_data: KBERowByteData  # Binary teleport completion data


@dataclass(frozen=True)
class ReqTeleportToCellAppOverMsgParserResult(MsgParserResult):
    """Result parser for Cellapp::reqTeleportToCellAppOver."""

    success: bool
    result: ReqTeleportToCellAppOverParsedMsgData
    msg_id: int = msgspec.cellapp.reqTeleportToCellAppOver.id
    text: str = ""


class ReqTeleportToCellAppOverMsgParser(IMsgParser):
    """Parser for Cellapp::reqTeleportToCellAppOver."""

    def parse(self, msg: Message) -> ReqTeleportToCellAppOverMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        teleport_complete_data = KBERowByteData(values[0])
        pd = ReqTeleportToCellAppOverParsedMsgData(teleport_complete_data)
        return ReqTeleportToCellAppOverMsgParserResult(True, pd)


@dataclass
class OnUpdateGhostPropertysParsedMsgData(ParsedMsgData):
    """Parsed data for Cellapp::onUpdateGhostPropertys."""

    ghost_properties_data: KBERowByteData  # Binary ghost properties update data


@dataclass(frozen=True)
class OnUpdateGhostPropertysMsgParserResult(MsgParserResult):
    """Result parser for Cellapp::onUpdateGhostPropertys."""

    success: bool
    result: OnUpdateGhostPropertysParsedMsgData
    msg_id: int = msgspec.cellapp.onUpdateGhostPropertys.id
    text: str = ""


class OnUpdateGhostPropertysMsgParser(IMsgParser):
    """Parser for Cellapp::onUpdateGhostPropertys."""

    def parse(self, msg: Message) -> OnUpdateGhostPropertysMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        ghost_properties_data = KBERowByteData(values[0])
        pd = OnUpdateGhostPropertysParsedMsgData(ghost_properties_data)
        return OnUpdateGhostPropertysMsgParserResult(True, pd)


@dataclass
class OnRemoteRealMethodCallParsedMsgData(ParsedMsgData):
    """Parsed data for Cellapp::onRemoteRealMethodCall."""

    remote_real_method_data: (
        KBERowByteData  # Binary remote real method call data
    )


@dataclass(frozen=True)
class OnRemoteRealMethodCallMsgParserResult(MsgParserResult):
    """Result parser for Cellapp::onRemoteRealMethodCall."""

    success: bool
    result: OnRemoteRealMethodCallParsedMsgData
    msg_id: int = msgspec.cellapp.onRemoteRealMethodCall.id
    text: str = ""


class OnRemoteRealMethodCallMsgParser(IMsgParser):
    """Parser for Cellapp::onRemoteRealMethodCall."""

    def parse(self, msg: Message) -> OnRemoteRealMethodCallMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        remote_real_method_data = KBERowByteData(values[0])
        pd = OnRemoteRealMethodCallParsedMsgData(remote_real_method_data)
        return OnRemoteRealMethodCallMsgParserResult(True, pd)


@dataclass
class OnUpdateGhostVolatileDataParsedMsgData(ParsedMsgData):
    """Parsed data for Cellapp::onUpdateGhostVolatileData."""

    ghost_volatile_data: KBERowByteData  # Binary ghost volatile data update


@dataclass(frozen=True)
class OnUpdateGhostVolatileDataMsgParserResult(MsgParserResult):
    """Result parser for Cellapp::onUpdateGhostVolatileData."""

    success: bool
    result: OnUpdateGhostVolatileDataParsedMsgData
    msg_id: int = msgspec.cellapp.onUpdateGhostVolatileData.id
    text: str = ""


class OnUpdateGhostVolatileDataMsgParser(IMsgParser):
    """Parser for Cellapp::onUpdateGhostVolatileData."""

    def parse(self, msg: Message) -> OnUpdateGhostVolatileDataMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        ghost_volatile_data = KBERowByteData(values[0])
        pd = OnUpdateGhostVolatileDataParsedMsgData(ghost_volatile_data)
        return OnUpdateGhostVolatileDataMsgParserResult(True, pd)


@dataclass
class ReqKillServerParsedMsgData(ParsedMsgData):
    """Parsed data for Cellapp::reqKillServer."""

    kill_server_data: KBERowByteData  # Binary kill server request data


@dataclass(frozen=True)
class ReqKillServerMsgParserResult(MsgParserResult):
    """Result parser for Cellapp::reqKillServer."""

    success: bool
    result: ReqKillServerParsedMsgData
    msg_id: int = msgspec.cellapp.reqKillServer.id
    text: str = ""


class ReqKillServerMsgParser(IMsgParser):
    """Parser for Cellapp::reqKillServer."""

    def parse(self, msg: Message) -> ReqKillServerMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        kill_server_data = KBERowByteData(values[0])
        pd = ReqKillServerParsedMsgData(kill_server_data)
        return ReqKillServerMsgParserResult(True, pd)


@dataclass
class ReqSetFlagsParsedMsgData(ParsedMsgData):
    """Parsed data for Cellapp::reqSetFlags."""

    set_flags_data: KBERowByteData  # Binary set flags request data


@dataclass(frozen=True)
class ReqSetFlagsMsgParserResult(MsgParserResult):
    """Result parser for Cellapp::reqSetFlags."""

    success: bool
    result: ReqSetFlagsParsedMsgData
    msg_id: int = msgspec.cellapp.reqSetFlags.id
    text: str = ""


class ReqSetFlagsMsgParser(IMsgParser):
    """Parser for Cellapp::reqSetFlags."""

    def parse(self, msg: Message) -> ReqSetFlagsMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        set_flags_data = KBERowByteData(values[0])
        pd = ReqSetFlagsParsedMsgData(set_flags_data)
        return ReqSetFlagsMsgParserResult(True, pd)


@dataclass
class SetSpaceViewerParsedMsgData(ParsedMsgData):
    """Parsed data for Cellapp::setSpaceViewer."""

    space_viewer_data: KBERowByteData  # Binary space viewer set data


@dataclass(frozen=True)
class SetSpaceViewerMsgParserResult(MsgParserResult):
    """Result parser for Cellapp::setSpaceViewer."""

    success: bool
    result: SetSpaceViewerParsedMsgData
    msg_id: int = msgspec.cellapp.setSpaceViewer.id
    text: str = ""


class SetSpaceViewerMsgParser(IMsgParser):
    """Parser for Cellapp::setSpaceViewer."""

    def parse(self, msg: Message) -> SetSpaceViewerMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        space_viewer_data = KBERowByteData(values[0])
        pd = SetSpaceViewerParsedMsgData(space_viewer_data)
        return SetSpaceViewerMsgParserResult(True, pd)


@dataclass
class LookAppParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Cellapp::lookApp."""


@dataclass(frozen=True)
class LookAppMsgParserResult(MsgParserResult):
    """Результат парсинга Cellapp::lookApp."""

    success: bool
    result: LookAppParsedMsgData
    msg_id: int = msgspec.cellapp.lookApp.id
    text: str = ""


class LookAppMsgParser(IMsgParser):
    """Парсер для Cellapp::lookApp."""

    def parse(self, msg: Message) -> LookAppMsgParserResult:
        """Распарсить сообщение Cellapp::lookApp.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            LookAppMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        pd = LookAppParsedMsgData(*values)
        return LookAppMsgParserResult(success=True, result=pd)


@dataclass
class OnLookAppParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Cellapp::onLookApp."""

    componentType: KBEComponentType  # noqa: N815
    componentId: KBEComponentId  # noqa: N815
    shutdownState: KBEShutdownState  # noqa: N815

    @property
    def component_type(self) -> ComponentType:
        """Возвращает тип компонента в виде enum ComponentType.

        Returns:
            ComponentType: Тип текущего компонента

        """
        return ComponentType(self.componentType)

    @property
    def component_state(self) -> ComponentState:
        """Возвращает состояние компонента.

        Returns:
            ComponentType: Тип текущего компонента

        """
        return COMPONENT_STATE_BY_SHUTDOWN_STATE[
            ShutdownState(self.shutdownState)
        ]

    __add_to_dict__: ClassVar = ("component_type", "component_state")


@dataclass(frozen=True)
class OnLookAppParserMsgParserResult(MsgParserResult):
    """Парсер для Cellapp::onLookApp."""

    success: bool
    result: OnLookAppParsedMsgData
    msg_id: int = msgspec.cellapp.onLookApp.id
    text: str = ""


class OnLookAppMsgParser(IMsgParser):
    """Парсер для Cellapp::onLookApp."""

    def parse(self, msg: Message) -> OnLookAppParserMsgParserResult:
        """Распарсить сообщение Cellapp::onLookApp.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnLookAppParserMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnLookAppParsedMsgData(*values)
        return OnLookAppParserMsgParserResult(success=True, result=pd)
