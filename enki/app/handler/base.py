"""This module contains base classes of server message handlers."""

import dataclasses
from dataclasses import dataclass
from typing import Any

from enki import settings
from enki.enkitype import Result
from enki.net.kbeclient.message import IMessage


@dataclass
class ParsedMsgData:
    """Base class for a parsed message.

    Descendants of the class will have entity_id and message fields.
    """
    pass

    def asdict(self) -> dict[str, Any]:
        return {**dataclasses.asdict(self),
                **{'__' + a: getattr(self, a) for a in getattr(self, '__add_to_dict__', [])}}


@dataclass
class HandlerResult(Result):
    """Base class for the result of a handler."""
    success: bool
    result: ParsedMsgData  # data of parsed message
    msg_id: int = settings.NO_ID  # id of the message (521, 511 etc)
    text: str = ''  # error message if it was

    def asdict(self) -> dict[str, Any]:
        return {**dataclasses.asdict(self),
                'result': self.result.asdict()}


class Handler:

    def handle(self, msg: IMessage) -> HandlerResult:
        """Handle a message."""
        return HandlerResult(False, ParsedMsgData(), text='Not implemented')
