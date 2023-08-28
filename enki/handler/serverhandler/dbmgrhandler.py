"""Обработчик сообщений от компонента DBMgr."""

import logging
import pickle
from dataclasses import dataclass
from typing import Any

from enki.core import kbetype, msgspec, utils
from enki.core.kbeenum import ComponentType
from enki.core.message import Message
from enki.misc import devonly

from ..base import Handler, HandlerResult, ParsedMsgData
from .common import OnAppActiveTickParsedData, OnRegisterNewAppParsedData

logger = logging.getLogger(__file__)


@dataclass
class OnRegisterNewAppHandlerResult(HandlerResult):
    """Обработчик для DBMgr::onRegisterNewApp."""
    success: bool
    result: OnRegisterNewAppParsedData
    msg_id: int = msgspec.app.dbmgr.onRegisterNewApp.id
    text: str = ''


class OnRegisterNewAppHandler(Handler):

    def handle(self, msg: Message) -> OnRegisterNewAppHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnRegisterNewAppParsedData(*msg.get_values())
        return OnRegisterNewAppHandlerResult(True, pd)


@dataclass
class OnAppActiveTickHandlerResult(HandlerResult):
    """Обработчик для DBMgr::onAppActiveTick."""
    success: bool
    result: OnAppActiveTickParsedData
    msg_id: int = msgspec.app.dbmgr.onAppActiveTick.id
    text: str = ''


class OnAppActiveTickHandler(Handler):

    def handle(self, msg: Message) -> OnAppActiveTickHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnAppActiveTickParsedData(*msg.get_values())
        return OnAppActiveTickHandlerResult(True, pd)


@dataclass
class OnBroadcastGlobalDataChangedParsedData(ParsedMsgData):
    dataType: int
    isDelete: bool
    key: str
    value: Any
    componentType: ComponentType


@dataclass
class OnBroadcastGlobalDataChangedHandlerResult(HandlerResult):
    """Обработчик для DBMgr::onBroadcastGlobalDataChanged."""
    success: bool
    result: OnBroadcastGlobalDataChangedParsedData
    msg_id: int = msgspec.app.dbmgr.onBroadcastGlobalDataChanged.id
    text: str = ''


class OnBroadcastGlobalDataChangedHandler(Handler):

    def handle(self, msg: Message) -> OnBroadcastGlobalDataChangedHandlerResult:
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
            value = utils.pickle_global_data_value(value_data)

        component_type, offset = kbetype.COMPONENT_TYPE.decode(data)
        data = data[offset:]
        componentType = ComponentType(component_type)

        pd = OnBroadcastGlobalDataChangedParsedData(
            dataType, isDelete, key, value, componentType
        )

        assert not data
        return OnBroadcastGlobalDataChangedHandlerResult(True, pd)


@dataclass
class SyncEntityStreamTemplateParsedData(ParsedMsgData):
    data: bytes


@dataclass
class SyncEntityStreamTemplateHandlerResult(HandlerResult):
    """Обработчик для DBMgr::syncEntityStreamTemplate."""
    success: bool
    result: SyncEntityStreamTemplateParsedData
    msg_id: int = msgspec.app.dbmgr.syncEntityStreamTemplate.id
    text: str = ''


class SyncEntityStreamTemplateHandler(Handler):
    """
    Довольно сложная логика заполнения данных, основанная на описание сущности
    (т.е. нужно иметь ссылку на assets'ы и в по ним заполнять данные).

    Поэтому пока просто возвращает байты без парсинга.
    см. bool SyncEntityStreamTemplateHandler::process()
    """

    def handle(self, msg: Message) -> SyncEntityStreamTemplateHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        data: memoryview = msg.get_values()[0]
        pd = SyncEntityStreamTemplateParsedData(data.tobytes())

        return SyncEntityStreamTemplateHandlerResult(True, pd)


@dataclass
class EntityAutoLoadParsedData(ParsedMsgData):
    dbInterfaceIndex: int
    componentID: int
    entityType: int
    start: int
    end: int


@dataclass
class EntityAutoLoadHandlerResult(HandlerResult):
    """Обработчик для DBMgr::entityAutoLoad."""
    success: bool
    result: EntityAutoLoadParsedData
    msg_id: int = msgspec.app.dbmgr.entityAutoLoad.id
    text: str = ''


class EntityAutoLoadHandler(Handler):

    def handle(self, msg: Message) -> EntityAutoLoadHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = EntityAutoLoadParsedData(*msg.get_values())
        return EntityAutoLoadHandlerResult(True, pd)
