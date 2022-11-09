"""This module contains base classes of server message handlers."""

from dataclasses import dataclass

from enki import settings
from enki.enkitype import Result
from enki.net.kbeclient.message import IMessage


@dataclass
class ParsedMsgData:
    """Base class for a parsed message.

    Descendants of the class will have entity_id and message fields.
    """
    pass


@dataclass
class HandlerResult(Result):
    """Base class for the result of a handler."""
    success: bool
    result: ParsedMsgData  # data of parsed message
    msg_id: int = settings.NO_ID  # id of the message (521, 511 etc)
    text: str = ''  # error message if it was


class Handler:

    def handle(self, msg: IMessage) -> HandlerResult:
        """Handle a message."""
        return HandlerResult(False, ParsedMsgData(), text='Not implemented')
