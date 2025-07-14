"""This module contains base classes of server message handlers."""

import dataclasses
from dataclasses import dataclass
import logging
from pathlib import Path
import pickle
from typing import Any, ClassVar

from enki.core import kbemath, kbepickle, kbetype
from enki.kbeenum import (
    COMPONENT_STATE_MAP,
    ComponentState,
    ComponentType,
    ShutdownState,
)
from enki.misc import result
from enki.misc.result import Result
from enki.net.addr import Addr
from enki.core import msgspec
from enki.core.message import Message, Message
from enki.misc import devonly

from ..imsgparser import ParsedMsgData, MsgParserResult, Handler

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
    def internal_address(self) -> Addr:
        return Addr(
            kbemath.int2ip(self.intaddr), kbemath.int2port(self.intport)
        )

    @property
    def external_address(self) -> Addr:
        return Addr(
            kbemath.int2ip(self.extaddr), kbemath.int2port(self.extport)
        )

    __add_to_dict__ = ["component_type", "internal_address", "external_address"]


@dataclass
class OnAppActiveTickParsedData(ParsedMsgData):
    componentType: int
    componentID: int

    @property
    def component_type(self) -> ComponentType:
        return ComponentType(self.componentType)

    __add_to_dict__ = ["component_type"]


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
        return ComponentState(COMPONENT_STATE_MAP[shutdown_state])

    __add_to_dict__ = ["component_type", "component_state"]


@dataclass
class LookAppParsedData(ParsedMsgData):
    pass


@dataclass
class CreateEntityAnywhereParsedData(ParsedMsgData):
    """Распарсенные данные сообщения BaseappMgr::reqCreateEntityAnywhere."""

    entityType: str
    initDataLength: int
    params: dict
    componentID: int
    callbackID: int
    # Если данные для pickle не получилось десериализовать (например, нужен
    # модуль исскуственно созданный модуль _upf, с атрибутом EntityCall)
    params_data: bytes = b""

    @property
    def baseapp_component_id(self) -> int:
        """Поле нужно для своего рода документации, что оно означает."""
        return self.componentID

    __add_to_dict__: ClassVar = ["baseapp_component_id"]


class CreateEntityAnywhereParser:
    """Парсер сообщения BaseappMgr::reqCreateEntityAnywhere."""

    def parse(self, msg: Message) -> CreateEntityAnywhereParsedData:
        """Распарсить сообщение BaseappMgr::reqCreateEntityAnywhere.

        Args:
            msg (Message): сообщение BaseappMgr::reqCreateEntityAnywhere

        Returns:
            CreateEntityAnywhereParsedData: распарсенные данные соощения

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        data = msg.get_values()[0]
        entity_type, offset = kbetype.STRING.decode(data)
        data = data[offset:]
        data_length, offset = kbetype.UINT32.decode(data)
        data = data[offset:]
        dct: dict = {}
        if data_length != 0:
            d = data[:data_length]
            data = data[data_length:]
            dct = kbepickle.pickle_global_data_value(d)
        component_id, offset = kbetype.COMPONENT_ID.decode(data)
        data = data[offset:]
        callback_id, offset = kbetype.CALLBACK_ID.decode(data)
        data = data[offset:]

        assert not data

        return CreateEntityAnywhereParsedData(
            entity_type, data_length, dct, component_id, callback_id
        )


@dataclass
class CreateCellEntityInNewSpaceFromBaseappParsedData(ParsedMsgData):
    entityType: str
    entitycallEntityID: int
    componentID: int
    spaceID: int
    hasClient: bool
    cellData: bytes = b""


class CreateCellEntityInNewSpaceFromBaseappParser:
    def parse(self, msg: Message) -> CreateCellEntityInNewSpaceFromBaseappParsedData:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
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
            entity_type,
            entity_id,
            component_id,
            space_id,
            has_client,
            data.tobytes(),
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
    def internal_address(self) -> Addr:
        return Addr(
            kbemath.int2ip(self.intaddr), kbemath.int2port(self.intport)
        )

    @property
    def external_address(self) -> Addr:
        return Addr(
            kbemath.int2ip(self.extaddr), kbemath.int2port(self.extport)
        )

    __add_to_dict__ = ["component_type", "internal_address", "external_address"]


@dataclass
class OnDbmgrInitCompletedParsedData(ParsedMsgData):
    gametime: int
    startID: int
    endID: int
    startGlobalOrder: int
    startGroupOrder: int
    digest: str
