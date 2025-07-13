"""Внешний интерфейс пакета."""

import abc

from .message import Message

# TODO: [burov_alexey@mail.ru 06.07.2025 08:11]
# Ну это точно не относится к сообщению. Это уже кто и как работать будет



class IServerMsgSender(abc.ABC):
    """Интерфейс отправителя сообщений на стороне серверного компонента."""

    @abc.abstractmethod
    async def send_msg(
        self, msg: Message, addr: AppAddr, channel_type: ChannelType
    ) -> bool:
        """Отправить сообщение """

    @abc.abstractmethod
    async def send_msg_content(
        self, data: bytes, addr: AppAddr, channel_type: ChannelType
    ) -> bool:
        """Отправить сообщения без id и длины.

        Принимающая сторона сама знает, какое сообщение ждать на конкретном
        адресе.
        """


class IChannel(IServerMsgSender):
    """Интерфейс канала обратной связи серверного компонента."""

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
            f"{self.__class__.__name__}("
            f"{self.connection_info.src_addr.host}:{self.connection_info.src_addr.port} -> "
            f"{self.connection_info.dst_addr.host}:{self.connection_info.dst_addr.port})"
        )

    __repr__ = __str__


class IServerMsgReceiver(abc.ABC):
    """Интерфейс приёма сообщений серверным компонентом.

    Серверные компоненты могут отвечать на некоторые сообщения, поэтому у них
    есть канал для обратной связи.
    """

    @abc.abstractmethod
    async def on_receive_msg(self, msg: Message, channel: IChannel):
        pass
