"""Парсер сообщений от компонента DBMgr."""

import logging
import pickle
from dataclasses import dataclass
from typing import Any, ClassVar

from enki import msgspec
from enki.core.kbepickle.kbepickle import pickle_global_data_value
from enki.kbeenum import ComponentType, ServerError
from enki.kbetype.decoders.basic_data_type_decoders import BLOB, BOOL, UINT8
from enki.kbetype.decoders.custom_decoders import (
    COMPONENT_TYPE,
    KBEComponentId,
    KBEEntityId,
)
from enki.kbetype.pytypes.basic_data_types import (
    KBEBlob,
    KBEBool,
    KBEString,
    KBEUInt16,
)
from enki.misc import devonly
from enki.msg.message import Message

from .common import OnAppActiveTickParsedMsgData, OnRegisterNewAppParsedMsgData
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

    dataType: int  # noqa: N815  # pylint: disable=invalid-name
    isDelete: KBEBool  # noqa: N815  # pylint: disable=invalid-name
    key: str
    value: Any
    component_type: ComponentType


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

    def parse(self, msg: Message) -> OnBroadcastGlobalDataChangedMsgParserResult:
        """Парсинг сообщения DBMgr::onBroadcastGlobalDataChanged.

        :param msg: Сообщение для парсинга
        :return: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])
        dataType, offset = UINT8.decode(data)  # noqa: N806  # pylint: disable=invalid-name
        data = data[offset:]
        is_delete, offset = BOOL.decode(data)
        data = data[offset:]
        key_data, offset = BLOB.decode(data)
        data = data[offset:]

        key = pickle.loads(key_data)

        if is_delete:
            value = None
        else:
            value_data, offset = BLOB.decode(data)
            data = data[offset:]
            value = pickle_global_data_value(value_data)

        component_type, offset = COMPONENT_TYPE.decode(data)
        data = data[offset:]
        componentType = ComponentType(component_type)  # noqa: N806  # pylint: disable=invalid-name

        pd = OnBroadcastGlobalDataChangedParsedMsgData(
            dataType, is_delete, key, value, componentType
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

    data: bytes


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
