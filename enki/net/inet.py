"""Интерфейсы отвечающие за сетевое взаимодейсвие."""

import abc
from dataclasses import dataclass
import enum
from typing import Any, Optional

from enki.core.enkitype import AppAddr, Result
from enki.core.message import Message


@dataclass
class ConnectionInfo:
    """Данные подключения."""

    """
    Сетевой адрес источника подключения.
    """
    src_addr: AppAddr

    """
    Сетевой адрес соединения, к которому подключились.
    Это адрес сервера, он есть всегда. Он задаётся в конструкторе и для
    серверного подключения, и для клиентского подключения.
    """
    dst_addr: AppAddr

    def __str__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'{self.src_addr.host}:{self.src_addr.port} -> '
            f'{self.dst_addr.host}:{self.dst_addr.port})'
        )

    __repr__ = __str__


class IClientDataReceiver(abc.ABC):
    """Интерфейс клиента получателя сетевых данных."""

    @abc.abstractmethod
    def on_receive_data(self, data: memoryview) -> None:
        """Обработчик сырых данных от компонента."""

    @abc.abstractmethod
    def on_end_receive_data(self):
        pass


class IDataSender(abc.ABC):
    """Интерфейс для отправителя сетевых данных."""

    @abc.abstractmethod
    async def send(self, data: bytes) -> bool:
        """Отправить данные по сетевому подключению."""


class IClientMsgSender(abc.ABC):
    """Отправитель сообщений клиента."""

    @abc.abstractmethod
    def send_msg(self, msg: Message) -> bool:
        pass


class IClientMsgReceiver(abc.ABC):
    """Message receiver interface."""

    @abc.abstractmethod
    def on_receive_msg(self, msg: Message):
        """Получить сообщение."""
        pass

    @abc.abstractmethod
    def on_end_receive_msg(self):
        pass


class IStartable(abc.ABC):

    @property
    @abc.abstractmethod
    def is_alive(self) -> bool:
        pass

    @abc.abstractmethod
    def start(self) -> Result:
        pass

    @abc.abstractmethod
    def stop(self) -> None:
        pass


class IMsgForwarder(abc.ABC):
    """
    Реализации этого интерфейса могут пересылать сообщение дальше в приёмщик
    сообщений (приложение, команду и т.д.).
    """

    @abc.abstractmethod
    def set_msg_receiver(self, receiver: IClientMsgReceiver) -> None:
        """Прописать получателя сообщений (приложение или команду, например)."""


class IUDPClient(IClientMsgSender):
    """Клиент для отправки сообщений по UDP."""


class ChannelType(enum.Enum):
    TCP = enum.auto()
    UDP = enum.auto()
    BROADCAST = enum.auto()


class IServerMsgSender(abc.ABC):
    """Отправитель сообщений на стороне серверного компонента."""

    @abc.abstractmethod
    async def send_msg(self, msg: Message, addr: AppAddr, channel_type: ChannelType) -> bool:
        pass

    @abc.abstractmethod
    async def send_msg_content(self, data: bytes, addr: AppAddr, channel_type: ChannelType) -> bool:
        """Отправить сообщения без id и длины.

        Принимающая сторона сама знает, какое сообщение ждать на конкретном
        адресе.
        """


class IChannel(IServerMsgSender):

    @property
    @abc.abstractmethod
    def type(self) -> ChannelType:
        """Тип канала (tcp, udp)."""

    @property
    @abc.abstractmethod
    def connection_info(self) -> ConnectionInfo:
        """Данные соединения."""

    @abc.abstractmethod
    async def close(self):
        """Закрыть больше не нужное соединение."""

    def __str__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'{self.connection_info.src_addr.host}:{self.connection_info.src_addr.port} -> '
            f'{self.connection_info.dst_addr.host}:{self.connection_info.dst_addr.port})'
        )

    __repr__ = __str__


class IServerDataReceiver(abc.ABC):
    """Интерфейс клиента получателя сетевых данных."""

    @abc.abstractmethod
    async def on_receive_data(self, data: memoryview, addr: AppAddr) -> None:
        """Обработчик сырых данных от компонента."""

    def on_stop_receive(self):
        pass


class IServerMsgReceiver(abc.ABC):
    """Интерфейс для приёма сообщений серверным компонентом."""

    @abc.abstractmethod
    async def on_receive_msg(self, msg: Message, channel: IChannel):
        pass
