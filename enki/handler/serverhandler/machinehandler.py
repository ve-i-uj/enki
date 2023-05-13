"""Обработчик сообщений от компонента Machine."""

import logging
from dataclasses import dataclass

from enki.core import kbeenum, kbemath
from enki.core import enkitype
from enki.core import msgspec
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

    @property
    def component_type(self) -> kbeenum.ComponentType:
        return kbeenum.ComponentType(self.componentType)

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
        'component_type', 'internal_address', 'external_address'
    ]


@dataclass
class OnBroadcastInterfaceHandlerResult(HandlerResult):
    """Обработчик для Machine::onBroadcastInterface."""
    success: bool
    result: OnBroadcastInterfaceParsedData
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
    def component_type(self) -> kbeenum.ComponentType:
        return kbeenum.ComponentType(self.componentType)

    @property
    def callback_address(self) -> enkitype.AppAddr:
        return enkitype.AppAddr(
            kbemath.int2ip(self.addr),
            kbemath.int2port(self.finderRecvPort)
        )

    @property
    def find_component_type(self) -> kbeenum.ComponentType:
        try:
            return kbeenum.ComponentType(self.findComponentType)
        except ValueError:
            return kbeenum.ComponentType.UNKNOWN_COMPONENT_TYPE

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
    def component_type(self) -> kbeenum.ComponentType:
        return kbeenum.ComponentType(self.componentType)

    @property
    def callback_port(self) -> int:
        return kbemath.int2port(self.finderRecvPort)

    __add_to_dict__ = ['component_type', 'callback_port']


@dataclass
class QueryComponentIDHandlerResult(HandlerResult):
    """Обработчик для Machine::onBroadcastInterface."""
    success: bool
    result: QueryComponentIDParsedData
    msg_id: int = msgspec.app.machine.queryComponentID.id
    text: str = ''


class QueryComponentIDHandler(Handler):

    def handle(self, msg: Message) -> QueryComponentIDHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = QueryComponentIDParsedData(*msg.get_values())
        return QueryComponentIDHandlerResult(True, pd)
