"""This module contains base classes of server message handlers."""

import dataclasses
from dataclasses import dataclass
from typing import Any

from enki.core import kbemath
from enki.core.kbeenum import ComponentState, ComponentType, ShutdownState
from enki.core import enkitype
from enki.core.enkitype import Result
from enki.core import msgspec
from enki.core.message import Message, Message

from ..base import ParsedMsgData, HandlerResult, Handler


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
