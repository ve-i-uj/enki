"""Обработчик сообщений от компонента DBMgr."""

import logging
import pickle
from dataclasses import dataclass
from typing import Any

from enki import msgspec
from enki.kbeenum import ComponentType
from enki.misc import devonly
from enki.msg.message import Message

from .common import OnAppActiveTickParsedMsgData, OnRegisterNewAppParsedMsgData
from .imsg_parser import IMsgParser, MsgParserResult, ParsedMsgData

logger = logging.getLogger(__name__)


@dataclass
class OnRegisterNewAppMsgParserResult(MsgParserResult):
    """Обработчик для DBMgr::onRegisterNewApp."""

    success: bool
    result: OnRegisterNewAppParsedMsgData
    msg_id: int = msgspec.dbmgr.onRegisterNewApp.id
    text: str = ""


class OnRegisterNewAppMsgParser(IMsgParser):
    """Обработчик для DBMgr::onRegisterNewApp."""

    def parse(self, msg: Message) -> OnRegisterNewAppMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnRegisterNewAppParsedMsgData(*values)
        return OnRegisterNewAppMsgParserResult(True, pd)


@dataclass
class OnAppActiveTickMsgParserResult(MsgParserResult):
    """Обработчик для DBMgr::onAppActiveTick."""

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
class OnBroadcastGlobalDataChangedParsedData(ParsedMsgData):
    dataType: int
    isDelete: bool
    key: str
    value: Any
    componentType: ComponentType


@dataclass
class OnBroadcastGlobalDataChangedMsgResult(MsgParserResult):
    """Обработчик для DBMgr::onBroadcastGlobalDataChanged."""

    success: bool
    result: OnBroadcastGlobalDataChangedParsedData
    msg_id: int = msgspec.dbmgr.onBroadcastGlobalDataChanged.id
    text: str = ""


class OnBroadcastGlobalDataChangedMsgParser(IMsgParser):
    def parse(self, msg: Message) -> OnBroadcastGlobalDataChangedMsgResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        data: memoryview = msg.get_values()[0]
        dataType, offset = kbetype.UINT8.decode(data)
        data = data[offset:]
        isDelete, offset = kbetype.BOOL.decode(data)
        data = data[offset:]
        key_data, offset = kbetype.BLOB.decode(data)
        data = data[offset:]
        key = pickle.loads(key_data)

        if isDelete:
            value = None
        else:
            value_data, offset = kbetype.BLOB.decode(data)
            data = data[offset:]
            value = kbepickle.pickle_global_data_value(value_data)

        component_type, offset = kbetype.COMPONENT_TYPE.decode(data)
        data = data[offset:]
        componentType = ComponentType(component_type)

        pd = OnBroadcastGlobalDataChangedParsedData(
            dataType, isDelete, key, value, componentType
        )

        assert not data
        return OnBroadcastGlobalDataChangedMsgResult(True, pd)


@dataclass
class SyncEntityStreamTemplateParsedData(ParsedMsgData):
    data: bytes


@dataclass
class SyncEntityStreamTemplateMsgResult(MsgParserResult):
    """Обработчик для DBMgr::syncEntityStreamTemplate."""

    success: bool
    result: SyncEntityStreamTemplateParsedData
    msg_id: int = msgspec.dbmgr.syncEntityStreamTemplate.id
    text: str = ""


class SyncEntityStreamTemplateMsgParser(IMsgParser):
    """
    Довольно сложная логика заполнения данных, основанная на описание сущности
    (т.е. нужно иметь ссылку на assets'ы и в по ним заполнять данные).

    Поэтому пока просто возвращает байты без парсинга.
    см. bool SyncEntityStreamTemplateHandler::process()
    """

    def parse(self, msg: Message) -> SyncEntityStreamTemplateMsgResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        data: memoryview = msg.get_values()[0]
        pd = SyncEntityStreamTemplateParsedData(data.tobytes())

        return SyncEntityStreamTemplateMsgResult(True, pd)


@dataclass
class EntityAutoLoadParsedData(ParsedMsgData):
    dbInterfaceIndex: int
    componentID: int
    entityType: int
    start: int
    end: int


@dataclass
class EntityAutoLoadMsgResult(MsgParserResult):
    """Обработчик для DBMgr::entityAutoLoad."""

    success: bool
    result: EntityAutoLoadParsedData
    msg_id: int = msgspec.dbmgr.entityAutoLoad.id
    text: str = ""


class EntityAutoLoadMsgParser(IMsgParser):
    def parse(self, msg: Message) -> EntityAutoLoadMsgResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        pd = EntityAutoLoadParsedData(*msg.get_values())
        return EntityAutoLoadMsgResult(True, pd)
