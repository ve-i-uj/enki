"""Базовые классы для обработчиков KBEngine-сообщений."""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any

from enki.core.message import Message  # noqa: TC001
from enki.core.novalue import NoValue
from enki.misc.result import Result


@dataclass
class ParsedMsgData:
    """Base class for a parsed message."""

    # TODO: [burov_alexey@mail.ru 02.07.2025 11:30]
    # Насколько помню это к форматированию под утилиту добавлял. Надо код
    # утилиты держать в утилите.
    def asdict(self) -> dict[str, Any]:
        return {
            **dataclasses.asdict(self),
            **{
                "__" + a: getattr(self, a)
                for a in getattr(self, "__add_to_dict__", [])
            },
        }

    def values(self) -> tuple:
        return tuple(getattr(self, f.name) for f in dataclasses.fields(self))


@dataclass
class HandlerResult(Result):
    """Base class for the result of a handler."""

    success: bool
    result: ParsedMsgData  # data of parsed message
    msg_id: int = NoValue.NO_ID  # id of the message (521, 511 etc)
    text: str = ""  # error message if it was

    def asdict(self) -> dict[str, Any]:
        return {**dataclasses.asdict(self), "result": self.result.asdict()}


class Handler:
    """Обработчик сообщения от компонента."""

    def handle(self, msg: Message) -> HandlerResult:
        """Handle a message."""
        return HandlerResult(False, ParsedMsgData(), text="Not implemented")

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    __repr__ = __str__
