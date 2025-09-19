"""Форматеры информации о сообщении."""


from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from enki.msg.message import Message

logger = logging.getLogger(__name__)


def _print_end():
    return logger.info("\n\n*** ------------- ***\n")


class MsgInfoOutFormatter:
    """Класс отвечает за внешнее форматирование информации о сообщении."""

    def __init__(self) -> None:
        pass

    def format(self, msg: Message) -> None:
        pass
