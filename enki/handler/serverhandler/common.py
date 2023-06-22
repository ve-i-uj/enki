"""This module contains base classes of server message handlers."""

import dataclasses
from dataclasses import dataclass
import logging
from pathlib import Path
import pickle
from typing import Any

from enki.core import kbemath, kbetype, utils
from enki.core.kbeenum import ComponentState, ComponentType, ShutdownState
from enki.core import enkitype
from enki.core.enkitype import AppAddr, Result
from enki.core import msgspec
from enki.core.message import Message, Message
from enki.misc import devonly

from ..base import ParsedMsgData, HandlerResult, Handler

logger = logging.getLogger(__file__)


@dataclass
class OnRegisterNewAppParsedData(ParsedMsgData):
    uid: int
    username: str
    componentType: int
    componentID: int
    globalorderID: int
    grouporderID: int
    intaddr: int
    intport: int
    extaddr: int
    extport: int
    extaddrEx: str

    @property
    def component_type(self) -> ComponentType:
        try:
            return ComponentType(self.componentType)
        except ValueError:
            return ComponentType.UNKNOWN_COMPONENT

    @property
    def internal_address(self) -> enkitype.AppAddr:
        return enkitype.AppAddr(
            kbemath.int2ip(self.intaddr),
            kbemath.int2port(self.intport)
        )

    @property
    def external_address(self) -> enkitype.AppAddr:
        return enkitype.AppAddr(
            kbemath.int2ip(self.extaddr),
            kbemath.int2port(self.extport)
        )

    __add_to_dict__ = [
        'component_type', 'internal_address','external_address'
    ]


@dataclass
class OnAppActiveTickParsedData(ParsedMsgData):
    componentType: int
    componentID: int

    @property
    def component_type(self) -> ComponentType:
        return ComponentType(self.componentType)

    __add_to_dict__ = [
        'component_type'
    ]


@dataclass
class OnLookAppParsedData(ParsedMsgData):
    componentType: int
    componentID: int
    shutdownState: int

    @property
    def component_type(self) -> ComponentType:
        return ComponentType(self.componentType)

    @property
    def component_state(self) -> ComponentState:
        shutdown_state = ShutdownState(self.shutdownState)
        state_map = {
            ShutdownState.STOP: ComponentState.RUN,
            ShutdownState.BEGIN: ComponentState.SHUTTINGDOWN_BEGIN,
            ShutdownState.RUNNING: ComponentState.SHUTTINGDOWN_RUNNING,
            ShutdownState.END: ComponentState.STOP,
        }
        return ComponentState(state_map[shutdown_state])

    __add_to_dict__ = [
        'component_type', 'component_state'
    ]


@dataclass
class LookAppParsedData(ParsedMsgData):
    pass


@dataclass
class CreateEntityAnywhereParsedData(ParsedMsgData):
    entityType: str
    initDataLength: int
    params: dict
    componentID: int
    callbackID: int
    # Если данные для pickle не получилось десериализовать (например, нужен
    # модуль исскуственно созданный модуль _upf, с атрибутом EntityCall)
    params_data: bytes = b''

    @property
    def baseapp_component_id(self) -> int:
        """Поле нужно для своего рода документации, что оно означает."""
        return self.componentID

    __add_to_dict__ = [
        'baseapp_component_id'
    ]


class CreateEntityAnywhereParser:

    def parse(self, msg: Message) -> CreateEntityAnywhereParsedData:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        data = msg.get_values()[0]
        entity_type, offset = kbetype.STRING.decode(data)
        data = data[offset:]
        data_length, offset = kbetype.UINT32.decode(data)
        data = data[offset:]
        dct: dict = {}
        if data_length != 0:
            d = data[:data_length]
            data = data[data_length:]
            dct = utils.pickle_global_data_value(d)
        component_id, offset = kbetype.COMPONENT_ID.decode(data)
        data = data[offset:]
        callback_id, offset = kbetype.CALLBACK_ID.decode(data)
        data = data[offset:]

        assert not data

        pd = CreateEntityAnywhereParsedData(
            entity_type, data_length, dct, component_id, callback_id
        )
        return pd


@dataclass
class CreateCellEntityInNewSpaceFromBaseappParsedData(ParsedMsgData):
    entityType: str
    entitycallEntityID: int
    componentID: int
    spaceID: int
    hasClient: bool


class CreateCellEntityInNewSpaceFromBaseappParser:

    def parse(self, msg: Message) -> CreateCellEntityInNewSpaceFromBaseappParsedData:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        data: memoryview = msg.get_values()[0]
        entity_type, offset = kbetype.STRING.decode(data)
        data = data[offset:]
        entity_id, offset = kbetype.ENTITY_ID.decode(data)
        data = data[offset:]
        component_id, offset = kbetype.COMPONENT_ID.decode(data)
        data = data[offset:]
        space_id, offset = kbetype.SPACE_ID.decode(data)
        data = data[offset:]
        has_client, offset = kbetype.BOOL.decode(data)
        data = data[offset:]

        pd = CreateCellEntityInNewSpaceFromBaseappParsedData(
            entity_type, entity_id, component_id, space_id, has_client
        )

        return pd


@dataclass
class OnGetEntityAppFromDbmgrParsedData(ParsedMsgData):
    uid: int
    username: str
    componentType: int
    componentID: int
    globalorderID: int
    grouporderID: int
    intaddr: int
    intport: int
    extaddr: int
    extport: int
    extaddrEx: str

    @property
    def component_type(self) -> ComponentType:
        return ComponentType(self.componentType)

    @property
    def internal_address(self) -> AppAddr:
        return AppAddr(
            kbemath.int2ip(self.intaddr),
            kbemath.int2port(self.intport)
        )

    @property
    def external_address(self) -> AppAddr:
        return AppAddr(
            kbemath.int2ip(self.extaddr),
            kbemath.int2port(self.extport)
        )

    __add_to_dict__ = [
        'component_type', 'internal_address', 'external_address'
    ]


@dataclass
class OnDbmgrInitCompletedParsedData(ParsedMsgData):
    gametime: int
    startID: int
    endID: int
    startGlobalOrder: int
    startGroupOrder: int
    digest: str
