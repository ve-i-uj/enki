"""Выведение информации результата десериализации сообщений."""

import logging

from enki.msg.message import Message
from enki.msg.msg_descr import MsgId

logger = logging.getLogger(__name__)


class MsgInfoOuter:
    """Класс отвечает за внешнее форматирование информации о сообщении."""

    def __init__(self) -> None:
        pass

    def print_msg(self, msg: Message, show_fileds: bool) -> None:
        text = f"{msg}"
        logger.info(text)

    def print_msg_id(self, msg_id: MsgId) -> None:
        text = f"The message id is '{msg_id}'"
        logger.info(text)
