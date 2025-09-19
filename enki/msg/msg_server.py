"""Классы серверов для работы с сообщениями."""

import logging

from enki.kbeenum import ComponentType
from enki.misc import devonly
from enki.msg.imsg import (
    IMsgBackChannel,
    IServerMsgReceiver,
)
from enki.msg.message import Message
from enki.msg.msg_descr import CompenentMsgSpecs, ComponentMsgSpecById
from enki.msg.msg_serializer import MessageSerializer
from enki.msg.msg_utils import get_serializer
from enki.net.addr import Addr
from enki.net.conninfo import ConnInfo
from enki.net.inet import IServerDataReceiver
from enki.net.server import TCPBackChannel, TCPServer, UDPBackChannel, UDPServer

logger = logging.getLogger(__name__)


class ClosedMsgBackChannelError(Exception):
    """Используется уже закрытый канал обратной связи."""


class UDPMsgBackChannel(IMsgBackChannel):
    """Канал обратной связи для ответа на соощение.

    Способ отправлять KBEngine-сообщения через слой сообщений.
    """

    def __init__(self, back_channel: UDPBackChannel) -> None:
        """Конструктор канала обратной связи для ответа на соощение.

        Args:
            back_channel (UDPBackChannel): канал обратной связи

        """
        self._back_channel = back_channel

    @property
    def conn_info(self) -> ConnInfo:
        """Данные соединения."""
        return self._back_channel.connection_info

    async def send_msg(self, msg: Message) -> bool:
        """Отправить сообщение на компонент, с которого пришёл запрос..

        Args:
            msg (Message): сообщение для отправки на компонент

        Returns:
            bool: получилось или нет отправить сообщение

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        data = get_serializer(msg.component).serialize(msg)
        return await self._back_channel.send_data(data)

    async def send_msg_content(self, msg: Message) -> bool:
        """Отправить сообщения без id и длины на компонент, с которого запрос.

        Принимающая сторона сама знает, какое сообщение ждать на конкретном
        адресе.

        Args:
            msg (Message): KBEngine-сообщение, данные которого будут отправлены
            addr (Addr): адрес KBEngine-компонента

        Raises:
            ClosedMsgBackChannelError: если используется закрытое соединение

        Returns:
            bool: получилось или нет отправить сообщение

        """
        logger.debug("[%s] (%s) ", self, devonly.func_args_values())

        data = get_serializer(msg.component).serialize(msg, only_data=True)
        await self._back_channel.send_data(data)

        # Это UDP. Даже, если будет "ICMP Destination Unreachable (Port
        # Unreachable)", то об этом всё равно сложно узнать. Поэтому всегда
        # True.
        return True

    def close(self) -> None:
        """Закрыть канал обратной связи."""
        # Для UDP это не имеет смысла. Для поддержания интерфейса.


class UDPMsgServer(UDPServer, IServerDataReceiver[UDPBackChannel]):
    """UDP-сервер сериализующий KBEngine-сообщения.

    Слой между бинарным представлением сообщения и объектом сообщения.
    """

    def __init__(
        self,
        addr: Addr,
        server_component: ComponentType,
        msg_receiver: IServerMsgReceiver,
    ) -> None:
        """UDP-сервер десериализующий / сериализующий KBEngine-сообщения.

        Args:
            addr (ComponentAddr): адрес прослушивания
            server_component (ComponentType): тип **компонента, который
                обслуживает сервер**
            msg_receiver (IServerMsgReceiver): получатель десериализованного
                сообщения

        """
        super().__init__(addr)
        self._msg_receiver = msg_receiver
        self._serializer = get_serializer(server_component)

    def on_receive_client_data(
        self, data: memoryview, back_channel: UDPBackChannel
    ) -> bool:
        """Обработчик сырых данных от компонента.

        Args:
            data (memoryview): данные
            back_channel (UDPBackChannel): канал обратной связи

        Returns:
            bool: были ли обработаны данные

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        msg_back_channel = UDPMsgBackChannel(back_channel)

        while data:
            msg, data = self._serializer.deserialize(data)
            if msg is None:
                logger.warning(
                    "[%s] Got unreadable data. The data rejected", self
                )
                break

            logger.debug(
                '[%s] Message "%s" fields: %s', self, msg.id, msg.get_values()
            )
            self._msg_receiver.on_receive_msg(msg, msg_back_channel)

        return False

    def on_end_receive_client_data(self, conn_info: ConnInfo) -> None:  # noqa: ARG002, D102
        # Для UDP это лишено смысла, но добавлено для поддержания общего
        # интерфейса серверов сообщений
        logger.debug("[%s] %s", self, devonly.func_args_values())


class TCPMsgBackChannel(IMsgBackChannel):
    """Канал обратной связи по TCP для ответа на сообщение."""

    def __init__(
        self,
        conn_info: ConnInfo,
        tcp_back_channel: TCPBackChannel,
    ) -> None:
        """Конструктор канала обратной связи по TCP для ответа на соощение.

        Args:
            conn_info (ConnInfo): информация соединения
            tcp_back_channel (TCPBackChannel): канал обратной связи для данных

        """
        self._conn_info = conn_info
        self._tcp_back_channel = tcp_back_channel

    @property
    def conn_info(self) -> ConnInfo:
        """Данные соединения."""
        return self._conn_info

    async def send_msg(self, msg: Message) -> bool:
        """Отправить сообщение клиенту в его соединение.

        Args:
            msg (Message): ответное сообщение для отправки

        Raises:
            ClosedMsgBackChannelError: если используется закрытое соединение

        Returns:
            bool: получилось или нет отправить сообщение

        """
        logger.debug("[%s] %s ", self, devonly.func_args_values())

        if self._tcp_back_channel.is_closed:
            exc_text = "The channel has been closed"
            raise ClosedMsgBackChannelError(exc_text)

        # Отправка сообщения через канал обратной связи на тот же адрес
        data = get_serializer(msg.component).serialize(msg)
        success = await self._tcp_back_channel.send_data(data)
        logger.info(
            "[%s] The data was sent by the back channel (success = %s) ",
            self,
            success,
        )

        return success

    async def send_msg_content(self, msg: Message) -> bool:
        """Отправить сообщения без id и длины.

        Принимающая сторона сама знает, какое сообщение ждать на конкретном
        адресе.

        Args:
            msg (Message): KBEngine-сообщение, данные которого будут отправлены
            addr (Addr): адрес KBEngine-компонента

        Raises:
            ClosedMsgBackChannelError: если используется закрытое соединение

        Returns:
            bool: получилось или нет отправить сообщение

        """
        logger.debug("[%s] %s ", self, devonly.func_args_values())

        if self._tcp_back_channel.is_closed:
            exc_text = "The channel has been closed"
            raise ClosedMsgBackChannelError(exc_text)

        # Отправка сообщения через канал обратной связи на тот же адрес
        data = get_serializer(msg.component).serialize(msg, only_data=True)
        success = await self._tcp_back_channel.send_data(data)
        logger.debug(
            "[%s] The data was sent by the back channel (success = %s) ",
            self,
            success,
        )

        return success

    def close(self) -> None:
        """Закрыть канал обратной связи.

        После закрытия отправка сообщений будет невозможна.
        """
        self._tcp_back_channel.close()


class TCPMsgServer(TCPServer):
    """TCP-сервер для приёма сериализованных KBEngine-сообщений."""

    def __init__(
        self,
        addr: Addr,
        comp_msg_spec_by_id: ComponentMsgSpecById,
        msg_receiver: IServerMsgReceiver,
        comp_msg_specs: CompenentMsgSpecs,
    ) -> None:
        """TCP-сервер для приёма сериализованных KBEngine-сообщений.

        Слой между бинарным представлением сообщений и объектом сообщения.

        Args:
            addr (ComponentAddr): адрес прослушивания
            comp_msg_spec_by_id (ComponentMsgSpecById): маппинг id сообщения к
                описанию сообщения **компонента, который обслуживает сервер**
            msg_receiver (IServerMsgReceiver): получатель десериализованного
                сообщения
            comp_msg_specs (CompenentMsgSpecs): спецификации сообщений
                компонентов-получателей ответных сообщений

        """
        super().__init__(addr)

        self._serializer = MessageSerializer(comp_msg_spec_by_id)
        self._msg_receiver = msg_receiver
        self._comp_msg_specs = comp_msg_specs

    def on_receive_client_data(
        self, data: memoryview, back_channel: TCPBackChannel
    ) -> bool:
        """Обработчик данных из клиентского подключения компонента.

        Args:
            data (memoryview): данные
            back_channel (TCPBackChannel): канал обратной связи

        Returns:
            bool: были ли обработаны данные

        """
        logger.debug("[%s] Received data (%s)", self, data.obj)
        super().on_receive_client_data(data, back_channel)

        conn_info = ConnInfo(back_channel.connection_info.client_addr, self._addr)
        msg_back_channel = TCPMsgBackChannel(conn_info, back_channel)

        while data:
            msg, data = self._serializer.deserialize(data)
            if msg is None:
                logger.warning(
                    "[%s] Unreadable data received. Possibly long "
                    "message or invalid data. The data is not handled",
                    self,
                )
                return False

            logger.debug(
                '[%s] Message "%s" fields: %s', self, msg.id, msg.get_values()
            )
            self._msg_receiver.on_receive_msg(msg, msg_back_channel)

        # Объект канал обратной связи остаётся открытым. Он или закроется
        # вызывающим кодом или он закроется транспортной библиотекой при
        # закрытии клиентского подключения.

        logger.debug("[%s] The received data was handled ", self)
        return True

    def on_end_receive_client_data(self, conn_info: ConnInfo) -> None:  # noqa: ARG002
        """Колбэк на закрытие соединения клиентом.

        Args:
            conn_info (ConnInfo): соединение, которое закрылось

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
