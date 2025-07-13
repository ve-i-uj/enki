# """Интерфейсы отвечающие за сетевое взаимодейсвие."""

# import abc
# from typing import Generic, TypeVar

# from enki.msg.message import Message
# from enki.net.conninfo import ConnInfo

# from ..net.addr import Addr

# # import enum
# # from enum import Enum
# # class ChannelType(Enum):
# #     """"""
# #     TCP = enum.auto()
# #     UDP = enum.auto()
# #     BROADCAST = enum.auto()


# class IServerMsgSender(abc.ABC):
#     """Интерфейс отправителя сообщений на стороне серверного компонента."""

#     @abc.abstractmethod
#     async def send_msg(self, msg: Message, addr: Addr) -> bool:
#         """Отправить сообщение."""

#     @abc.abstractmethod
#     async def send_msg_content(self, data: bytes, addr: Addr) -> bool:
#         """Отправить сообщения без id и длины.

#         Принимающая сторона сама знает, какое сообщение ждать на конкретном
#         адресе.
#         """


# class IBackChannel(IServerMsgSender):
#     """Интерфейс канала обратной связи на полученное сообщение."""

#     @abc.abstractmethod
#     def get_connection_info(self) -> ConnInfo:
#         """Данные соединения."""

#     @abc.abstractmethod
#     async def close(self) -> None:
#         """Закрыть больше не нужное соединение."""

#     def __str__(self) -> str:
#         connection_info = self.get_connection_info()
#         return (
#             f"{self.__class__.__name__}("
#             f"{connection_info.client_addr.host}:{connection_info.client_addr.port} -> "
#             f"{connection_info.server_addr.host}:{connection_info.server_addr.port})"
#         )

#     __repr__ = __str__


# _C = TypeVar("_C", bound=IBackChannel)


# class IServerMsgReceiver(abc.ABC, Generic[_C]):
#     """Интерфейс приёма сообщений для серверного компонента.

#     Серверные компоненты могут отвечать на некоторые сообщения, поэтому у них
#     есть канал для обратной связи.
#     """

#     @abc.abstractmethod
#     def on_receive_msg(self, msg: Message, back_channel: _C) -> None:
#         """Колбэк на полученное сообщение.

#         Args:
#             msg (Message): полученное сервером сообщение
#             back_channel (IBackChannel): канал обратной связи

#         """


# class IClientMsgSender(abc.ABC):
#     """Интерфейс отправителя сообщений для клиентского подключения к компоненту."""

#     @abc.abstractmethod
#     async def send_msg(self, msg: Message) -> bool:
#         """Отправить сообщение компоненту KBEngine."""


# class IClientMsgReceiver(abc.ABC):
#     """Интерфейс получателя сообщений для клиентского подключения к компоненту.

#     Клиент не отвечает на сообщения (в отличии от сервера).
#     """

#     @abc.abstractmethod
#     def on_receive_msg(self, msg: Message) -> None:
#         """Колбэк на получение сообщения."""

#     @abc.abstractmethod
#     def on_end_receive_msg(self) -> None:
#         """Колбэк, что сообщения больше приходить не будут."""


# class IMsgProxyForwarder(abc.ABC):
#     """Интерфейс класса, имеющего сменный приёмник сообщений."""

#     @abc.abstractmethod
#     def set_msg_receiver(self, receiver: IClientMsgReceiver) -> None:
#         """Прописать получателя сообщений (приложение или команду, например)."""

#     @abc.abstractmethod
#     def _get_msg_receiver(self) -> IClientMsgReceiver:
#         """Возвращает получателя соощения."""


# class IComponentApp(abc.ABC):
#     """Интерфейс для приложения KBEngine-компонента."""
