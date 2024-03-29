"""This module contains base classes of server message handlers."""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any

from enki.core.enkitype import NoValue
from enki.core.enkitype import Result
from enki.core.message import Message


@dataclass
class ParsedMsgData:
    """Base class for a parsed message.

    Descendants of the class will have entity_id and message fields.
    """

    def asdict(self) -> dict[str, Any]:
        return {
            **dataclasses.asdict(self),
            **{'__' + a: getattr(self, a) for a in getattr(self, '__add_to_dict__', [])}
        }

    def values(self) -> tuple:
        return tuple(getattr(self, f.name) for f in dataclasses.fields(self))


@dataclass
class HandlerResult(Result):
    """Base class for the result of a handler."""
    success: bool
    result: ParsedMsgData  # data of parsed message
    msg_id: int = NoValue.NO_ID  # id of the message (521, 511 etc)
    text: str = ''  # error message if it was

    def asdict(self) -> dict[str, Any]:
        return {**dataclasses.asdict(self),
                'result': self.result.asdict()}


class Handler:

    def handle(self, msg: Message) -> HandlerResult:
        """Handle a message."""
        return HandlerResult(False, ParsedMsgData(), text='Not implemented')

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'

    __repr__ = __str__
