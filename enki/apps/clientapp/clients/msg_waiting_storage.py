"""Модуль с общими классами для ожидания ответных сообщений.

Используется клиентами Loginapp и Baseapp для отправки сообщений
и ожидания ответов с таймаутами.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from asyncio import Future

    from enki.msg.message import Message
    from enki.msg.msg_descr import MsgId


WaitingRespTimeout: TypeAlias = float
WAIT_FOREVER = WaitingRespTimeout(sys.maxsize)


@dataclass
class WaitingRespMsgData:
    """Данные сообщения, ожидающего ответа."""

    msg: Message
    resp_msgs: list[MsgId]
    timeout: WaitingRespTimeout
    future: Future[Message]


class WaitingRespMsgStorage:
    """Хранилище сообщений, ожидающих ответа.

    Позволяет добавлять ожидающие сообщения и получать их по id ответного
    сообщения.
    """

    def __init__(self) -> None:
        self._waiting_resp_msgs: list[WaitingRespMsgData] = []

    @property
    def is_empty(self) -> bool:
        """Флаг того, что очередь пустая."""
        return len(self._waiting_resp_msgs) == 0

    def get_all(self) -> list[WaitingRespMsgData]:
        """Возвращает копию всех ожидающих сообщений.

        Returns:
            list[WaitingRespMsgData]: список ожидающих сообщений

        """
        return self._waiting_resp_msgs[:]

    def add_waiting_obj(self, waiting_resp_obj: WaitingRespMsgData) -> None:
        """Добавить ожидающее сообщение в хранилище.

        Args:
            waiting_resp_obj (WaitingRespMsgData): объект с данными
                ожидающего сообщения

        """
        self._waiting_resp_msgs.append(waiting_resp_obj)

    def pop_waiting_obj(self, resp_msg_id: MsgId) -> WaitingRespMsgData | None:
        """Найти и удалить ожидающее сообщение по id ответа.

        Args:
            resp_msg_id (int): id ответного сообщения

        Returns:
            WaitingRespMsgData | None: найденный объект или None

        """
        obj_for_deleting = None
        i_for_deleting = None
        for i, obj in enumerate(self._waiting_resp_msgs):
            if resp_msg_id in obj.resp_msgs:
                obj_for_deleting = obj
                i_for_deleting = i
                break

        if i_for_deleting is not None:
            del self._waiting_resp_msgs[i_for_deleting]
            assert obj_for_deleting is not None
            return obj_for_deleting

        return None
