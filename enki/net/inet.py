"""Интерфесы пакета."""

from __future__ import annotations

import abc
from typing import Generic, Self, TypeVar

from enki.misc.result import Result  # noqa: TC001
from enki.net.conninfo import ConnInfo  # noqa: TC001


class IClientDataReceiver(abc.ABC):
    """Интерфейс клиента получателя данных."""

    @abc.abstractmethod
    def on_receive_data(self, data: bytes) -> None:
        """Колбэк на получение сырых данных от компонента."""

    @abc.abstractmethod
    def on_end_receive_data(self) -> None:
        """Колбэк окончания передачи данных от транспортной библиотеки."""


class IClientDataSender(abc.ABC):
    """Интерфейс для отправителя сетевых данных."""

    @abc.abstractmethod
    async def send_data(self, data: bytes) -> bool:
        """Отправить данные по сетевому подключению."""


class IServerDataSender(abc.ABC):
    """Интерфейс для отправителя сетевых данных."""

    @abc.abstractmethod
    async def send_data(self, data: bytes) -> bool:
        """Отправить данные по сетевому подключению."""


class IUDPServerDataReceiver(abc.ABC):
    """Интерфейс UDP-сервера получателя сетевых данных."""

    @abc.abstractmethod
    def on_receive_data(self, data: memoryview, addr: tuple[str, int]) -> None:
        """Обработчик сырых данных от компонента.

        Args:
            data (memoryview): данные
            addr (tuple[str, int]r): адрес компонента, отправившего данные

        """

    @abc.abstractmethod
    def on_stop_receive_data(self) -> None:
        """Колбэк на остановку получения данных.

        Может вызываться нескоьлко раз. Вызов делается со стороны транспортного
        слоя.
        """


class ITCPBackChannel(IServerDataSender):
    """Интерфейс канал обратной связи по TCP-данных."""

    @property
    @abc.abstractmethod
    def connection_info(self) -> ConnInfo:
        """Информация о подключении."""

    @abc.abstractmethod
    async def send_data(self, data: bytes) -> bool:
        """Отправить данные по сетевому подключению.

        Args:
            data (bytes): данные для отправки

        Returns:
            bool: флаг получилось ли отправить данные

        """

    @abc.abstractmethod
    def close(self) -> None:
        """Закрыть канал обратной связи."""

    def __str__(self) -> str:
        conn_info = self.connection_info
        return (
            f"{self.__class__.__name__}("
            f"{conn_info.client_addr.host}:{conn_info.client_addr.port} -> "
            f"{conn_info.server_addr.host}:{conn_info.server_addr.port})"
        )

    __repr__ = __str__


_C = TypeVar("_C", bound=ITCPBackChannel)


class ITCPServerDataReceiver(abc.ABC, Generic[_C]):
    """Интерфейс TCP-сервера получателя сетевых данных."""

    @abc.abstractmethod
    def on_receive_client_data(self, data: memoryview, back_channel: _C) -> bool:
        """Обработчик сырых данных от компонента.

        Args:
            data (memoryview): данные
            back_channel (_C): канал обратной связи

        Returns:
            bool: были ли обработаны данные

        """

    @abc.abstractmethod
    def on_end_receive_client_data(self, conn_info: ConnInfo) -> None:
        """Колбэк на закрытие соединения клиентом.

        Может вызываться несколько раз.

        Args:
            conn_info (ConnInfo): соединение, которое закрылось

        """


class IResponseAwaitable(abc.ABC):
    """Интерфейс объекта ожидающего ответа на запрос."""

    @abc.abstractmethod
    def wait_and_iterate_responses(self, timeout: float) -> Self:
        """Возвращает итератор данных от сервера с таймаутом ожидания.

        Args:
            timeout (float, optional): время ожидания ответа

        Returns:
            Self: итератор данных от сервера

        """

    @abc.abstractmethod
    def need_resp_waiting(self) -> bool:
        """Hужно ли ждать ответы.

        Returns:
            bool: флаг того, нужно ли ждать ответы

        """

    @abc.abstractmethod
    def __aiter__(self) -> Self:
        pass

    @abc.abstractmethod
    async def __anext__(self) -> bytes:
        pass


class IConnectableClient(abc.ABC):
    """Интерфейс для подключаемых объектов."""

    @property
    @abc.abstractmethod
    def is_connected(self) -> bool:
        """Флаг подключен ли экземпляр.

        Returns:
            bool: флаг подключен ли клиент

        """

    @abc.abstractmethod
    async def connect(self) -> Result:
        """Подключить объект.

        Returns:
            Result: результат подлючения клиента

        """

    @abc.abstractmethod
    def disconnect(self) -> None:
        """Отключить объект."""
