"""This module contains handlers of server messages."""

import abc
import enum
from dataclasses import dataclass

from enki import interface


class MsgRoute(enum.Enum):
    """Type of server message.

    It's a plugin type.
    """
    SPACE_DATA = enum.auto()
    ENTITY = enum.auto()
    APP_RESPONSE = enum.auto()  # this type should be encapsulated in commands
    STREAM = enum.auto()
    SERVER_MANAGE = enum.auto()


@dataclass
class ParsedMsgData:
    pass


@dataclass
class HandlerResult:
    result: ParsedMsgData
    msg_route: MsgRoute
    msg_id: int


class IHandler(abc.ABC):
    """Message apphandler interface."""

    def handle(self, msg: interface.IMessage) -> HandlerResult:
        """Handle message."""
        pass
