"""Базовые классы парасеров KBEngine-сообщений.

Данные сообщения в слое компонента-приложения.
"""

from __future__ import annotations

import abc
import dataclasses
from dataclasses import dataclass
from typing import Any, ClassVar

from enki.kbetype.ikbetype import IKBEType  # noqa: TC001
from enki.misc.result import Result
from enki.msg.message import Message


@dataclass
class ParsedMsgData:
    """Родительский класс для данных распарсенного сообещения.

    Это представление данных KBEngine-сообщения в слое приложения.
    """

    def asdict(self) -> dict[str, Any]:
        """Возвращает данные в виде словаря + доп. атрибуты из __add_to_dict__.

        Returns:
            dict[str, Any]: словарь-представление распарсенных данных

        """
        return {
            **dataclasses.asdict(self),
            **{
                "__" + a: getattr(self, a) for a in getattr(self, "__add_to_dict__", [])
            },
        }

    def values(self) -> tuple[IKBEType, ...]:
        """Значения распарсенного сообщения в виде контежа.

        Returns:
            tuple[Any]: значения сообщения

        """
        return dataclasses.astuple(self)

    # Добавочные атрибуты в словаре-представлении распарсенных данных
    __add_to_dict__: ClassVar[tuple[Any]]


@dataclass
class MsgParserResult(Result):
    """Base class for the parser result."""

    success: bool
    result: ParsedMsgData | None  # data of parsed message
    msg_id: int = Message.NO_ID  # id of the message (521, 511 etc)
    text: str = ""  # error message if it was


class IMsgParser(abc.ABC):
    """Парсер данных KBEngine-сообщения."""

    @abc.abstractmethod
    def parse(self, msg: Message) -> MsgParserResult:
        """Распарсить сообщение.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            MsgResult: объект результата парсинга

        """
        return MsgParserResult(
            success=False,
            result=ParsedMsgData() or None,
            text=f"Not implemented ({self}, {msg})",
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    __repr__ = __str__
