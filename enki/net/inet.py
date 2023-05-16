"""Интерфейсы отвечающие за сетевое взаимодейсвие."""

import abc
from dataclasses import dataclass
from typing import Any, Optional

from enki.core.enkitype import AppAddr, Result
from enki.core.message import IMessage


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


class IDataSender(abc.ABC):
    """Интерфейс для отправителя сетевых данных."""

    @abc.abstractmethod
    def send(self, data: bytes) -> bool:
        """Отправить данные по сетевому подключению."""


class ITCPConnection(IDataSender, IClientDataReceiver):
    """Родительский класс для TCP соединения."""

    @property
    @abc.abstractmethod
    def connection_info(self) -> ConnectionInfo:
        """Данные соединения."""

    @abc.abstractmethod
    def on_end_receive_data(self):
        """Данных не будет после этого колбэка."""

    @property
    @abc.abstractmethod
    def is_alive(self) -> bool:
        pass


class IUDPConnection(IDataSender):
    """Класс для клиентского UDP соединения.

    Экземпляр класса можно только инициализировать и один раз отравить через
    него сообшение. В момент отправки делается попытка отправить данные
    на адрес. Так как гарантии доставки нет, то результат будет всегда
    положительным.
    """

    @property
    @abc.abstractmethod
    def connection_info(self) -> ConnectionInfo:
        """Данные соединения."""


class IMsgSender(abc.ABC):
    """Отправитель сообщений.

    Через него можно осуществить непосредственную обратную связь с компонентом,
    отправившим сообщение.
    """

    @abc.abstractmethod
    def send_msg(self, msg: IMessage) -> bool:
        pass

    @abc.abstractmethod
    def send_msg_content(self, msg: IMessage) -> bool:
        """
        Это отправка сообщения без id и длины.

        Принимающая сторона сама знает, какое сообщение ждать на конкретном
        адресе.
        """


class IClientMsgReceiver(abc.ABC):
    """Message receiver interface."""

    @abc.abstractmethod
    def on_receive_msg(self, msg: IMessage):
        """Получить сообщение."""
        pass

    @abc.abstractmethod
    def on_end_receive_msg(self):
        pass


class ITCPClient(IMsgSender, IClientDataReceiver):
    """
    Слой между сетевыми байтами данных по TCP и приложением, которое работает
    на сообщениях.

    Возвращается TCP сервером или может использоваться, как самостоятельный
    клиент.
    """

    @abc.abstractmethod
    def set_msg_receiver(self, receiver: IClientMsgReceiver) -> None:
        """Прописать получателя сообщений (приложение или команду, например)."""

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


class IUDPClient(IMsgSender):
    """Клиент для отправки сообщений по UDP."""


class IChannel(IMsgSender):

    @property
    @abc.abstractmethod
    def connection_info(self) -> ConnectionInfo:
        """Данные соединения."""


class IServerDataReceiver(abc.ABC):
    """Интерфейс клиента получателя сетевых данных."""

    @abc.abstractmethod
    def on_receive_data(self, data: memoryview, addr: str) -> None:
        """Обработчик сырых данных от компонента."""


class IServerMsgReceiver(abc.ABC):
    """Интерфейс для приёма сообщений серверным компонентом."""

    @abc.abstractmethod
    def on_receive_msg(self, msg: IMessage, channel: IChannel):
        pass


class IServer(abc.ABC):
    """Интерфейс сервера."""

    @abc.abstractmethod
    def start(self) -> Result:
        pass

    @abc.abstractmethod
    def stop(self):
        pass

    @property
    @abc.abstractmethod
    def is_alive(self) -> bool:
        pass


class IAppComponent(IServerMsgReceiver):

    @abc.abstractmethod
    def start(self) -> Result:
        pass

    @abc.abstractmethod
    def stop(self):
        pass
