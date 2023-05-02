"""Обработчик сообщений от компонента Machine."""

import logging
import socket
from dataclasses import dataclass

from enki import enkitype, kbeenum, kbemath
from enki.net import msgspec
from enki.net.kbeclient import Message
from enki.misc import devonly

from . import base

logger = logging.getLogger(__file__)


@dataclass
class OnBroadcastInterfaceParsedData(base.ParsedMsgData):
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


@dataclass
class OnBroadcastInterfaceHandlerResult(base.HandlerResult):
    """Обработчик для Machine::onBroadcastInterface."""
    success: bool
    result: OnBroadcastInterfaceParsedData
    msg_id: int = msgspec.app.machine.onBroadcastInterface.id
    text: str = ''


class OnBroadcastInterfaceHandler(base.Handler):

    def handle(self, msg: Message) -> OnBroadcastInterfaceHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnBroadcastInterfaceParsedData(*msg.get_values())
        return OnBroadcastInterfaceHandlerResult(True, pd)


@dataclass
class OnFindInterfaceAddrParsedData(base.ParsedMsgData):
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

    __add_to_dict__ = ['component_type', 'callback_address']


@dataclass
class OnFindInterfaceAddrHandlerResult(base.HandlerResult):
    """Обработчик для Machine::onBroadcastInterface."""
    success: bool
    result: OnFindInterfaceAddrParsedData
    msg_id: int = msgspec.app.machine.onFindInterfaceAddr.id
    text: str = ''


class OnFindInterfaceAddrHandler(base.Handler):

    def handle(self, msg: Message) -> OnFindInterfaceAddrHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnFindInterfaceAddrParsedData(*msg.get_values())
        return OnFindInterfaceAddrHandlerResult(True, pd)
