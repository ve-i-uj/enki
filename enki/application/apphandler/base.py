"""This module contains base classes of server message handlers."""

import abc
from dataclasses import dataclass

from enki import interface

# TODO: [2022-08-23 12:04 burov_alexey@mail.ru]:
# Возможно, их стоит слить с интерфейсес приложения.


@dataclass
class ParsedMsgData:
    """Base class for a parsed message.

    Descendants of the class will have entity_id and message fields.
    """
    pass


@dataclass
class HandlerResult:
    """Base class for the result of a handler."""
    success: bool
    result: ParsedMsgData  # data of parsed message
    text: str  # error message if it was
    msg_id: int  # id of the message (521, 511 etc)


class IHandler(abc.ABC):
    """Application message handler interface."""

    @abc.abstractmethod
    def handle(self, msg: interface.IMessage) -> HandlerResult:
        """Handle message."""
        pass
