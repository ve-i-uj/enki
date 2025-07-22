
"""Обработчик сообщений от компонента DBMgr."""

import logging
import pickle
from dataclasses import dataclass
from typing import Any

from enki.core import kbepickle, kbetype, msgspec
from enki.kbeenum import ComponentType
from enki.core.message import Message
from enki.misc import devonly

from ..imsgparser import Handler, MsgParserResult, ParsedMsgData
from .common import OnAppActiveTickParsedData, OnRegisterNewAppParsedData

logger = logging.getLogger(__file__)


@dataclass
class OnRegisterNewAppMsgResult(MsgParserResult):
    """Обработчик для DBMgr::onRegisterNewApp."""
    success: bool
    result: OnRegisterNewAppParsedData
    msg_id: int = msgspec.app.dbmgr.onRegisterNewApp.id
    text: str = ''


class OnRegisterNewAppMsgParser(IMsgParser):

    def parse(self, msg: Message) -> OnRegisterNewAppMsgResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnRegisterNewAppParsedData(*msg.get_values())
        return OnRegisterNewAppMsgResult(True, pd)


@dataclass
class OnAppActiveTickMsgResult(MsgParserResult):
    """Обработчик для DBMgr::onAppActiveTick."""
    success: bool
    result: OnAppActiveTickParsedData
    msg_id: int = msgspec.app.dbmgr.onAppActiveTick.id
    text: str = ''


class OnAppActiveTickMsgParser(IMsgParser):

    def parse(self, msg: Message) -> OnAppActiveTickMsgResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnAppActiveTickParsedData(*msg.get_values())
        return OnAppActiveTickMsgResult(True, pd)


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
    msg_id: int = msgspec.app.dbmgr.onBroadcastGlobalDataChanged.id
    text: str = ''


class OnBroadcastGlobalDataChangedMsgParser(IMsgParser):

    def parse(self, msg: Message) -> OnBroadcastGlobalDataChangedMsgResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
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
    msg_id: int = msgspec.app.dbmgr.syncEntityStreamTemplate.id
    text: str = ''


class SyncEntityStreamTemplateMsgParser(IMsgParser):
    """
    Довольно сложная логика заполнения данных, основанная на описание сущности
    (т.е. нужно иметь ссылку на assets'ы и в по ним заполнять данные).

    Поэтому пока просто возвращает байты без парсинга.
    см. bool SyncEntityStreamTemplateHandler::process()
    """

    def parse(self, msg: Message) -> SyncEntityStreamTemplateMsgResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
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
    msg_id: int = msgspec.app.dbmgr.entityAutoLoad.id
    text: str = ''


class EntityAutoLoadMsgParser(IMsgParser):

    def parse(self, msg: Message) -> EntityAutoLoadMsgResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = EntityAutoLoadParsedData(*msg.get_values())
        return EntityAutoLoadMsgResult(True, pd)
