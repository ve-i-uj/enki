"""Обработчик сообщений от компонента Baseapp."""

from __future__ import annotations

import logging
import pickle
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar

from enki import msgspec
from enki.core.kbepickle.kbepickle import pickle_global_data_value
from enki.kbeenum import ClientType
from enki.kbetype.decoders.basic_data_type_decoders import (
    BLOB,
    BOOL,
    INT32,
    UINT16,
)
from enki.kbetype.decoders.custom_decoders import (
    DBID,
    ENTITY_SCRIPT_UID,
    KBEDdid,
    KBEEntityId,
)
from enki.kbetype.pytypes.basic_data_types import (
    KBEInt32,
    KBEString,
    KBEUInt32,
    KBEUInt64,
)
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
    from enki.kbetype.pytypes.basic_data_types import KBEBool
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

    dbInterfaceIndex: int  # noqa: N815  # pylint: disable=invalid-name
    size: int
    entityType: int  # noqa: N815  # pylint: disable=invalid-name
    dbids: list[int]


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
            OnEntityAutoLoadCBFromDBMgrMsgParserResult: объект результата обработки.

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
        dbids: list[int] = []
        for _ in range(size):
            dbid, offset = DBID.decode(data)
            data = data[offset:]
            dbids.append(dbid)

        pd = OnEntityAutoLoadCBFromDBMgrParsedMsgData(
            dbInterfaceIndex, size, entityType, dbids
        )
        return OnEntityAutoLoadCBFromDBMgrMsgParserResult(success=True, result=pd)


@dataclass
class OnBroadcastGlobalDataChangedParsedMsgData(ParsedMsgData):
    """Данные результата парсинга Baseapp::onBroadcastGlobalDataChanged.

    Args:
        isDelete: Флаг удаления.
        key: Ключ данных.
        value: Значение данных.

    """

    isDelete: KBEBool  # noqa: N815  # pylint: disable=invalid-name
    key: str
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

    def parse(self, msg: Message) -> OnBroadcastGlobalDataChangedMsgParserResult:
        """Обработать сообщение Baseapp::onBroadcastGlobalDataChanged.

        Args:
            msg: KBEngine-сообщение.

        Returns:
            OnBroadcastGlobalDataChangedMsgParserResult: объект результата обработки.

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

    entity_id: int
    componentID: int  # noqa: N815  # pylint: disable=invalid-name
    spaceID: int  # noqa: N815  # pylint: disable=invalid-name


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
    entityDBID: KBEDdid  # noqa: N815  # pylint: disable=invalid-name
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
