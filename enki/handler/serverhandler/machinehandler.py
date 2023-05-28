"""Обработчик сообщений от компонента Machine."""

from __future__ import annotations
import copy
import dataclasses
import json

import logging
from dataclasses import dataclass
from typing import Optional

from enki.core import kbemath
from enki.core import enkitype
from enki.core.enkitype import AppAddr
from enki.core import msgspec
from enki.core.kbeenum import ComponentType
from enki.core.message import Message
from enki.misc import devonly

from ..base import ParsedMsgData, Handler, HandlerResult

logger = logging.getLogger(__file__)


@dataclass
class OnBroadcastInterfaceParsedData(ParsedMsgData):
    uid: int
    username: str
    componentType: int
    componentID: int
    componentIDEx: int
    globalorderid: int
    grouporderid: int
    gus: int
    intaddr: int
    intport: int
    extaddr: int
    extport: int
    extaddrEx: str
    pid: int
    cpu: int
    mem: int
    usedmem: int
    state: int
    machineID: int
    extradata: int
    extradata1: int
    extradata2: int
    extradata3: int
    backRecvAddr: int
    backRecvPort: int

    @staticmethod
    def get_empty() -> OnBroadcastInterfaceParsedData:
        return OnBroadcastInterfaceParsedData(
            uid=1,
            username='root',
            componentType=ComponentType.UNKNOWN_COMPONENT.value,
            componentID=0,
            componentIDEx=0,
            globalorderid=-1,
            grouporderid=-1,
            gus=-1,
            intaddr=0,
            intport=0,
            extaddr=0,
            extport=0,
            extaddrEx='',
            pid=0,
            cpu=0,
            mem=0,
            usedmem=0,
            state=0,
            machineID=1,
            extradata=0,
            extradata1=0,
            extradata2=0,
            extradata3=0,
            backRecvAddr=0,
            backRecvPort=0
        )

    def copy(self) -> OnBroadcastInterfaceParsedData:
        return copy.deepcopy(self)

    # Эти два метода нужны для кэширования данных в файл

    @staticmethod
    def to_json(pd: OnBroadcastInterfaceParsedData) -> str:
        return json.dumps(dataclasses.asdict(pd))

    @staticmethod
    def from_json(text: str) -> OnBroadcastInterfaceParsedData:
        return OnBroadcastInterfaceParsedData(**json.loads(text))

    # ***

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

    @property
    def callback_address(self) -> AppAddr:
        return AppAddr(
            kbemath.int2ip(self.backRecvAddr),
            kbemath.int2port(self.backRecvPort)
        )

    @callback_address.setter
    def callback_address(self, addr: AppAddr):
        self.backRecvAddr = kbemath.ip2int(addr.host)
        self.backRecvPort = kbemath.port2int(addr.port)

    __add_to_dict__ = [
        'component_type', 'internal_address', 'external_address',
        'callback_address'
    ]


@dataclass
class OnBroadcastInterfaceHandlerResult(HandlerResult):
    """Обработчик для Machine::onBroadcastInterface."""
    success: bool
    result: Optional[OnBroadcastInterfaceParsedData]
    msg_id: int = msgspec.app.machine.onBroadcastInterface.id
    text: str = ''


class OnBroadcastInterfaceHandler(Handler):

    def handle(self, msg: Message) -> OnBroadcastInterfaceHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnBroadcastInterfaceParsedData(*msg.get_values())
        return OnBroadcastInterfaceHandlerResult(True, pd)


@dataclass
class OnFindInterfaceAddrParsedData(ParsedMsgData):
    uid: int
    username: str
    componentType: int
    componentID: int
    findComponentType: int
    addr: int
    finderRecvPort: int

    @property
    def component_type(self) -> ComponentType:
        return ComponentType(self.componentType)

    @property
    def callback_address(self) -> AppAddr:
        return AppAddr(
            kbemath.int2ip(self.addr),
            kbemath.int2port(self.finderRecvPort)
        )

    @callback_address.setter
    def callback_address(self, addr: AppAddr):
        self.addr = kbemath.ip2int(addr.host)
        self.finderRecvPort = kbemath.port2int(addr.port)

    @property
    def find_component_type(self) -> ComponentType:
        try:
            return ComponentType(self.findComponentType)
        except ValueError:
            return ComponentType.UNKNOWN_COMPONENT

    __add_to_dict__ = [
        'component_type', 'callback_address', 'find_component_type'
    ]


@dataclass
class OnFindInterfaceAddrHandlerResult(HandlerResult):
    """Обработчик для Machine::onBroadcastInterface."""
    success: bool
    result: OnFindInterfaceAddrParsedData
    msg_id: int = msgspec.app.machine.onFindInterfaceAddr.id
    text: str = ''


class OnFindInterfaceAddrHandler(Handler):

    def handle(self, msg: Message) -> OnFindInterfaceAddrHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnFindInterfaceAddrParsedData(*msg.get_values())
        return OnFindInterfaceAddrHandlerResult(True, pd)


@dataclass
class QueryComponentIDParsedData(ParsedMsgData):
    componentType: int
    componentID: int
    uid: int
    finderRecvPort: int
    macMD5: int
    pid: int

    @property
    def component_type(self) -> ComponentType:
        return ComponentType(self.componentType)

    @property
    def callback_port(self) -> int:
        return kbemath.int2port(self.finderRecvPort)

    @callback_port.setter
    def callback_port(self, value: int):
        self.finderRecvPort = kbemath.port2int(value)

    __add_to_dict__ = ['component_type', 'callback_port']


@dataclass
class QueryComponentIDHandlerResult(HandlerResult):
    """Обработчик для Machine::onBroadcastInterface."""
    success: bool
    result: Optional[QueryComponentIDParsedData]
    msg_id: int = msgspec.app.machine.queryComponentID.id
    text: str = ''


class QueryComponentIDHandler(Handler):

    def handle(self, msg: Message) -> QueryComponentIDHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = QueryComponentIDParsedData(*msg.get_values())
        return QueryComponentIDHandlerResult(True, pd)
