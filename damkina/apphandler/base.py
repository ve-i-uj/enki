"""This module contains base classes of server message handlers."""

import abc
import enum
from dataclasses import dataclass

from enki import interface


class MsgRoute(enum.Enum):
    """Server message routes."""
    SPACE_DATA = enum.auto()
    ENTITY = enum.auto()
    APP_RESPONSE = enum.auto()  # this type should be encapsulated in commands
    STREAM = enum.auto()  # ??? system action: load file etc.
    SERVER_MANAGE = enum.auto()


@dataclass
class ParsedMsgData:
    """Base class for a parsed message.

    Descendants of the class will have entity_id and message fields.
    """
    pass


@dataclass
class HandlerResult:
    """Base class for the result of a handler."""
    result: ParsedMsgData  # data of parsed message
    msg_route: MsgRoute  # the message destination in the plugin
    msg_id: int  # id of the message (521, 511 etc)


class IHandler(abc.ABC):
    """Application message handler interface."""

    def handle(self, msg: interface.IMessage) -> HandlerResult:
        """Handle message."""
        pass
