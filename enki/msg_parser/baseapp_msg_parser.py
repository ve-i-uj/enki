"""Обработчик сообщений от компонента Baseapp."""

from __future__ import annotations

import logging
import pickle
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar

from enki import msgspec
from enki.core.kbepickle.kbepickle import pickle_global_data_value
from enki.kbeenum import (
    COMPONENT_STATE_BY_SHUTDOWN_STATE,
    ClientType,
    ComponentState,
    ComponentType,
    ShutdownState,
)
from enki.kbetype.decoders.basic_data_type_decoders import (
    BLOB,
    BOOL,
    INT32,
    UINT16,
)
from enki.kbetype.decoders.custom_decoders import (
    DBID,
    ENTITY_SCRIPT_UID,
    KBECallbackId,
    KBEComponentId,
    KBEComponentType,
    KBEDbid,
    KBEEntityId,
    KBESpaceId,
)
from enki.kbetype.pytypes.basic_data_types import KBEBlob, KBERowByteData
from enki.misc import devonly

from .common import (
    CreateEntityAnywhereMsgParser,
    CreateEntityAnywhereParsedMsgData,
    OnAppActiveTickParsedMsgData,
    OnDbmgrInitCompletedParsedMsgData,
    OnGetEntityAppFromDbmgrParsedMsgData,
    OnRegisterNewAppParsedMsgData,
)
from .imsg_parser import (
    IMsgParser,
    MsgParserResult,
    ParsedMsgData,
)

if TYPE_CHECKING:
    from enki.kbetype.pytypes.basic_data_types import (
        KBEBool,
        KBEFloat,
        KBEInt8,
        KBEInt32,
        KBEString,
        KBEUInt16,
        KBEUInt32,
        KBEUInt64,
    )
    from enki.msg.message import Message

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OnCreateEntityAnywhereMsgParserResult(MsgParserResult):
    """Результат парсера сообщения BaseappMgr::reqCreateEntityAnywhere.

    Args:
        success: Успешность обработки сообщения.
        result: Результат парсинга.
        msg_id: ID сообщения.
        text: Текст результата.

    """

    success: bool
    result: CreateEntityAnywhereParsedMsgData | None
    msg_id: int = msgspec.baseapp.onCreateEntityAnywhere.id
    text: str = ""


class OnCreateEntityAnywhereMsgParser(IMsgParser):
    """Парсер для BaseappMgr::reqCreateEntityAnywhere."""

    def parse(self, msg: Message) -> OnCreateEntityAnywhereMsgParserResult:
        """Обработать сообщение BaseappMgr::reqCreateEntityAnywhere.

        Args:
            msg: KBEngine-сообщение.

        Returns:
            OnCreateEntityAnywhereMsgParserResult: объект результата обработки.

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        res = CreateEntityAnywhereMsgParser().parse(msg)

        return OnCreateEntityAnywhereMsgParserResult(
            success=res.success, result=res.result, text=res.text
        )


@dataclass(frozen=True)
class OnGetEntityAppFromDbmgrMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::onGetEntityAppFromDbmgr.

    Args:
        success: Успешность обработки сообщения.
        result: Результат парсинга.
        msg_id: ID сообщения.
        text: Текст результата.

    """

    success: bool
    result: OnGetEntityAppFromDbmgrParsedMsgData
    msg_id: int = msgspec.baseapp.onGetEntityAppFromDbmgr.id
    text: str = ""


class OnGetEntityAppFromDbmgrMsgParser(IMsgParser):
    """Парсер для Baseapp::onGetEntityAppFromDbmgr."""

    def parse(self, msg: Message) -> OnGetEntityAppFromDbmgrMsgParserResult:
        """Обработать сообщение Baseapp::onGetEntityAppFromDbmgr.

        Args:
            msg: KBEngine-сообщение.

        Returns:
            OnGetEntityAppFromDbmgrMsgParserResult: объект результата обработки.

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnGetEntityAppFromDbmgrParsedMsgData(*values)
        return OnGetEntityAppFromDbmgrMsgParserResult(success=True, result=pd)


@dataclass(frozen=True)
class OnDbmgrInitCompletedMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::onDbmgrInitCompleted.

    Args:
        success: Успешность обработки сообщения.
        result: Результат парсинга.
        msg_id: ID сообщения.
        text: Текст результата.

    """

    success: bool
    result: OnDbmgrInitCompletedParsedMsgData
    msg_id: int = msgspec.baseapp.onDbmgrInitCompleted.id
    text: str = ""


class OnDbmgrInitCompletedMsgParser(IMsgParser):
    """Парсер для Baseapp::onDbmgrInitCompleted."""

    def parse(self, msg: Message) -> OnDbmgrInitCompletedMsgParserResult:
        """Обработать сообщение Baseapp::onDbmgrInitCompleted.

        Args:
            msg: KBEngine-сообщение.

        Returns:
            OnDbmgrInitCompletedMsgParserResult: объект результата обработки.

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnDbmgrInitCompletedParsedMsgData(*values)
        return OnDbmgrInitCompletedMsgParserResult(success=True, result=pd)


@dataclass
class OnEntityAutoLoadCBFromDBMgrParsedMsgData(ParsedMsgData):
    """Данные результата парсинга Baseapp::onEntityAutoLoadCBFromDBMgr.

    Args:
        dbInterfaceIndex: Индекс интерфейса БД.
        size: Размер данных.
        entityType: Тип entity.
        dbids: Список ID БД.

    """

    dbInterfaceIndex: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name
    size: KBEInt32
    entityType: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name
    dbids: list[KBEUInt64]


@dataclass(frozen=True)
class OnEntityAutoLoadCBFromDBMgrMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::onEntityAutoLoadCBFromDBMgr.

    Args:
        success: Успешность обработки сообщения.
        result: Результат парсинга.
        msg_id: ID сообщения.
        text: Текст результата.

    """

    success: bool
    result: OnEntityAutoLoadCBFromDBMgrParsedMsgData
    msg_id: int = msgspec.baseapp.onEntityAutoLoadCBFromDBMgr.id
    text: str = ""


class OnEntityAutoLoadCBFromDBMgrMsgParser(IMsgParser):
    """Парсер для Baseapp::onEntityAutoLoadCBFromDBMgr."""

    def parse(self, msg: Message) -> OnEntityAutoLoadCBFromDBMgrMsgParserResult:
        """Обработать сообщение Baseapp::onEntityAutoLoadCBFromDBMgr.

        Args:
            msg: KBEngine-сообщение.

        Returns:
            OnEntityAutoLoadCBFromDBMgrMsgParserResult: объект результата
                обработки.

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])
        dbInterfaceIndex, offset = UINT16.decode(data)  # noqa: N806
        data = data[offset:]
        size, offset = INT32.decode(data)
        data = data[offset:]
        entityType, offset = ENTITY_SCRIPT_UID.decode(data)  # noqa: N806
        data = data[offset:]
        dbids = []
        for _ in range(size):
            dbid, offset = DBID.decode(data)
            data = data[offset:]
            dbids.append(dbid)

        pd = OnEntityAutoLoadCBFromDBMgrParsedMsgData(
            dbInterfaceIndex, size, entityType, dbids
        )
        return OnEntityAutoLoadCBFromDBMgrMsgParserResult(
            success=True, result=pd
        )


@dataclass
class OnBroadcastGlobalDataChangedParsedMsgData(ParsedMsgData):
    """Данные результата парсинга Baseapp::onBroadcastGlobalDataChanged.

    Args:
        isDelete: Флаг удаления.
        key: Ключ данных.
        value: Значение данных.

    """

    isDelete: KBEBool  # noqa: N815  # pylint: disable=invalid-name
    key: KBEString
    value: Any = None


@dataclass(frozen=True)
class OnBroadcastGlobalDataChangedMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::onBroadcastGlobalDataChanged.

    Args:
        success: Успешность обработки сообщения.
        result: Результат парсинга.
        msg_id: ID сообщения.
        text: Текст результата.

    """

    success: bool
    result: OnBroadcastGlobalDataChangedParsedMsgData
    msg_id: int = msgspec.baseapp.onBroadcastGlobalDataChanged.id
    text: str = ""


class OnBroadcastGlobalDataChangedMsgParser(IMsgParser):
    """Парсер для Baseapp::onBroadcastGlobalDataChanged."""

    def parse(
        self, msg: Message
    ) -> OnBroadcastGlobalDataChangedMsgParserResult:
        """Обработать сообщение Baseapp::onBroadcastGlobalDataChanged.

        Args:
            msg: KBEngine-сообщение.

        Returns:
            OnBroadcastGlobalDataChangedMsgParserResult: объект результата
                обработки.

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()

        data = memoryview(values[0])
        isDelete, offset = BOOL.decode(data)  # noqa: N806
        data = data[offset:]

        key_data, offset = BLOB.decode(data)
        data = data[offset:]
        key = pickle.loads(key_data)  # noqa: S301
        if isDelete:
            pd = OnBroadcastGlobalDataChangedParsedMsgData(
                isDelete, key, value=None
            )
            return OnBroadcastGlobalDataChangedMsgParserResult(
                success=True, result=pd
            )

        value_data, offset = BLOB.decode(data)
        data = data[offset:]
        value = pickle_global_data_value(value_data)
        pd = OnBroadcastGlobalDataChangedParsedMsgData(isDelete, key, value)
        assert not data

        return OnBroadcastGlobalDataChangedMsgParserResult(
            success=True, result=pd
        )


@dataclass(frozen=True)
class OnAppActiveTickMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::onAppActiveTick.

    Args:
        success: Успешность обработки сообщения.
        result: Результат парсинга.
        msg_id: ID сообщения.
        text: Текст результата.

    """

    success: bool
    result: OnAppActiveTickParsedMsgData
    msg_id: int = msgspec.baseapp.onAppActiveTick.id
    text: str = ""


class OnAppActiveTickMsgParser(IMsgParser):
    """Парсер для Baseapp::onAppActiveTick."""

    def parse(self, msg: Message) -> OnAppActiveTickMsgParserResult:
        """Обработать сообщение Baseapp::onAppActiveTick.

        Args:
            msg: KBEngine-сообщение.

        Returns:
            OnAppActiveTickMsgParserResult: объект результата обработки.

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnAppActiveTickParsedMsgData(*values)
        return OnAppActiveTickMsgParserResult(success=True, result=pd)


@dataclass(frozen=True)
class OnRegisterNewAppMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseappp::onRegisterNewApp.

    Args:
        success: Успешность обработки сообщения.
        result: Результат парсинга.
        msg_id: ID сообщения.
        text: Текст результата.

    """

    success: bool
    result: OnRegisterNewAppParsedMsgData
    msg_id: int = msgspec.baseapp.onRegisterNewApp.id
    text: str = ""


class OnRegisterNewAppMsgParser(IMsgParser):
    """Парсер для Baseappp::onRegisterNewApp."""

    def parse(self, msg: Message) -> OnRegisterNewAppMsgParserResult:
        """Обработать сообщение Baseappp::onRegisterNewApp.

        Args:
            msg: KBEngine-сообщение.

        Returns:
            OnRegisterNewAppMsgParserResult: объект результата обработки.

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnRegisterNewAppParsedMsgData(*values)
        return OnRegisterNewAppMsgParserResult(success=True, result=pd)


@dataclass
class OnEntityGetCellParsedMsgData(ParsedMsgData):
    """Данные результата парсинга Baseapp::onEntityGetCell.

    Args:
        entity_id: ID entity.
        componentID: ID компонента.
        spaceID: ID пространства.

    """

    entity_id: KBEEntityId
    componentID: KBEComponentId  # noqa: N815  # pylint: disable=invalid-name
    spaceID: KBESpaceId  # noqa: N815  # pylint: disable=invalid-name


@dataclass(frozen=True)
class OnEntityGetCellMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::onEntityGetCell.

    Args:
        success: Успешность обработки сообщения.
        result: Результат парсинга.
        msg_id: ID сообщения.
        text: Текст результата.

    """

    success: bool
    result: OnEntityGetCellParsedMsgData
    msg_id: int = msgspec.baseapp.onEntityGetCell.id
    text: str = ""


class OnEntityGetCellMsgParser(IMsgParser):
    """Парсер для Baseapp::onEntityGetCell."""

    def parse(self, msg: Message) -> OnEntityGetCellMsgParserResult:
        """Обработать сообщение Baseapp::onEntityGetCell.

        Args:
            msg: KBEngine-сообщение.

        Returns:
            OnEntityGetCellMsgParserResult: объект результата обработки.

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnEntityGetCellParsedMsgData(*values)
        return OnEntityGetCellMsgParserResult(success=True, result=pd)


@dataclass
class RegisterPendingLoginParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Baseapp::registerPendingLogin."""

    login: KBEString
    account_name: KBEString
    password: KBEString
    needCheckPassword: KBEBool  # noqa: N815  # pylint: disable=invalid-name
    eid: KBEEntityId
    entityDBID: KBEDbid  # noqa: N815  # pylint: disable=invalid-name
    flags: KBEUInt32
    deadline: KBEUInt64
    clientType: KBEInt32  # noqa: N815  # pylint: disable=invalid-name
    forceInternalLogin: KBEBool  # noqa: N815  # pylint: disable=invalid-name
    datas: KBEString

    @property
    def client_type(self) -> ClientType:
        """Тип клиента.

        Returns:
            ClientType: тип клиента.

        """
        return ClientType(self.clientType)

    __add_to_dict__: ClassVar[tuple[str, ...]] = ("client_type",)


@dataclass(frozen=True)
class RegisterPendingLoginMsgParserResult(MsgParserResult):
    """Парсер для Baseapp::registerPendingLogin."""

    success: bool
    result: RegisterPendingLoginParsedMsgData
    msg_id: int = msgspec.baseapp.registerPendingLogin.id
    text: str = ""


class RegisterPendingLoginMsgParser(IMsgParser):
    """Парсер для Baseapp::registerPendingLogin."""

    def parse(self, msg: Message) -> RegisterPendingLoginMsgParserResult:
        """Распарсить сообщение Baseapp::registerPendingLogin.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            RegisterPendingLoginParserMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = RegisterPendingLoginParsedMsgData(*values)
        return RegisterPendingLoginMsgParserResult(success=True, result=pd)


@dataclass
class HelloParsedMsgData(ParsedMsgData):
    """Данные результата парсинга Baseapp::hello."""

    server_version: KBEString
    assets_version: KBEString
    encrypted_key: KBEBlob


@dataclass(frozen=True)
class HelloMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::hello."""

    success: bool
    result: HelloParsedMsgData
    msg_id: int = msgspec.baseapp.hello.id
    text: str = ""


class HelloMsgParser(IMsgParser):
    """Парсер для Baseapp::hello."""

    def parse(self, msg: Message) -> HelloMsgParserResult:
        """Распарсить сообщение Baseapp::hello.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            HelloMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = HelloParsedMsgData(*values)
        return HelloMsgParserResult(success=True, result=pd)


@dataclass(frozen=True)
class ImportClientMessagesMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::importClientMessages."""

    success: bool
    result: ParsedMsgData
    msg_id: int = msgspec.baseapp.importClientMessages.id
    text: str = ""


class ImportClientMessagesMsgParser(IMsgParser):
    """Парсер для Baseapp::importClientMessages."""

    def parse(self, msg: Message) -> ImportClientMessagesMsgParserResult:
        """Распарсить сообщение Baseapp::importClientMessages.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            ImportClientMessagesMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        return ImportClientMessagesMsgParserResult(
            success=True, result=ParsedMsgData()
        )


@dataclass(frozen=True)
class ImportClientEntityDefMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::importClientEntityDef."""

    success: bool
    result: ParsedMsgData
    msg_id: int = msgspec.baseapp.importClientEntityDef.id
    text: str = ""


class ImportClientEntityDefMsgParser(IMsgParser):
    """Парсер для Baseapp::importClientEntityDef."""

    def parse(self, msg: Message) -> ImportClientEntityDefMsgParserResult:
        """Распарсить сообщение Baseapp::importClientEntityDef.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            ImportClientEntityDefMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        return ImportClientEntityDefMsgParserResult(
            success=True, result=ParsedMsgData()
        )


@dataclass
class OnUpdateDataFromClientParsedMsgData(ParsedMsgData):
    """Данные результата парсинга Baseapp::onUpdateDataFromClient."""

    x: KBEFloat
    y: KBEFloat
    z: KBEFloat
    roll: KBEFloat
    pitch: KBEFloat
    yaw: KBEFloat
    isOnGround: KBEBool  # noqa: N815  # pylint: disable=invalid-name
    spaceID: KBESpaceId  # noqa: N815  # pylint: disable=invalid-name


@dataclass(frozen=True)
class OnUpdateDataFromClientMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::onUpdateDataFromClient."""

    success: bool
    result: OnUpdateDataFromClientParsedMsgData
    msg_id: int = msgspec.baseapp.onUpdateDataFromClient.id
    text: str = ""


class OnUpdateDataFromClientMsgParser(IMsgParser):
    """Парсер для Baseapp::onUpdateDataFromClient."""

    def parse(self, msg: Message) -> OnUpdateDataFromClientMsgParserResult:
        """Распарсить сообщение Baseapp::onUpdateDataFromClient.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnUpdateDataFromClientMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnUpdateDataFromClientParsedMsgData(*values)
        return OnUpdateDataFromClientMsgParserResult(success=True, result=pd)


@dataclass
class OnUpdateDataFromClientForControlledEntityParsedMsgData(ParsedMsgData):
    """Данные результата парсинга Baseapp::onUpdateDataFromClientForControlledEntity."""  # noqa: E501

    entity_id: KBEEntityId
    x: KBEFloat
    y: KBEFloat
    z: KBEFloat
    roll: KBEFloat
    pitch: KBEFloat
    yaw: KBEFloat
    isOnGround: KBEBool  # noqa: N815  # pylint: disable=invalid-name
    spaceID: KBESpaceId  # noqa: N815  # pylint: disable=invalid-name


@dataclass(frozen=True)
class OnUpdateDataFromClientForControlledEntityMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::onUpdateDataFromClientForControlledEntity."""  # noqa: E501

    success: bool
    result: OnUpdateDataFromClientForControlledEntityParsedMsgData
    msg_id: int = msgspec.baseapp.onUpdateDataFromClientForControlledEntity.id
    text: str = ""


class OnUpdateDataFromClientForControlledEntityMsgParser(IMsgParser):
    """Парсер для Baseapp::onUpdateDataFromClientForControlledEntity."""

    def parse(
        self, msg: Message
    ) -> OnUpdateDataFromClientForControlledEntityMsgParserResult:
        """Распарсить сообщение Baseapp::onUpdateDataFromClientForControlledEntity.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnUpdateDataFromClientForControlledEntityMsgParserResult: объект
                результата обработки

        """  # noqa: E501
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnUpdateDataFromClientForControlledEntityParsedMsgData(*values)
        return OnUpdateDataFromClientForControlledEntityMsgParserResult(
            success=True, result=pd
        )


@dataclass(frozen=True)
class LookAppMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::lookApp."""

    success: bool
    result: ParsedMsgData
    msg_id: int = msgspec.baseapp.lookApp.id
    text: str = ""


class LookAppMsgParser(IMsgParser):
    """Парсер для Baseapp::lookApp."""

    def parse(self, msg: Message) -> LookAppMsgParserResult:  # noqa: ARG002
        """Распарсить сообщение Baseapp::lookApp.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            LookAppMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        return LookAppMsgParserResult(success=True, result=ParsedMsgData())


@dataclass(frozen=True)
class QueryLoadMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::queryLoad."""

    success: bool
    result: ParsedMsgData
    msg_id: int = msgspec.baseapp.queryLoad.id
    text: str = ""


class QueryLoadMsgParser(IMsgParser):
    """Парсер для Baseapp::queryLoad."""

    def parse(self, msg: Message) -> QueryLoadMsgParserResult:  # noqa: ARG002
        """Распарсить сообщение Baseapp::queryLoad.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            QueryLoadMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        return QueryLoadMsgParserResult(success=True, result=ParsedMsgData())


@dataclass
class OnExecScriptCommandParsedMsgData(ParsedMsgData):
    """Данные результата парсинга Baseapp::onExecScriptCommand."""

    command: KBEString


@dataclass(frozen=True)
class OnExecScriptCommandMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::onExecScriptCommand."""

    success: bool
    result: OnExecScriptCommandParsedMsgData
    msg_id: int = msgspec.baseapp.onExecScriptCommand.id
    text: str = ""


class OnExecScriptCommandMsgParser(IMsgParser):
    """Парсер для Baseapp::onExecScriptCommand."""

    def parse(self, msg: Message) -> OnExecScriptCommandMsgParserResult:
        """Распарсить сообщение Baseapp::onExecScriptCommand.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnExecScriptCommandMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnExecScriptCommandParsedMsgData(*values)
        return OnExecScriptCommandMsgParserResult(success=True, result=pd)


@dataclass
class OnReqAllocEntityIDParsedMsgData(ParsedMsgData):
    """Данные результата парсинга Baseapp::onReqAllocEntityID."""

    count: KBEUInt32


@dataclass(frozen=True)
class OnReqAllocEntityIDMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::onReqAllocEntityID."""

    success: bool
    result: OnReqAllocEntityIDParsedMsgData
    msg_id: int = msgspec.baseapp.onReqAllocEntityID.id
    text: str = ""


class OnReqAllocEntityIDMsgParser(IMsgParser):
    """Парсер для Baseapp::onReqAllocEntityID."""

    def parse(self, msg: Message) -> OnReqAllocEntityIDMsgParserResult:
        """Распарсить сообщение Baseapp::onReqAllocEntityID.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnReqAllocEntityIDMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnReqAllocEntityIDParsedMsgData(*values)
        return OnReqAllocEntityIDMsgParserResult(success=True, result=pd)


@dataclass
class OnBroadcastBaseAppDataChangedParsedMsgData(ParsedMsgData):
    """Данные результата парсинга Baseapp::onBroadcastBaseAppDataChanged."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnBroadcastBaseAppDataChangedMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::onBroadcastBaseAppDataChanged."""

    success: bool
    result: OnBroadcastBaseAppDataChangedParsedMsgData
    msg_id: int = msgspec.baseapp.onBroadcastBaseAppDataChanged.id
    text: str = ""


class OnBroadcastBaseAppDataChangedMsgParser(IMsgParser):
    """Парсер для Baseapp::onBroadcastBaseAppDataChanged."""

    def parse(
        self, msg: Message
    ) -> OnBroadcastBaseAppDataChangedMsgParserResult:
        """Распарсить сообщение Baseapp::onBroadcastBaseAppDataChanged.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnBroadcastBaseAppDataChangedMsgParserResult: объект результата
                обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnBroadcastBaseAppDataChangedParsedMsgData(values[0])
        return OnBroadcastBaseAppDataChangedMsgParserResult(
            success=True, result=pd
        )


@dataclass
class OnCreateEntityAnywhereCallbackParsedMsgData(ParsedMsgData):
    """Данные результата парсинга Baseapp::onCreateEntityAnywhereCallback."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnCreateEntityAnywhereCallbackMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::onCreateEntityAnywhereCallback."""

    success: bool
    result: OnCreateEntityAnywhereCallbackParsedMsgData
    msg_id: int = msgspec.baseapp.onCreateEntityAnywhereCallback.id
    text: str = ""


class OnCreateEntityAnywhereCallbackMsgParser(IMsgParser):
    """Парсер для Baseapp::onCreateEntityAnywhereCallback."""

    def parse(
        self, msg: Message
    ) -> OnCreateEntityAnywhereCallbackMsgParserResult:
        """Распарсить сообщение Baseapp::onCreateEntityAnywhereCallback.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnCreateEntityAnywhereCallbackMsgParserResult: объект результата
                обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnCreateEntityAnywhereCallbackParsedMsgData(values[0])
        return OnCreateEntityAnywhereCallbackMsgParserResult(
            success=True, result=pd
        )


@dataclass
class OnCreateEntityRemotelyParsedMsgData(ParsedMsgData):
    """Данные результата парсинга Baseapp::onCreateEntityRemotely."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnCreateEntityRemotelyMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::onCreateEntityRemotely."""

    success: bool
    result: OnCreateEntityRemotelyParsedMsgData
    msg_id: int = msgspec.baseapp.onCreateEntityRemotely.id
    text: str = ""


class OnCreateEntityRemotelyMsgParser(IMsgParser):
    """Парсер для Baseapp::onCreateEntityRemotely."""

    def parse(self, msg: Message) -> OnCreateEntityRemotelyMsgParserResult:
        """Распарсить сообщение Baseapp::onCreateEntityRemotely.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnCreateEntityRemotelyMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnCreateEntityRemotelyParsedMsgData(values[0])
        return OnCreateEntityRemotelyMsgParserResult(success=True, result=pd)


@dataclass
class OnCreateEntityRemotelyCallbackParsedMsgData(ParsedMsgData):
    """Данные результата парсинга Baseapp::onCreateEntityRemotelyCallback."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnCreateEntityRemotelyCallbackMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::onCreateEntityRemotelyCallback."""

    success: bool
    result: OnCreateEntityRemotelyCallbackParsedMsgData
    msg_id: int = msgspec.baseapp.onCreateEntityRemotelyCallback.id
    text: str = ""


class OnCreateEntityRemotelyCallbackMsgParser(IMsgParser):
    """Парсер для Baseapp::onCreateEntityRemotelyCallback."""

    def parse(
        self, msg: Message
    ) -> OnCreateEntityRemotelyCallbackMsgParserResult:
        """Распарсить сообщение Baseapp::onCreateEntityRemotelyCallback.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnCreateEntityRemotelyCallbackMsgParserResult: объект результата
                обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnCreateEntityRemotelyCallbackParsedMsgData(values[0])
        return OnCreateEntityRemotelyCallbackMsgParserResult(
            success=True, result=pd
        )


@dataclass
class OnCreateCellFailureParsedMsgData(ParsedMsgData):
    """Данные результата парсинга Baseapp::onCreateCellFailure."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnCreateCellFailureMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::onCreateCellFailure."""

    success: bool
    result: OnCreateCellFailureParsedMsgData
    msg_id: int = msgspec.baseapp.onCreateCellFailure.id
    text: str = ""


class OnCreateCellFailureMsgParser(IMsgParser):
    """Парсер для Baseapp::onCreateCellFailure."""

    def parse(self, msg: Message) -> OnCreateCellFailureMsgParserResult:
        """Распарсить сообщение Baseapp::onCreateCellFailure.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnCreateCellFailureMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnCreateCellFailureParsedMsgData(values[0])
        return OnCreateCellFailureMsgParserResult(success=True, result=pd)


@dataclass
class OnQueryAccountCBFromDbmgrParsedMsgData(ParsedMsgData):
    """Данные результата парсинга Baseapp::onQueryAccountCBFromDbmgr."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnQueryAccountCBFromDbmgrMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::onQueryAccountCBFromDbmgr."""

    success: bool
    result: OnQueryAccountCBFromDbmgrParsedMsgData
    msg_id: int = msgspec.baseapp.onQueryAccountCBFromDbmgr.id
    text: str = ""


class OnQueryAccountCBFromDbmgrMsgParser(IMsgParser):
    """Парсер для Baseapp::onQueryAccountCBFromDbmgr."""

    def parse(self, msg: Message) -> OnQueryAccountCBFromDbmgrMsgParserResult:
        """Распарсить сообщение Baseapp::onQueryAccountCBFromDbmgr.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnQueryAccountCBFromDbmgrMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnQueryAccountCBFromDbmgrParsedMsgData(values[0])
        return OnQueryAccountCBFromDbmgrMsgParserResult(success=True, result=pd)


@dataclass
class OnEntityCallParsedMsgData(ParsedMsgData):
    """Данные результата парсинга Baseapp::onEntityCall."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnEntityCallMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::onEntityCall."""

    success: bool
    result: OnEntityCallParsedMsgData
    msg_id: int = msgspec.baseapp.onEntityCall.id
    text: str = ""


class OnEntityCallMsgParser(IMsgParser):
    """Парсер для Baseapp::onEntityCall."""

    def parse(self, msg: Message) -> OnEntityCallMsgParserResult:
        """Распарсить сообщение Baseapp::onEntityCall.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnEntityCallMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnEntityCallParsedMsgData(values[0])
        return OnEntityCallMsgParserResult(success=True, result=pd)


@dataclass
class OnRemoteCallCellMethodFromClientParsedMsgData(ParsedMsgData):
    """Данные результата парсинга Baseapp::onRemoteCallCellMethodFromClient."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnRemoteCallCellMethodFromClientMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::onRemoteCallCellMethodFromClient."""

    success: bool
    result: OnRemoteCallCellMethodFromClientParsedMsgData
    msg_id: int = msgspec.baseapp.onRemoteCallCellMethodFromClient.id
    text: str = ""


class OnRemoteCallCellMethodFromClientMsgParser(IMsgParser):
    """Парсер для Baseapp::onRemoteCallCellMethodFromClient."""

    def parse(
        self, msg: Message
    ) -> OnRemoteCallCellMethodFromClientMsgParserResult:
        """Распарсить сообщение Baseapp::onRemoteCallCellMethodFromClient.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnRemoteCallCellMethodFromClientMsgParserResult: объект результата
                обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnRemoteCallCellMethodFromClientParsedMsgData(values[0])
        return OnRemoteCallCellMethodFromClientMsgParserResult(
            success=True, result=pd
        )


@dataclass(frozen=True)
class OnClientActiveTickMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::onClientActiveTick."""

    success: bool
    result: ParsedMsgData
    msg_id: int = msgspec.baseapp.onClientActiveTick.id
    text: str = ""


class OnClientActiveTickMsgParser(IMsgParser):
    """Парсер для Baseapp::onClientActiveTick."""

    def parse(self, msg: Message) -> OnClientActiveTickMsgParserResult:
        """Распарсить сообщение Baseapp::onClientActiveTick.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnClientActiveTickMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        return OnClientActiveTickMsgParserResult(
            success=True, result=ParsedMsgData()
        )


@dataclass
class LoginBaseappParsedMsgData(ParsedMsgData):
    """Данные результата парсинга Baseapp::loginBaseapp."""

    account_name: KBEString
    password: KBEString


@dataclass(frozen=True)
class LoginBaseappMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::loginBaseapp."""

    success: bool
    result: LoginBaseappParsedMsgData
    msg_id: int = msgspec.baseapp.loginBaseapp.id
    text: str = ""


class LoginBaseappMsgParser(IMsgParser):
    """Парсер для Baseapp::loginBaseapp."""

    def parse(self, msg: Message) -> LoginBaseappMsgParserResult:
        """Распарсить сообщение Baseapp::loginBaseapp.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            LoginBaseappMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = LoginBaseappParsedMsgData(*values)
        return LoginBaseappMsgParserResult(success=True, result=pd)


@dataclass
class ReloginBaseappParsedMsgData(ParsedMsgData):
    """Данные результата парсинга Baseapp::reloginBaseapp."""

    account_name: KBEString
    password: KBEString
    key: KBEUInt64
    entity_id: KBEEntityId


@dataclass(frozen=True)
class ReloginBaseappMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::reloginBaseapp."""

    success: bool
    result: ReloginBaseappParsedMsgData
    msg_id: int = msgspec.baseapp.reloginBaseapp.id
    text: str = ""


class ReloginBaseappMsgParser(IMsgParser):
    """Парсер для Baseapp::reloginBaseapp."""

    def parse(self, msg: Message) -> ReloginBaseappMsgParserResult:
        """Распарсить сообщение Baseapp::reloginBaseapp.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            ReloginBaseappMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = ReloginBaseappParsedMsgData(*values)
        return ReloginBaseappMsgParserResult(success=True, result=pd)


@dataclass
class LogoutBaseappParsedMsgData(ParsedMsgData):
    """Данные результата парсинга Baseapp::logoutBaseapp."""

    key: KBEUInt64
    entity_id: KBEEntityId


@dataclass(frozen=True)
class LogoutBaseappMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::logoutBaseapp."""

    success: bool
    result: LogoutBaseappParsedMsgData
    msg_id: int = msgspec.baseapp.logoutBaseapp.id
    text: str = ""


class LogoutBaseappMsgParser(IMsgParser):
    """Парсер для Baseapp::logoutBaseapp."""

    def parse(self, msg: Message) -> LogoutBaseappMsgParserResult:
        """Распарсить сообщение Baseapp::logoutBaseapp.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            LogoutBaseappMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = LogoutBaseappParsedMsgData(*values)
        return LogoutBaseappMsgParserResult(success=True, result=pd)


@dataclass
class ReqAccountBindEmailParsedMsgData(ParsedMsgData):
    """Данные результата парсинга Baseapp::reqAccountBindEmail."""

    entity_id: KBEEntityId
    password: KBEString
    email: KBEString


@dataclass(frozen=True)
class ReqAccountBindEmailMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::reqAccountBindEmail."""

    success: bool
    result: ReqAccountBindEmailParsedMsgData
    msg_id: int = msgspec.baseapp.reqAccountBindEmail.id
    text: str = ""


class ReqAccountBindEmailMsgParser(IMsgParser):
    """Парсер для Baseapp::reqAccountBindEmail."""

    def parse(self, msg: Message) -> ReqAccountBindEmailMsgParserResult:
        """Распарсить сообщение Baseapp::reqAccountBindEmail.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            ReqAccountBindEmailMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = ReqAccountBindEmailParsedMsgData(*values)
        return ReqAccountBindEmailMsgParserResult(success=True, result=pd)


@dataclass
class ReqAccountNewPasswordParsedMsgData(ParsedMsgData):
    """Данные результата парсинга Baseapp::reqAccountNewPassword."""

    entity_id: KBEEntityId
    oldpassword: KBEString
    newpassword: KBEString


@dataclass(frozen=True)
class ReqAccountNewPasswordMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::reqAccountNewPassword."""

    success: bool
    result: ReqAccountNewPasswordParsedMsgData
    msg_id: int = msgspec.baseapp.reqAccountNewPassword.id
    text: str = ""


class ReqAccountNewPasswordMsgParser(IMsgParser):
    """Парсер для Baseapp::reqAccountNewPassword."""

    def parse(self, msg: Message) -> ReqAccountNewPasswordMsgParserResult:
        """Распарсить сообщение Baseapp::reqAccountNewPassword.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            ReqAccountNewPasswordMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = ReqAccountNewPasswordParsedMsgData(*values)
        return ReqAccountNewPasswordMsgParserResult(success=True, result=pd)


@dataclass
class OnLookAppParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Baseapp::onLookApp."""

    componentType: KBEComponentType  # noqa: N815
    componentId: KBEComponentId  # noqa: N815
    shutdownState: KBEInt8  # noqa: N815
    entitiesSize: KBEUInt32  # noqa: N815
    numClients: KBEInt32  # noqa: N815
    numProxices: KBEInt32  # noqa: N815
    port: KBEUInt32

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
class OnLookAppMsgParserResult(MsgParserResult):
    """Парсер для Baseapp::onLookApp."""

    success: bool
    result: OnLookAppParsedMsgData
    msg_id: int = msgspec.baseapp.onLookApp.id
    text: str = ""


class OnLookAppMsgParser(IMsgParser):
    """Парсер для Baseapp::onLookApp."""

    def parse(self, msg: Message) -> OnLookAppMsgParserResult:
        """Распарсить сообщение Baseapp::onLookApp.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnLookAppParserMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnLookAppParsedMsgData(*values)
        return OnLookAppMsgParserResult(success=True, result=pd)


@dataclass
class OnBackupEntityCellDataParsedMsgData(ParsedMsgData):
    """Данные результата парсинга Baseapp::onBackupEntityCellData."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnBackupEntityCellDataMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::onBackupEntityCellData."""

    success: bool
    result: OnBackupEntityCellDataParsedMsgData
    msg_id: int = msgspec.baseapp.onBackupEntityCellData.id
    text: str = ""


class OnBackupEntityCellDataMsgParser(IMsgParser):
    """Парсер для Baseapp::onBackupEntityCellData."""

    def parse(self, msg: Message) -> OnBackupEntityCellDataMsgParserResult:
        """Распарсить сообщение Baseapp::onBackupEntityCellData.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnBackupEntityCellDataMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()

        data = KBERowByteData(values[0])
        pd = OnBackupEntityCellDataParsedMsgData(data)

        return OnBackupEntityCellDataMsgParserResult(success=True, result=pd)


@dataclass
class OnWriteToDBCallbackParsedMsgData(ParsedMsgData):
    """Данные результата парсинга Baseapp::onWriteToDBCallback.

    Args:
        entity_id: ID сущности в памяти.
        entityDBID: ID сущности в базе данных.
        dbInterfaceIndex: Индекс интерфейса БД.
        callbackID: ID callback для сопоставления.
        success: Успешность операции записи.

    """

    entity_id: KBEEntityId
    entityDBID: KBEDbid  # noqa: N815  # pylint: disable=invalid-name
    dbInterfaceIndex: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name
    callbackID: KBECallbackId  # noqa: N815  # pylint: disable=invalid-name
    success_int: KBEBool

    @property
    def success(self) -> bool:
        return bool(self.success_int)

    __add_to_dict__: ClassVar[tuple[str, ...]] = ("success",)


@dataclass(frozen=True)
class OnWriteToDBCallbackMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Baseapp::onWriteToDBCallback.

    Args:
        success: Успешность обработки сообщения.
        result: Результат парсинга.
        msg_id: ID сообщения.
        text: Текст результата.

    """

    success: bool
    result: OnWriteToDBCallbackParsedMsgData | None
    msg_id: int = msgspec.baseapp.onWriteToDBCallback.id
    text: str = ""


class OnWriteToDBCallbackMsgParser(IMsgParser):
    """Парсер для Baseapp::onWriteToDBCallback."""

    def parse(self, msg: Message) -> OnWriteToDBCallbackMsgParserResult:
        """Обработать сообщение Baseapp::onWriteToDBCallback.

        Args:
            msg: KBEngine-сообщение.

        Returns:
            OnWriteToDBCallbackMsgParserResult: объект результата обработки.

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnWriteToDBCallbackParsedMsgData(*values)
        return OnWriteToDBCallbackMsgParserResult(success=True, result=pd)


@dataclass
class OnRemoteMethodCallParsedMsgData(ParsedMsgData):
    """Данные результата парсинга Entity::onRemoteMethodCall."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnRemoteMethodCallMsgParserResult(MsgParserResult):
    """Результат парсера сообщения Entity::onRemoteMethodCall."""

    success: bool
    result: OnRemoteMethodCallParsedMsgData
    msg_id: int = msgspec.baseapp.onRemoteMethodCall.id
    text: str = ""


class OnRemoteMethodCallMsgParser(IMsgParser):
    """Парсер для Entity::onRemoteMethodCall."""

    def parse(self, msg: Message) -> OnRemoteMethodCallMsgParserResult:
        """Распарсить сообщение Entity::onRemoteMethodCall.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnRemoteMethodCallMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnRemoteMethodCallParsedMsgData(values[0])
        return OnRemoteMethodCallMsgParserResult(success=True, result=pd)
