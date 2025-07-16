"""Интерфесы пакета."""

import abc
from typing import Generic, TypeVar

from enki.net.addr import Addr
from enki.net.conninfo import ConnInfo


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
    def on_receive_data(self, data: memoryview, addr: Addr) -> None:
        """Обработчик сырых данных от компонента.

        Args:
            data (memoryview): данные
            addr (ComponentAddr): адрес компонента, отправившего данные

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
