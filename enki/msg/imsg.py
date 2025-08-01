"""Интерфейсы отвечающие за сетевое взаимодейсвие."""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Generic, Self, TypeVar

if TYPE_CHECKING:
    from enki.msg.message import Message
    from enki.net.addr import Addr
    from enki.net.conninfo import ConnInfo


# TODO: [2025-08-01 08:25 burov_alexey@mail.ru]:
# Неиспользуется похоже
class IServerMsgSender:
    """Интерфейс отправителя сообщений на стороне серверного компонента."""

    @abc.abstractmethod
    async def send_msg(self, msg: Message, addr: Addr) -> bool:
        """Отправить сообщение.

        Args:
            msg (Message): сообщение для отправки на компонент
            addr (Addr): адрес KBEngine-компонента

        Returns:
            bool: получилось или нет отправить сообщение

        """

    @abc.abstractmethod
    async def send_msg_content(self, msg: Message, addr: Addr) -> bool:
        """Отправить сообщения без id и длины.

        Принимающая сторона сама знает, какое сообщение ждать на конкретном
        адресе.

        Args:
            msg (Message): KBEngine-сообщение, данные которого будут отправлены
            addr (Addr): адрес KBEngine-компонента

        Returns:
            bool: получилось или нет отправить сообщение

        """


class IClientMsgSender:
    """Интерфейс отправителя сообщений компоненту для клиентского подключения."""

    @abc.abstractmethod
    async def send_msg(self, msg: Message) -> bool:
        """Отправить сообщение компоненту KBEngine.

        Args:
            msg (Message): отправляемое сообщение

        Returns:
            bool: флаг получилось отправить или нет сообщение

        """

    @abc.abstractmethod
    async def send_msg_content(self, msg: Message) -> bool:
        """Отправить сообщения без id и длины на компонент, с которого запрос.

        Принимающая сторона сама знает, какое сообщение ждать на конкретном
        адресе.

        Args:
            msg (Message): KBEngine-сообщение, данные которого будут отправлены

        Returns:
            bool: получилось или нет отправить сообщение

        """


class IMsgBackChannel(IClientMsgSender):
    """Интерфейс канала обратной связи на полученное KBEngine-сообщение.

    Способ отправлять KBEngine-сообщения из вышестоящего слоя, обрабатывающего
    сообщения.
    """

    @property
    @abc.abstractmethod
    def conn_info(self) -> ConnInfo:
        """Данные соединения."""

    @abc.abstractmethod
    async def send_msg(self, msg: Message) -> bool:
        """Отправить сообщение на компонент, с которого пришёл запрос..

        Args:
            msg (Message): сообщение для отправки на компонент

        Returns:
            bool: получилось или нет отправить сообщение

        """

    @abc.abstractmethod
    async def send_msg_content(self, msg: Message) -> bool:
        """Отправить сообщения без id и длины на компонент, с которого запрос.

        Принимающая сторона сама знает, какое сообщение ждать на конкретном
        адресе.

        Args:
            msg (Message): KBEngine-сообщение, данные которого будут отправлены

        Returns:
            bool: получилось или нет отправить сообщение

        """

    @abc.abstractmethod
    def close(self) -> None:
        """Закрыть канал обратной связи.

        После закрытия отправка сообщений будет невозможна.
        """

    def __str__(self) -> str:
        conn_info = self.conn_info
        return (
            f"{self.__class__.__name__}("
            f"{conn_info.client_addr.ip_addr}:{conn_info.client_addr.port} -> "
            f"{conn_info.server_addr.ip_addr}:{conn_info.server_addr.port})"
        )

    __repr__ = __str__


_C = TypeVar("_C", bound=IMsgBackChannel)


class IServerMsgReceiver(abc.ABC, Generic[_C]):
    """Интерфейс приёма сообщений для серверного компонента.

    Серверные компоненты могут отвечать на некоторые сообщения, поэтому у них
    есть канал для обратной связи.
    """

    @abc.abstractmethod
    def on_receive_msg(self, msg: Message, back_channel: _C) -> None:
        """Колбэк на полученное сообщение.

        Args:
            msg (Message): полученное сервером сообщение
            back_channel (IMsgBackChannel): канал обратной связи

        """


# TODO: [2025-07-26 12:05 burov_alexey@mail.ru]:
# Скорей всего не используется. Может только в плагине клиентском.
class IClientMsgReceiver(abc.ABC):
    """Интерфейс получателя сообщений для клиентского подключения к компоненту.

    Клиент не отвечает на сообщения (в отличии от сервера).
    """

    @abc.abstractmethod
    def on_receive_msg(self, msg: Message) -> None:
        """Колбэк на получение сообщения."""

    @abc.abstractmethod
    def on_end_receive_msg(self) -> None:
        """Колбэк, что сообщения больше приходить не будут."""


class IMsgResponseAwaitable(abc.ABC):
    """Интерфейс для классов, ожидающих ответа на сообщение."""

    @abc.abstractmethod
    def wait_and_iterate_resp_msgs(self, timeout: float) -> Self:
        """Возвращает итератор с таймаутом ожидания ответа на сообщение.

        Может быть несколько сообщений в ответ или несколько чанков ответов,
        завёрнутых в сообщения (т.к. это клиент слоя сообщений, то и возвращает
        он даже чанки в виде сообщений).

        Args:
            timeout (float, optional): время ожидания ответа

        Returns:
            Self: итератор ответных сообщений

        """

    @abc.abstractmethod
    def __aiter__(self) -> Self:
        pass

    @abc.abstractmethod
    async def __anext__(self) -> Message:
        pass

    async def wait_only_first_resp_msg(self, timeout: float) -> Message | None:
        """Ожидает и возвращает только первый ответ (None, если не было ответа).

        Args:
            timeout (float): ожидание ответа

        Returns:
            Message | None: первое ответное сообщение (None, если не было ответа)

        """
        res: Message | None = None
        async for resp_msg in self.wait_and_iterate_resp_msgs(timeout):
            res = resp_msg
            break

        return res
