"""This module contains base classes of server message handlers."""

import abc
from dataclasses import dataclass

from enki.interface import IMessage, IResult
from enki import settings

# TODO: [2022-08-23 12:04 burov_alexey@mail.ru]:
# Возможно, их стоит слить с интерфейсес приложения.


@dataclass
class ParsedMsgData:
    """Base class for a parsed message.

    Descendants of the class will have entity_id and message fields.
    """
    pass


@dataclass
class HandlerResult(IResult):
    """Base class for the result of a handler."""
    success: bool
    result: ParsedMsgData  # data of parsed message
    msg_id: int = settings.NO_ID  # id of the message (521, 511 etc)
    text: str = ''  # error message if it was


class IHandler(abc.ABC):
    """Application message handler interface."""

    @abc.abstractmethod
    def handle(self, msg: IMessage) -> HandlerResult:
        """Handle message."""
        pass
