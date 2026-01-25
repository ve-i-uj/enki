"""Парсер сообщений от компонента DBMgr."""

import logging
import pickle
from dataclasses import dataclass
from typing import Any, ClassVar

from enki import msgspec
from enki.core import kbemath
from enki.core.kbepickle.kbepickle import pickle_global_data_value
from enki.kbeenum import (
    COMPONENT_STATE_BY_SHUTDOWN_STATE,
    ComponentState,
    ComponentType,
    GlobalDataTypeEnum,
    ServerError,
    ShutdownState,
)
from enki.kbetype.decoders.basic_data_type_decoders import BLOB, BOOL, UINT8
from enki.kbetype.decoders.custom_decoders import (
    COMPONENT_TYPE,
    KBEComponentId,
    KBEComponentType,
    KBEEntityId,
)
from enki.kbetype.pytypes.basic_data_types import (
    KBEBlob,
    KBEBool,
    KBEInt8,
    KBEInt32,
    KBERowByteData,
    KBEString,
    KBEUInt8,
    KBEUInt16,
    KBEUInt32,
    KBEUInt64,
)
from enki.misc import devonly
from enki.msg.message import Message
from enki.net.addr import Addr, Port

from .common import (
    OnAppActiveTickParsedMsgData,
    OnRegisterNewAppParsedMsgData,
    ReqCloseServerParsedMsgData,
)
from .imsg_parser import IMsgParser, MsgParserResult, ParsedMsgData

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OnRegisterNewAppMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::onRegisterNewApp.

    :param success: Флаг успешного выполнения
    :param result: Результат парсинга
    :param msg_id: ID сообщения
    :param text: Текст сообщения

    """

    success: bool
    result: OnRegisterNewAppParsedMsgData
    msg_id: int = msgspec.dbmgr.onRegisterNewApp.id
    text: str = ""


class OnRegisterNewAppMsgParser(IMsgParser):
    """Парсер для DBMgr::onRegisterNewApp."""

    def parse(self, msg: Message) -> OnRegisterNewAppMsgParserResult:
        """Парсинг сообщения DBMgr::onRegisterNewApp.

        :param msg: Сообщение для парсинга
        :return: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnRegisterNewAppParsedMsgData(*values)
        return OnRegisterNewAppMsgParserResult(success=True, result=pd)


@dataclass(frozen=True)
class OnAppActiveTickMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::onAppActiveTick.

    :param success: Флаг успешного выполнения
    :param result: Результат парсинга
    :param msg_id: ID сообщения
    :param text: Текст сообщения

    """

    success: bool
    result: OnAppActiveTickParsedMsgData
    msg_id: int = msgspec.dbmgr.onAppActiveTick.id
    text: str = ""


class OnAppActiveTickMsgParser(IMsgParser):
    """Парсер для DBMgr::onAppActiveTick."""

    def parse(self, msg: Message) -> OnAppActiveTickMsgParserResult:
        """Парсинг сообщения DBMgr::onAppActiveTick.

        :param msg: Сообщение для парсинга
        :return: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnAppActiveTickParsedMsgData(*values)
        return OnAppActiveTickMsgParserResult(success=True, result=pd)


@dataclass
class OnBroadcastGlobalDataChangedParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::onBroadcastGlobalDataChanged.

    :param dataType: Тип данных
    :param isDelete: Флаг удаления
    :param key: Ключ данных
    :param value: Значение данных
    :param component_type: Тип компонента

    """

    dataType: KBEUInt8  # noqa: N815  # pylint: disable=invalid-name
    isDelete: KBEBool  # noqa: N815  # pylint: disable=invalid-name
    key: KBEString
    value: Any
    componentType: KBEComponentType  # pylint: disable=invalid-name

    @property
    def global_data_type(self) -> GlobalDataTypeEnum:
        """Тип глобальных данных."""
        return GlobalDataTypeEnum(self.dataType)

    @property
    def component_type(self) -> ComponentType:
        """Энам типа компонента.

        Returns:
            ComponentType: энам типа компонента

        """
        return ComponentType(self.componentType)

    __add_to_dict__: ClassVar = (
        "global_data_type",
        "component_type",
    )


@dataclass(frozen=True)
class OnBroadcastGlobalDataChangedMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::onBroadcastGlobalDataChanged.

    :param success: Флаг успешного выполнения
    :param result: Результат парсинга
    :param msg_id: ID сообщения
    :param text: Текст сообщения

    """

    success: bool
    result: OnBroadcastGlobalDataChangedParsedMsgData
    msg_id: int = msgspec.dbmgr.onBroadcastGlobalDataChanged.id
    text: str = ""


class OnBroadcastGlobalDataChangedMsgParser(IMsgParser):
    """Парсер для DBMgr::onBroadcastGlobalDataChanged."""

    def parse(
        self, msg: Message
    ) -> OnBroadcastGlobalDataChangedMsgParserResult:
        """Парсинг сообщения DBMgr::onBroadcastGlobalDataChanged.

        :param msg: Сообщение для парсинга
        :return: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])
        dataType, offset = UINT8.decode(data)  # pylint: disable=invalid-name
        data = data[offset:]
        is_delete, offset = BOOL.decode(data)
        data = data[offset:]
        key_data, offset = BLOB.decode(data)
        data = data[offset:]

        key = pickle.loads(key_data)  # noqa: S301

        if is_delete:
            value = None
        else:
            value_data, offset = BLOB.decode(data)
            data = data[offset:]
            value = pickle_global_data_value(value_data)

        component_type, offset = COMPONENT_TYPE.decode(data)
        data = data[offset:]

        pd = OnBroadcastGlobalDataChangedParsedMsgData(
            dataType, is_delete, key, value, component_type
        )

        assert not data
        return OnBroadcastGlobalDataChangedMsgParserResult(
            success=True, result=pd
        )


@dataclass
class SyncEntityStreamTemplateParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::syncEntityStreamTemplate.

    :param data: Данные шаблона потока сущностей

    """

    data: KBERowByteData


@dataclass(frozen=True)
class SyncEntityStreamTemplateMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::syncEntityStreamTemplate.

    :param success: Флаг успешного выполнения
    :param result: Результат парсинга
    :param msg_id: ID сообщения
    :param text: Текст сообщения

    """

    success: bool
    result: SyncEntityStreamTemplateParsedMsgData
    msg_id: int = msgspec.dbmgr.syncEntityStreamTemplate.id
    text: str = ""


class SyncEntityStreamTemplateMsgParser(IMsgParser):
    """Парсер сообщения DBMgr::syncEntityStreamTemplate.

    Довольно сложная логика заполнения данных, основанная на описание сущности
    (т.е. нужно иметь ссылку на assets'ы и в по ним заполнять данные).

    Поэтому пока просто возвращает байты без парсинга.
    см. bool SyncEntityStreamTemplateHandler::process()
    """

    def parse(self, msg: Message) -> SyncEntityStreamTemplateMsgParserResult:
        """Парсинг сообщения DBMgr::syncEntityStreamTemplate.

        :param msg: Сообщение для парсинга
        :return: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        memoryview(values[0])
        pd = SyncEntityStreamTemplateParsedMsgData(*values)

        return SyncEntityStreamTemplateMsgParserResult(success=True, result=pd)


@dataclass
class EntityAutoLoadParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::entityAutoLoad.

    :param dbInterfaceIndex: Индекс интерфейса БД
    :param componentID: ID компонента
    :param entityType: Тип сущности
    :param start: Начало диапазона
    :param end: Конец диапазона

    """

    dbInterfaceIndex: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name
    componentID: KBEComponentId  # noqa: N815  # pylint: disable=invalid-name
    entityType: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name
    start: KBEEntityId
    end: KBEEntityId


@dataclass(frozen=True)
class EntityAutoLoadMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::entityAutoLoad.

    :param success: Флаг успешного выполнения
    :param result: Результат парсинга
    :param msg_id: ID сообщения
    :param text: Текст сообщения

    """

    success: bool
    result: EntityAutoLoadParsedMsgData
    msg_id: int = msgspec.dbmgr.entityAutoLoad.id
    text: str = ""


class EntityAutoLoadMsgParser(IMsgParser):
    """Парсер для DBMgr::entityAutoLoad."""

    def parse(self, msg: Message) -> EntityAutoLoadMsgParserResult:
        """Парсинг сообщения DBMgr::entityAutoLoad.

        :param msg: Сообщение для парсинга
        :return: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = EntityAutoLoadParsedMsgData(*values)
        return EntityAutoLoadMsgParserResult(success=True, result=pd)


@dataclass
class OnAccountLoginParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::onAccountLogin."""

    login: KBEString
    password: KBEString
    data: KBEBlob


@dataclass(frozen=True)
class OnAccountLoginMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::onAccountLogin."""

    success: bool
    result: OnAccountLoginParsedMsgData
    msg_id: int = msgspec.dbmgr.onAccountLogin.id
    text: str = ""


class OnAccountLoginMsgParser(IMsgParser):
    """Парсер для DBMgr::onAccountLogin."""

    def parse(self, msg: Message) -> OnAccountLoginMsgParserResult:
        """Парсинг сообщения DBMgr::onAccountLogin.

        :param msg: Сообщение для парсинга
        :return: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnAccountLoginParsedMsgData(*values)
        return OnAccountLoginMsgParserResult(success=True, result=pd)


@dataclass
class OnLoginAccountCBBFromInterfacesParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::onLoginAccountCBBFromInterfaces."""

    component_id: KBEComponentId
    login: KBEString
    account_name: KBEString
    password: KBEString
    retCode: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name
    postdatas: KBEBlob
    getdatas: KBEBlob

    @property
    def ret_code(self) -> ServerError:
        """Возвращает код ошибки в виде enum ServerError.

        Returns:
            ServerError: Код ошибки

        """
        return ServerError(self.retCode)

    __add_to_dict__: ClassVar = ("ret_code",)


@dataclass(frozen=True)
class OnLoginAccountCBBFromInterfacesMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::onLoginAccountCBBFromInterfaces."""

    success: bool
    result: OnLoginAccountCBBFromInterfacesParsedMsgData
    msg_id: int = msgspec.dbmgr.onLoginAccountCBBFromInterfaces.id
    text: str = ""


class OnLoginAccountCBBFromInterfacesMsgParser(IMsgParser):
    """Парсер для DBMgr::onLoginAccountCBBFromInterfaces."""

    def parse(
        self, msg: Message
    ) -> OnLoginAccountCBBFromInterfacesMsgParserResult:
        """Парсинг сообщения DBMgr::onLoginAccountCBBFromInterfaces.

        :param msg: Сообщение для парсинга
        :return: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnLoginAccountCBBFromInterfacesParsedMsgData(*values)
        return OnLoginAccountCBBFromInterfacesMsgParserResult(
            success=True, result=pd
        )


@dataclass(frozen=True)
class LookAppMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::lookApp."""

    success: bool
    result: ParsedMsgData
    msg_id: int = msgspec.dbmgr.lookApp.id
    text: str = ""


class LookAppMsgParser(IMsgParser):
    """Парсер для DBMgr::lookApp."""

    def parse(self, msg: Message) -> LookAppMsgParserResult:  # noqa: ARG002
        """Парсинг сообщения DBMgr::lookApp."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        return LookAppMsgParserResult(success=True, result=ParsedMsgData())


@dataclass(frozen=True)
class QueryLoadMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::queryLoad."""

    success: bool
    result: ParsedMsgData
    msg_id: int = msgspec.dbmgr.queryLoad.id
    text: str = ""


class QueryLoadMsgParser(IMsgParser):
    """Парсер для DBMgr::queryLoad."""

    def parse(self, msg: Message) -> QueryLoadMsgParserResult:  # noqa: ARG002
        """Парсинг сообщения DBMgr::queryLoad."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        return QueryLoadMsgParserResult(success=True, result=ParsedMsgData())


@dataclass
class OnReqAllocEntityIDParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::onReqAllocEntityID."""

    componentType: KBEUInt8  # noqa: N815  # pylint: disable=invalid-name
    componentID: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name

    @property
    def component_type(self) -> ComponentType:
        """Тип компонента."""
        return ComponentType(self.componentType)

    __add_to_dict__: ClassVar = ("component_type",)


@dataclass(frozen=True)
class OnReqAllocEntityIDMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::onReqAllocEntityID."""

    success: bool
    result: OnReqAllocEntityIDParsedMsgData
    msg_id: int = msgspec.dbmgr.onReqAllocEntityID.id
    text: str = ""


class OnReqAllocEntityIDMsgParser(IMsgParser):
    """Парсер для DBMgr::onReqAllocEntityID."""

    def parse(self, msg: Message) -> OnReqAllocEntityIDMsgParserResult:
        """Парсинг сообщения DBMgr::onReqAllocEntityID."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnReqAllocEntityIDParsedMsgData(*values)
        return OnReqAllocEntityIDMsgParserResult(success=True, result=pd)


@dataclass
class ReqCreateAccountParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::reqCreateAccount."""

    accountName: KBEString  # noqa: N815  # pylint: disable=invalid-name
    password: KBEString
    datas: KBEBlob


@dataclass(frozen=True)
class ReqCreateAccountMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::reqCreateAccount."""

    success: bool
    result: ReqCreateAccountParsedMsgData
    msg_id: int = msgspec.dbmgr.reqCreateAccount.id
    text: str = ""


class ReqCreateAccountMsgParser(IMsgParser):
    """Парсер для DBMgr::reqCreateAccount."""

    def parse(self, msg: Message) -> ReqCreateAccountMsgParserResult:
        """Парсинг сообщения DBMgr::reqCreateAccount."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = ReqCreateAccountParsedMsgData(*values)
        return ReqCreateAccountMsgParserResult(success=True, result=pd)


@dataclass
class OnCreateAccountCBFromInterfacesParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::onCreateAccountCBFromInterfaces."""

    component_id: KBEUInt64
    accountName: KBEString  # noqa: N815  # pylint: disable=invalid-name
    password: KBEString
    retcode: KBEUInt16
    datas: KBEBlob

    @property
    def ret_code(self) -> ServerError:
        """Код возврата."""
        return ServerError(self.retcode)

    __add_to_dict__: ClassVar = ("ret_code",)


@dataclass(frozen=True)
class OnCreateAccountCBFromInterfacesMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::onCreateAccountCBFromInterfaces."""

    success: bool
    result: OnCreateAccountCBFromInterfacesParsedMsgData
    msg_id: int = msgspec.dbmgr.onCreateAccountCBFromInterfaces.id
    text: str = ""


class OnCreateAccountCBFromInterfacesMsgParser(IMsgParser):
    """Парсер для DBMgr::onCreateAccountCBFromInterfaces."""

    def parse(
        self, msg: Message
    ) -> OnCreateAccountCBFromInterfacesMsgParserResult:
        """Парсинг сообщения DBMgr::onCreateAccountCBFromInterfaces."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnCreateAccountCBFromInterfacesParsedMsgData(*values)
        return OnCreateAccountCBFromInterfacesMsgParserResult(
            success=True, result=pd
        )


@dataclass
class QueryAccountParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::queryAccount."""

    accountName: KBEString  # noqa: N815  # pylint: disable=invalid-name
    password: KBEString
    needCheckPassword: KBEBool  # noqa: N815  # pylint: disable=invalid-name
    componentID: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name
    entityID: KBEUInt32  # noqa: N815  # pylint: disable=invalid-name
    entityDBID: KBEUInt64  # noqa: N815  # pylint: disable=invalid-name
    ip: KBEUInt32
    port: KBEUInt16


@dataclass(frozen=True)
class QueryAccountMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::queryAccount."""

    success: bool
    result: QueryAccountParsedMsgData
    msg_id: int = msgspec.dbmgr.queryAccount.id
    text: str = ""


class QueryAccountMsgParser(IMsgParser):
    """Парсер для DBMgr::queryAccount."""

    def parse(self, msg: Message) -> QueryAccountMsgParserResult:
        """Парсинг сообщения DBMgr::queryAccount."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = QueryAccountParsedMsgData(*values)
        return QueryAccountMsgParserResult(success=True, result=pd)


@dataclass
class OnAccountOnlineParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::onAccountOnline."""

    account_name: KBEString
    component_id: KBEUInt16
    entity_id: KBEUInt32


@dataclass(frozen=True)
class OnAccountOnlineMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::onAccountOnline."""

    success: bool
    result: OnAccountOnlineParsedMsgData
    msg_id: int = msgspec.dbmgr.onAccountOnline.id
    text: str = ""


class OnAccountOnlineMsgParser(IMsgParser):
    """Парсер для DBMgr::onAccountOnline."""

    def parse(self, msg: Message) -> OnAccountOnlineMsgParserResult:
        """Парсинг сообщения DBMgr::onAccountOnline."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnAccountOnlineParsedMsgData(*values)
        return OnAccountOnlineMsgParserResult(success=True, result=pd)


@dataclass
class OnEntityOfflineParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::onEntityOffline."""

    dbid: KBEUInt64
    sid: KBEUInt16
    dbInterfaceIndex: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name


@dataclass(frozen=True)
class OnEntityOfflineMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::onEntityOffline."""

    success: bool
    result: OnEntityOfflineParsedMsgData
    msg_id: int = msgspec.dbmgr.onEntityOffline.id
    text: str = ""


class OnEntityOfflineMsgParser(IMsgParser):
    """Парсер для DBMgr::onEntityOffline."""

    def parse(self, msg: Message) -> OnEntityOfflineMsgParserResult:
        """Парсинг сообщения DBMgr::onEntityOffline."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnEntityOfflineParsedMsgData(*values)
        return OnEntityOfflineMsgParserResult(success=True, result=pd)


@dataclass
class EraseClientReqParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::eraseClientReq."""

    logkey: KBEString


@dataclass(frozen=True)
class EraseClientReqMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::eraseClientReq."""

    success: bool
    result: EraseClientReqParsedMsgData
    msg_id: int = msgspec.dbmgr.eraseClientReq.id
    text: str = ""


class EraseClientReqMsgParser(IMsgParser):
    """Парсер для DBMgr::eraseClientReq."""

    def parse(self, msg: Message) -> EraseClientReqMsgParserResult:
        """Парсинг сообщения DBMgr::eraseClientReq."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = EraseClientReqParsedMsgData(*values)
        return EraseClientReqMsgParserResult(success=True, result=pd)


@dataclass
class ExecuteRawDatabaseCommandParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::executeRawDatabaseCommand."""

    entity_id: KBEUInt32
    dbInterfaceIndex: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name
    component_id: KBEUInt16
    componentType: KBEUInt8  # noqa: N815  # pylint: disable=invalid-name
    callback_id: KBEUInt32
    row_sql: KBEBlob

    @property
    def component_type_enum(self) -> ComponentType:
        """Тип компонента."""
        return ComponentType(self.componentType)

    __add_to_dict__: ClassVar = ("component_type_enum",)


@dataclass(frozen=True)
class ExecuteRawDatabaseCommandMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::executeRawDatabaseCommand."""

    success: bool
    result: ExecuteRawDatabaseCommandParsedMsgData
    msg_id: int = msgspec.dbmgr.executeRawDatabaseCommand.id
    text: str = ""


class ExecuteRawDatabaseCommandMsgParser(IMsgParser):
    """Парсер для DBMgr::executeRawDatabaseCommand."""

    def parse(self, msg: Message) -> ExecuteRawDatabaseCommandMsgParserResult:
        """Парсинг сообщения DBMgr::executeRawDatabaseCommand."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = ExecuteRawDatabaseCommandParsedMsgData(*values)
        return ExecuteRawDatabaseCommandMsgParserResult(success=True, result=pd)


@dataclass
class WriteEntityParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::writeEntity."""

    componentID: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name
    entity_id: KBEUInt32
    entity_db_id: KBEUInt64
    dbInterfaceIndex: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name
    sid: KBEUInt16
    callback_id: KBEUInt32
    shouldAutoLoad: KBEBool  # noqa: N815  # pylint: disable=invalid-name
    ip: KBEUInt32
    port: KBEUInt16
    data: KBERowByteData

    # [2026-01-25 11:35 burov_alexey@mail.ru]:
    # Тут не то что-то получается
    # '__ip_and_port': Addr(ip_addr='0.0.1.0', port=0)
    @property
    def ip_and_port(self) -> Addr:
        return Addr(kbemath.int2ip(self.ip), Port(kbemath.int2port(self.port)))

    __add_to_dict__: ClassVar = ("ip_and_port",)


@dataclass(frozen=True)
class WriteEntityMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::writeEntity."""

    success: bool
    result: WriteEntityParsedMsgData
    msg_id: int = msgspec.dbmgr.writeEntity.id
    text: str = ""


class WriteEntityMsgParser(IMsgParser):
    """Парсер для DBMgr::writeEntity."""

    def parse(self, msg: Message) -> WriteEntityMsgParserResult:
        """Парсинг сообщения DBMgr::writeEntity."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = WriteEntityParsedMsgData(*values)
        return WriteEntityMsgParserResult(success=True, result=pd)


@dataclass
class RemoveEntityParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::removeEntity."""

    dbInterfaceIndex: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name
    componentID: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name
    entity_id: KBEUInt32
    entity_db_id: KBEUInt64
    sid: KBEUInt16
    data: KBERowByteData


@dataclass(frozen=True)
class RemoveEntityMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::removeEntity."""

    success: bool
    result: RemoveEntityParsedMsgData
    msg_id: int = msgspec.dbmgr.removeEntity.id
    text: str = ""


class RemoveEntityMsgParser(IMsgParser):
    """Парсер для DBMgr::removeEntity."""

    def parse(self, msg: Message) -> RemoveEntityMsgParserResult:
        """Парсинг сообщения DBMgr::removeEntity."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = RemoveEntityParsedMsgData(*values)
        return RemoveEntityMsgParserResult(success=True, result=pd)


@dataclass
class DeleteEntityByDBIDParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::deleteEntityByDBID."""

    dbInterfaceIndex: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name
    componentID: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name
    entity_db_id: KBEUInt64
    callback_id: KBEUInt32
    sid: KBEUInt16


@dataclass(frozen=True)
class DeleteEntityByDBIDMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::deleteEntityByDBID."""

    success: bool
    result: DeleteEntityByDBIDParsedMsgData
    msg_id: int = msgspec.dbmgr.deleteEntityByDBID.id
    text: str = ""


class DeleteEntityByDBIDMsgParser(IMsgParser):
    """Парсер для DBMgr::deleteEntityByDBID."""

    def parse(self, msg: Message) -> DeleteEntityByDBIDMsgParserResult:
        """Парсинг сообщения DBMgr::deleteEntityByDBID."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = DeleteEntityByDBIDParsedMsgData(*values)
        return DeleteEntityByDBIDMsgParserResult(success=True, result=pd)


@dataclass
class LookUpEntityByDBIDParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::lookUpEntityByDBID."""

    dbInterfaceIndex: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name
    componentID: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name
    entity_db_id: KBEUInt64
    callback_id: KBEUInt32
    sid: KBEUInt16


@dataclass(frozen=True)
class LookUpEntityByDBIDMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::lookUpEntityByDBID."""

    success: bool
    result: LookUpEntityByDBIDParsedMsgData
    msg_id: int = msgspec.dbmgr.lookUpEntityByDBID.id
    text: str = ""


class LookUpEntityByDBIDMsgParser(IMsgParser):
    """Парсер для DBMgr::lookUpEntityByDBID."""

    def parse(self, msg: Message) -> LookUpEntityByDBIDMsgParserResult:
        """Парсинг сообщения DBMgr::lookUpEntityByDBID."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = LookUpEntityByDBIDParsedMsgData(*values)
        return LookUpEntityByDBIDMsgParserResult(success=True, result=pd)


@dataclass
class QueryEntityParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::queryEntity."""

    dbInterfaceIndex: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name
    componentID: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name
    queryMode: KBEInt8  # noqa: N815  # pylint: disable=invalid-name
    entity_db_id: KBEUInt64
    entityType: KBEString  # noqa: N815  # pylint: disable=invalid-name
    callback_id: KBEUInt32
    entity_id: KBEUInt32


@dataclass(frozen=True)
class QueryEntityMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::queryEntity."""

    success: bool
    result: QueryEntityParsedMsgData
    msg_id: int = msgspec.dbmgr.queryEntity.id
    text: str = ""


class QueryEntityMsgParser(IMsgParser):
    """Парсер для DBMgr::queryEntity."""

    def parse(self, msg: Message) -> QueryEntityMsgParserResult:
        """Парсинг сообщения DBMgr::queryEntity."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = QueryEntityParsedMsgData(*values)
        return QueryEntityMsgParserResult(success=True, result=pd)


@dataclass
class ChargeParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::charge."""

    chargeID: KBEString  # noqa: N815  # pylint: disable=invalid-name
    dbid: KBEUInt64
    data: KBEBlob
    callback_id: KBEUInt32


@dataclass(frozen=True)
class ChargeMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::charge."""

    success: bool
    result: ChargeParsedMsgData
    msg_id: int = msgspec.dbmgr.charge.id
    text: str = ""


class ChargeMsgParser(IMsgParser):
    """Парсер для DBMgr::charge."""

    def parse(self, msg: Message) -> ChargeMsgParserResult:
        """Парсинг сообщения DBMgr::charge."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = ChargeParsedMsgData(*values)
        return ChargeMsgParserResult(success=True, result=pd)


@dataclass
class OnChargeCBParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::onChargeCB."""

    baseappID: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name
    order_id: KBEString
    dbid: KBEUInt64
    extraDatas: KBEBlob  # noqa: N815  # pylint: disable=invalid-name
    cbid: KBEUInt32
    errorCode: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name

    @property
    def error_code_enum(self) -> ServerError:
        """Код ошибки."""
        return ServerError(self.errorCode)

    __add_to_dict__: ClassVar = ("error_code_enum",)


@dataclass(frozen=True)
class OnChargeCBMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::onChargeCB."""

    success: bool
    result: OnChargeCBParsedMsgData
    msg_id: int = msgspec.dbmgr.onChargeCB.id
    text: str = ""


class OnChargeCBMsgParser(IMsgParser):
    """Парсер для DBMgr::onChargeCB."""

    def parse(self, msg: Message) -> OnChargeCBMsgParserResult:
        """Парсинг сообщения DBMgr::onChargeCB."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnChargeCBParsedMsgData(*values)
        return OnChargeCBMsgParserResult(success=True, result=pd)


@dataclass
class AccountActivateParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::accountActivate."""

    scode: KBEString


@dataclass(frozen=True)
class AccountActivateMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::accountActivate."""

    success: bool
    result: AccountActivateParsedMsgData
    msg_id: int = msgspec.dbmgr.accountActivate.id
    text: str = ""


class AccountActivateMsgParser(IMsgParser):
    """Парсер для DBMgr::accountActivate."""

    def parse(self, msg: Message) -> AccountActivateMsgParserResult:
        """Парсинг сообщения DBMgr::accountActivate."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = AccountActivateParsedMsgData(*values)
        return AccountActivateMsgParserResult(success=True, result=pd)


@dataclass
class AccountReqResetPasswordParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::accountReqResetPassword."""

    accountName: KBEString  # noqa: N815  # pylint: disable=invalid-name


@dataclass(frozen=True)
class AccountReqResetPasswordMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::accountReqResetPassword."""

    success: bool
    result: AccountReqResetPasswordParsedMsgData
    msg_id: int = msgspec.dbmgr.accountReqResetPassword.id
    text: str = ""


class AccountReqResetPasswordMsgParser(IMsgParser):
    """Парсер для DBMgr::accountReqResetPassword."""

    def parse(self, msg: Message) -> AccountReqResetPasswordMsgParserResult:
        """Парсинг сообщения DBMgr::accountReqResetPassword."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = AccountReqResetPasswordParsedMsgData(*values)
        return AccountReqResetPasswordMsgParserResult(success=True, result=pd)


@dataclass
class AccountResetPasswordParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::accountResetPassword."""

    accountName: KBEString  # noqa: N815  # pylint: disable=invalid-name
    newpassword: KBEString
    code: KBEString


@dataclass(frozen=True)
class AccountResetPasswordMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::accountResetPassword."""

    success: bool
    result: AccountResetPasswordParsedMsgData
    msg_id: int = msgspec.dbmgr.accountResetPassword.id
    text: str = ""


class AccountResetPasswordMsgParser(IMsgParser):
    """Парсер для DBMgr::accountResetPassword."""

    def parse(self, msg: Message) -> AccountResetPasswordMsgParserResult:
        """Парсинг сообщения DBMgr::accountResetPassword."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = AccountResetPasswordParsedMsgData(*values)
        return AccountResetPasswordMsgParserResult(success=True, result=pd)


@dataclass
class AccountReqBindMailParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::accountReqBindMail."""

    entityID: KBEUInt32  # noqa: N815  # pylint: disable=invalid-name
    accountName: KBEString  # noqa: N815  # pylint: disable=invalid-name
    password: KBEString
    email: KBEString


@dataclass(frozen=True)
class AccountReqBindMailMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::accountReqBindMail."""

    success: bool
    result: AccountReqBindMailParsedMsgData
    msg_id: int = msgspec.dbmgr.accountReqBindMail.id
    text: str = ""


class AccountReqBindMailMsgParser(IMsgParser):
    """Парсер для DBMgr::accountReqBindMail."""

    def parse(self, msg: Message) -> AccountReqBindMailMsgParserResult:
        """Парсинг сообщения DBMgr::accountReqBindMail."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = AccountReqBindMailParsedMsgData(*values)
        return AccountReqBindMailMsgParserResult(success=True, result=pd)


@dataclass
class AccountBindMailParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::accountBindMail."""

    accountName: KBEString  # noqa: N815  # pylint: disable=invalid-name
    code: KBEString


@dataclass(frozen=True)
class AccountBindMailMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::accountBindMail."""

    success: bool
    result: AccountBindMailParsedMsgData
    msg_id: int = msgspec.dbmgr.accountBindMail.id
    text: str = ""


class AccountBindMailMsgParser(IMsgParser):
    """Парсер для DBMgr::accountBindMail."""

    def parse(self, msg: Message) -> AccountBindMailMsgParserResult:
        """Парсинг сообщения DBMgr::accountBindMail."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = AccountBindMailParsedMsgData(*values)
        return AccountBindMailMsgParserResult(success=True, result=pd)


@dataclass
class AccountNewPasswordParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::accountNewPassword."""

    entity_id: KBEUInt32
    accountName: KBEString  # noqa: N815  # pylint: disable=invalid-name
    password: KBEString
    newPassword: KBEString  # noqa: N815  # pylint: disable=invalid-name


@dataclass(frozen=True)
class AccountNewPasswordMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::accountNewPassword."""

    success: bool
    result: AccountNewPasswordParsedMsgData
    msg_id: int = msgspec.dbmgr.accountNewPassword.id
    text: str = ""


class AccountNewPasswordMsgParser(IMsgParser):
    """Парсер для DBMgr::accountNewPassword."""

    def parse(self, msg: Message) -> AccountNewPasswordMsgParserResult:
        """Парсинг сообщения DBMgr::accountNewPassword."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = AccountNewPasswordParsedMsgData(*values)
        return AccountNewPasswordMsgParserResult(success=True, result=pd)


@dataclass
class StartProfileParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::startProfile."""

    profileName: KBEString  # noqa: N815  # pylint: disable=invalid-name
    profileType: KBEInt8  # noqa: N815  # pylint: disable=invalid-name
    timelen: KBEUInt32


@dataclass(frozen=True)
class StartProfileMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::startProfile."""

    success: bool
    result: StartProfileParsedMsgData
    msg_id: int = msgspec.dbmgr.startProfile.id
    text: str = ""


class StartProfileMsgParser(IMsgParser):
    """Парсер для DBMgr::startProfile."""

    def parse(self, msg: Message) -> StartProfileMsgParserResult:
        """Парсинг сообщения DBMgr::startProfile."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = StartProfileParsedMsgData(*values)
        return StartProfileMsgParserResult(success=True, result=pd)


@dataclass
class ReqKillServerParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::reqKillServer."""

    component_id: KBEUInt16
    componentType: KBEUInt8  # noqa: N815  # pylint: disable=invalid-name
    username: KBEString
    uid: KBEInt32
    reason: KBEString

    @property
    def component_type_enum(self) -> ComponentType:
        """Тип компонента."""
        return ComponentType(self.componentType)

    __add_to_dict__: ClassVar = ("component_type_enum",)


@dataclass(frozen=True)
class ReqKillServerMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::reqKillServer."""

    success: bool
    result: ReqKillServerParsedMsgData
    msg_id: int = msgspec.dbmgr.reqKillServer.id
    text: str = ""


class ReqKillServerMsgParser(IMsgParser):
    """Парсер для DBMgr::reqKillServer."""

    def parse(self, msg: Message) -> ReqKillServerMsgParserResult:
        """Парсинг сообщения DBMgr::reqKillServer."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = ReqKillServerParsedMsgData(*values)
        return ReqKillServerMsgParserResult(success=True, result=pd)


@dataclass
class QueryWatcherParsedMsgData(ParsedMsgData):
    """Данные парсинга DBMgr::queryWatcher."""

    path: KBEString


@dataclass(frozen=True)
class QueryWatcherMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::queryWatcher."""

    success: bool
    result: QueryWatcherParsedMsgData
    msg_id: int = msgspec.dbmgr.queryWatcher.id
    text: str = ""


class QueryWatcherMsgParser(IMsgParser):
    """Парсер для DBMgr::queryWatcher."""

    def parse(self, msg: Message) -> QueryWatcherMsgParserResult:
        """Парсинг сообщения DBMgr::queryWatcher."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = QueryWatcherParsedMsgData(*values)
        return QueryWatcherMsgParserResult(success=True, result=pd)


@dataclass
class OnLookAppParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения DBMgr::onLookApp."""

    componentType: KBEComponentType  # noqa: N815
    componentId: KBEComponentId  # noqa: N815
    shutdownState: KBEInt8  # noqa: N815

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
    """Парсер для DBMgr::onLookApp."""

    success: bool
    result: OnLookAppParsedMsgData
    msg_id: int = msgspec.loginapp.onLookApp.id
    text: str = ""


class OnLookAppMsgParser(IMsgParser):
    """Парсер для DBMgr::onLookApp."""

    def parse(self, msg: Message) -> OnLookAppMsgParserResult:
        """Распарсить сообщение DBMgr::onLookApp.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnLookAppParserMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnLookAppParsedMsgData(*values)
        return OnLookAppMsgParserResult(success=True, result=pd)


@dataclass(frozen=True)
class ReqCloseServerParsedMsgParserResult(MsgParserResult):
    """Результат парсинга Interfaces::reqCloseServer."""

    success: bool
    result: ReqCloseServerParsedMsgData
    msg_id: int = msgspec.interfaces.reqCloseServer.id
    text: str = ""


class ReqCloseServerMsgParser(IMsgParser):
    """Парсер для Interfaces::reqCloseServer."""

    def parse(self, msg: Message) -> ReqCloseServerParsedMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = ReqCloseServerParsedMsgData(*values)
        return ReqCloseServerParsedMsgParserResult(success=True, result=pd)
