"""This module contains base classes of server message handlers."""

import dataclasses
from dataclasses import dataclass
from typing import Any

from enki.core import kbeenum, kbemath
from enki.core import enkitype
from enki.core.enkitype import Result
from enki.core import msgspec
from enki.core.message import IMessage, Message

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
    def component_type(self) -> kbeenum.ComponentType:
        try:
            return kbeenum.ComponentType(self.componentType)
        except ValueError:
            return kbeenum.ComponentType.UNKNOWN_COMPONENT_TYPE

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
    def component_type(self) -> kbeenum.ComponentType:
        return kbeenum.ComponentType(self.componentType)

    __add_to_dict__ = [
        'component_type'
    ]
