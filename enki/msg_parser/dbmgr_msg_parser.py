"""Парсер сообщений от компонента DBMgr."""

import logging
import pickle
from dataclasses import dataclass
from typing import Any

from enki import msgspec
from enki.core.kbepickle.kbepickle import pickle_global_data_value
from enki.kbetype.decoders.basic_data_type_decoders import BLOB, UINT8
from enki.kbetype.decoders.custom_decoders import BOOL, COMPONENT_TYPE, KBEBool
from enki.kbeenum import ComponentType
from enki.misc import devonly
from enki.msg.message import Message

from .common import OnAppActiveTickParsedMsgData, OnRegisterNewAppParsedMsgData
from .imsg_parser import IMsgParser, MsgParserResult, ParsedMsgData

logger = logging.getLogger(__name__)


@dataclass
class OnRegisterNewAppMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::onRegisterNewApp."""

    success: bool
    result: OnRegisterNewAppParsedMsgData
    msg_id: int = msgspec.dbmgr.onRegisterNewApp.id
    text: str = ""


class OnRegisterNewAppMsgParser(IMsgParser):
    """Парсер для DBMgr::onRegisterNewApp."""

    def parse(self, msg: Message) -> OnRegisterNewAppMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnRegisterNewAppParsedMsgData(*values)
        return OnRegisterNewAppMsgParserResult(True, pd)


@dataclass
class OnAppActiveTickMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::onAppActiveTick."""

    success: bool
    result: OnAppActiveTickParsedMsgData
    msg_id: int = msgspec.dbmgr.onAppActiveTick.id
    text: str = ""


class OnAppActiveTickMsgParser(IMsgParser):
    def parse(self, msg: Message) -> OnAppActiveTickMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnAppActiveTickParsedMsgData(*values)
        return OnAppActiveTickMsgParserResult(True, pd)


@dataclass
class OnBroadcastGlobalDataChangedParsedMsgData(ParsedMsgData):
    dataType: int
    isDelete: KBEBool
    key: str
    value: Any
    component_type: ComponentType


@dataclass
class OnBroadcastGlobalDataChangedMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::onBroadcastGlobalDataChanged."""

    success: bool
    result: OnBroadcastGlobalDataChangedParsedMsgData
    msg_id: int = msgspec.dbmgr.onBroadcastGlobalDataChanged.id
    text: str = ""


class OnBroadcastGlobalDataChangedMsgParser(IMsgParser):
    def parse(self, msg: Message) -> OnBroadcastGlobalDataChangedMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])
        dataType, offset = UINT8.decode(data)
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
        componentType = ComponentType(component_type)

        pd = OnBroadcastGlobalDataChangedParsedMsgData(
            dataType, is_delete, key, value, componentType
        )

        assert not data
        return OnBroadcastGlobalDataChangedMsgParserResult(True, pd)


@dataclass
class SyncEntityStreamTemplateParsedMsgData(ParsedMsgData):
    data: bytes


@dataclass
class SyncEntityStreamTemplateMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::syncEntityStreamTemplate."""

    success: bool
    result: SyncEntityStreamTemplateParsedMsgData
    msg_id: int = msgspec.dbmgr.syncEntityStreamTemplate.id
    text: str = ""


class SyncEntityStreamTemplateMsgParser(IMsgParser):
    """Довольно сложная логика заполнения данных, основанная на описание сущности
    (т.е. нужно иметь ссылку на assets'ы и в по ним заполнять данные).

    Поэтому пока просто возвращает байты без парсинга.
    см. bool SyncEntityStreamTemplateHandler::process()
    """

    def parse(self, msg: Message) -> SyncEntityStreamTemplateMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        memoryview(values[0])
        pd = SyncEntityStreamTemplateParsedMsgData(*values)

        return SyncEntityStreamTemplateMsgParserResult(True, pd)


@dataclass
class EntityAutoLoadParsedMsgData(ParsedMsgData):
    dbInterfaceIndex: int
    componentID: int
    entityType: int
    start: int
    end: int


@dataclass
class EntityAutoLoadMsgParserResult(MsgParserResult):
    """Результат парсинга DBMgr::entityAutoLoad."""

    success: bool
    result: EntityAutoLoadParsedMsgData
    msg_id: int = msgspec.dbmgr.entityAutoLoad.id
    text: str = ""


class EntityAutoLoadMsgParser(IMsgParser):
    """Парсер для DBMgr::entityAutoLoad."""

    def parse(self, msg: Message) -> EntityAutoLoadMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = EntityAutoLoadParsedMsgData(*values)
        return EntityAutoLoadMsgParserResult(success=True, result=pd)
