"""Интерфейсы отвечающие за сетевое взаимодейсвие."""

import abc
from typing import Generic, TypeVar

from enki.kbeenum import ComponentType
from enki.msg.message import Message
from enki.msg.msg_serializer import MessageSerializer
from enki.net.addr import Addr
from enki.net.conninfo import ConnInfo


class NoSerializerForComponentError(RuntimeError):
    """Исключение в случае, если для нужного компонента нет сериализатора."""


class IMsgSerializer(abc.ABC):
    """Интерфейс классов, которые умеют сериализовать сообщения."""

    @abc.abstractmethod
    def _get_serializer(self, component: ComponentType) -> MessageSerializer:
        """Возвращает сериализатор сообщения в зависимовсти от типа компонента.

        Args:
            component (ComponentType): тип компонента

        Raises:
            NoSerializerForComponentError: если для нужного компонента нет
                сериализатора

        Returns:
            MessageSerializer: сериализатор сообщений

        """


class IServerMsgSender(IMsgSerializer):
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


class IMsgBackChannel(IServerMsgSender):
    """Интерфейс канала обратной связи на полученное KBEngine-сообщение.

    Способ отправлять KBEngine-сообщения из вышестоящего слоя, обрабатывающего
    сообщения.
    """

    @property
    @abc.abstractmethod
    def conn_info(self) -> ConnInfo:
        """Данные соединения."""

    @abc.abstractmethod
    def close(self) -> None:
        """Закрыть канал обратной связи.

        После закрытия отправка сообщений будет невозможна.
        """

    def __str__(self) -> str:
        conn_info = self.conn_info
        return (
            f"{self.__class__.__name__}("
            f"{conn_info.client_addr.host}:{conn_info.client_addr.port} -> "
            f"{conn_info.server_addr.host}:{conn_info.server_addr.port})"
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


class IClientMsgSender(IMsgSerializer):
    """Интерфейс отправителя сообщений для клиентского подключения к компоненту."""

    @abc.abstractmethod
    async def send_msg(self, msg: Message) -> bool:
        """Отправить сообщение компоненту KBEngine.

        Args:
            msg (Message): отправляемое сообщение

        Returns:
            bool: флаг получилось отправить или нет сообщение

        """


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


class IMsgProxyForwarder(abc.ABC):
    """Интерфейс класса, имеющего сменный приёмник сообщений."""

    @abc.abstractmethod
    def set_msg_receiver(self, receiver: IClientMsgReceiver) -> None:
        """Прописать получателя сообщений (приложение или команду, например)."""

    @abc.abstractmethod
    def _get_msg_receiver(self) -> IClientMsgReceiver:
        """Возвращает получателя соощения."""
