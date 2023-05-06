"""Обработчик сообщений от компонента DBMgr."""

import logging
from dataclasses import dataclass

from enki import enkitype, kbeenum, kbemath
from enki.net import msgspec
from enki.net.kbeclient import Message
from enki.misc import devonly

from . import base

logger = logging.getLogger(__file__)


@dataclass
class OnRegisterNewAppParsedData(base.ParsedMsgData):
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
        'component_type', 'internal_address','external_address'
    ]


@dataclass
class OnRegisterNewAppHandlerResult(base.HandlerResult):
    """Обработчик для DBMgr::onRegisterNewApp."""
    success: bool
    result: OnRegisterNewAppParsedData
    msg_id: int = msgspec.app.dbmgr.onRegisterNewApp.id
    text: str = ''


class OnRegisterNewAppHandler(base.Handler):

    def handle(self, msg: Message) -> OnRegisterNewAppHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnRegisterNewAppParsedData(*msg.get_values())
        return OnRegisterNewAppHandlerResult(True, pd)


@dataclass
class OnAppActiveTickParsedData(base.ParsedMsgData):
    componentType: int
    componentID: int

    @property
    def component_type(self) -> kbeenum.ComponentType:
        return kbeenum.ComponentType(self.componentType)

    __add_to_dict__ = [
        'component_type'
    ]


@dataclass
class OnAppActiveTickHandlerResult(base.HandlerResult):
    """Обработчик для DBMgr::onAppActiveTick."""
    success: bool
    result: OnAppActiveTickParsedData
    msg_id: int = msgspec.app.dbmgr.onAppActiveTick.id
    text: str = ''


class OnAppActiveTickHandler(base.Handler):

    def handle(self, msg: Message) -> OnAppActiveTickHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnAppActiveTickParsedData(*msg.get_values())
        return OnAppActiveTickHandlerResult(True, pd)
