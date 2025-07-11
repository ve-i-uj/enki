"""Классы серверов для работы с сообщениями."""

import logging
from typing import TypeAlias

from enki.kbeenum import ComponentType
from enki.misc import devonly
from enki.msg.imsg import IMsgBackChannel, IServerMsgReceiver
from enki.msg.message import Message
from enki.msg.msg_serializer import ComponentMsgSpecById, MessageSerializer
from enki.net.addr import Addr
from enki.net.client import TCPClient, UDPClient
from enki.net.conninfo import ConnInfo
from enki.net.server import TCPBackChannel, TCPServer, UDPServer

logger = logging.getLogger(__name__)


MessageSerializers: TypeAlias = dict[ComponentType, MessageSerializer]


class ClosedMsgBackChannelError(Exception):
    """Используется уже закрытый канал обратной связи."""


class UDPMsgBackChannel(IMsgBackChannel):
    """Канал обратной связи для ответа на соощение.

    Способ отправлять KBEngine-сообщения через слой сообщений.
    """

    def __init__(self, conn_info: ConnInfo, serializers: MessageSerializers) -> None:
        """Конструктор канала обратной связи для ответа на соощение.

        Args:
            conn_info (ConnInfo): информация соединения
            serializers (MessageSerializers): сериализаторы сообщений для
                разных компонентов

        """
        self._conn_info = conn_info
        self._serializers = serializers
        self._closed = False

    @property
    def conn_info(self) -> ConnInfo:
        """Данные соединения."""
        return self._conn_info

    def _get_serializer(self, component: ComponentType) -> MessageSerializer:
        """Возвращает сериализатор сообщения в зависимовсти от типа компонента.

        Args:
            component (ComponentType): тип компонента

        Returns:
            MessageSerializer: сериализатор сообщений

        """
        return self._serializers[component]

    async def send_msg(self, msg: Message, addr: Addr) -> bool:
        """Отправить сообщение по UDP-транспорту на заданный адрес.

        Args:
            msg (Message): сообщение для отправки на компонент
            addr (Addr): адрес KBEngine-компонента

        Raises:
            ClosedMsgBackChannelError: если используется закрытое соединение

        Returns:
            bool: получилось или нет отправить сообщение

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        if self._closed:
            exc_text = "The channel has been closed"
            raise ClosedMsgBackChannelError(exc_text)

        data = self._get_serializer(msg.component).serialize(msg)

        if addr.is_broadcast_ip:
            client = UDPClient(addr, broadcast=True)
            return await client.send_data(data)

        client = UDPClient(addr)
        return await client.send_data(data)

    async def send_msg_content(self, msg: Message, addr: Addr) -> bool:
        """Отправить сообщения по UDP-транспорту без id и длины.

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

        if self._closed:
            exc_text = "The channel has been closed"
            raise ClosedMsgBackChannelError(exc_text)

        data = self._get_serializer(msg.component).serialize(msg, only_data=True)

        if addr.is_broadcast_ip:
            client = UDPClient(addr, broadcast=True)
            return await client.send_data(data)

        client = UDPClient(addr)
        return await client.send_data(data)

    async def close(self) -> None:
        """Закрыть канал обратной связи."""
        self._closed = True


class UDPMsgServer(UDPServer):
    """Сервер принимает по UDP сериализованные сообщения."""

    def __init__(
        self,
        addr: Addr,
        comp_msg_spec_by_id: ComponentMsgSpecById,
        msg_receiver: IServerMsgReceiver,
        serializers: MessageSerializers,
    ) -> None:
        """UDP-сервер сериализующий KBEngine-сообщения.

        Слой между бинарным представлением сообщений и объектом сообщения.

        Args:
            addr (ComponentAddr): адрес прослушивания
            comp_msg_spec_by_id (ComponentMsgSpecById): маппинг id сообщения к
                описанию сообщения **компонента, который обслуживает сервер**
            msg_receiver (IServerMsgReceiver): получатель десериализованного
                сообщения
            serializers (MessageSerializers): сериализаторы сообщений для
                разных компонентов

        """
        super().__init__(addr)
        self._msg_receiver = msg_receiver
        self._serializer = MessageSerializer(comp_msg_spec_by_id)
        self._serializers = serializers

    def on_receive_data(self, data: memoryview, addr: Addr) -> None:
        """Колбэк на полученное сериализованное сообщение.

        Args:
            data (memoryview): данные сериализованного сообщения
            addr (ComponentAddr): адрес компонента отправителя

        """
        logger.debug("[%s] Received data (%s)", self, data.obj)
        super().on_receive_data(data, addr)

        conn_info = ConnInfo(addr, self._addr)
        back_channel = UDPMsgBackChannel(conn_info, self._serializers)

        while data:
            msg, data = self._serializer.deserialize(data)
            if msg is None:
                logger.warning("[%s] Got unreadable data. End receiving", self)
                break

            logger.debug(
                '[%s] Message "%s" fields: %s', self, msg.id, msg.get_values()
            )
            self._msg_receiver.on_receive_msg(msg, back_channel)


class TCPMsgBackChannel(IMsgBackChannel):
    """Канал обратной связи по TCP для ответа на сообщение."""

    def __init__(
        self,
        conn_info: ConnInfo,
        serializers: MessageSerializers,
        tcp_back_channel: TCPBackChannel,
    ) -> None:
        """Конструктор канала обратной связи по TCP для ответа на соощение.

        Args:
            conn_info (ConnInfo): информация соединения
            serializers (MessageSerializers): сериализаторы сообщений для
                разных компонентов
            tcp_back_channel (TCPBackChannel): канал обратной связи для данных

        """
        self._conn_info = conn_info
        self._serializers = serializers
        self._tcp_back_channel = tcp_back_channel
        self._closed = False

    @property
    def conn_info(self) -> ConnInfo:
        """Данные соединения."""
        return self._conn_info

    def _get_serializer(self, component: ComponentType) -> MessageSerializer:
        """Возвращает сериализатор сообщения в зависимовсти от типа компонента.

        Args:
            component (ComponentType): тип компонента

        Returns:
            MessageSerializer: сериализатор сообщений

        """
        return self._serializers[component]

    async def _send_msg_to_address(
        self, addr: Addr, msg: Message, *, only_data: bool = False
    ) -> bool:
        """Отправить KBEngine-сообщение на TCP адрес."""  # noqa: DOC201
        client = TCPClient(addr)
        res = await client.start()
        if not res.success:
            logger.warning(
                "[%s] The message cannot be sent. Reason: '%s' (msg = '%s')",
                self,
                res.text,
                msg,
            )
            return False

        data = self._get_serializer(msg.component).serialize(msg, only_data=only_data)

        sent = await client.send_data(data)
        if not sent:
            logger.warning("The message is not sent (msg = '%s')", msg)
            return False

        logger.info(
            "[%s] The message was sent to the adddress '%s' (msg = '%s')",
            self,
            addr,
            msg,
        )
        return True

    async def send_msg(self, msg: Message, addr: Addr) -> bool:
        """Отправить сообщение.

        Args:
            msg (Message): сообщение для отправки на компонент
            addr (Addr): адрес KBEngine-компонента

        Raises:
            ClosedMsgBackChannelError: если используется закрытое соединение

        Returns:
            bool: получилось или нет отправить сообщение

        """
        logger.debug("[%s] %s ", self, devonly.func_args_values())

        if self._closed:
            exc_text = "The channel has been closed"
            raise ClosedMsgBackChannelError(exc_text)

        if addr != self.conn_info.client_addr:
            logger.info(
                "[%s] The response address and the back channel adress are not "
                "equal (addr = '%s', back channel addr = '%s')",
                self,
                addr,
                self.conn_info.client_addr,
            )
            return await self._send_msg_to_address(addr, msg)

        # Отправка сообщения через канал обратной связи на тот же адрес
        data = self._get_serializer(msg.component).serialize(msg)
        success = await self._tcp_back_channel.send_data(data)
        logger.info(
            "[%s] The data was sent by the back channel (success = %s) ",
            self,
            success,
        )

        return success

    async def send_msg_content(self, msg: Message, addr: Addr) -> bool:
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

        if self._closed:
            exc_text = "The channel has been closed"
            raise ClosedMsgBackChannelError(exc_text)

        if addr != self.conn_info.client_addr:
            logger.info(
                "[%s] The response address and the back channel adress are not "
                "equal (addr = '%s', back channel addr = '%s')",
                self,
                addr,
                self.conn_info.client_addr,
            )
            return await self._send_msg_to_address(addr, msg, only_data=True)

        # Отправка сообщения через канал обратной связи на тот же адрес
        data = self._get_serializer(msg.component).serialize(msg, only_data=True)
        success = await self._tcp_back_channel.send_data(data)
        logger.info(
            "[%s] The data was sent by the back channel (success = %s) ",
            self,
            success,
        )

        return success

    async def close(self) -> None:
        """Закрыть канал обратной связи.

        После закрытия отправка сообщений будет невозможна.
        """


class TCPMsgServer(TCPServer):
    """TCP-сервер для приёма сериализованных KBEngine-сообщений."""

    def __init__(
        self,
        addr: Addr,
        comp_msg_spec_by_id: ComponentMsgSpecById,
        msg_receiver: IServerMsgReceiver,
        serializers: MessageSerializers,
    ) -> None:
        """TCP-сервер для приёма сериализованных KBEngine-сообщений.

        Слой между бинарным представлением сообщений и объектом сообщения.

        Args:
            addr (ComponentAddr): адрес прослушивания
            comp_msg_spec_by_id (ComponentMsgSpecById): маппинг id сообщения к
                описанию сообщения **компонента, который обслуживает сервер**
            msg_receiver (IServerMsgReceiver): получатель десериализованного
                сообщения
            serializers (MessageSerializers): сериализаторы сообщений для
                разных компонентов

        """
        super().__init__(addr)

        self._serializer = MessageSerializer(comp_msg_spec_by_id)
        self._msg_receiver = msg_receiver
        self._serializers = serializers

    def on_receive_data(
        self, data: memoryview, back_channel: TCPBackChannel
    ) -> bool:
        """Обработчик сырых данных от компонента.

        Args:
            data (memoryview): данные
            back_channel (ITCPBackChannel): канал обратной связи

        Returns:
            bool: были ли обработаны данные

        """
        logger.debug("[%s] Received data (%s)", self, data.obj)
        super().on_receive_data(data, back_channel)

        conn_info = ConnInfo(back_channel.connection_info.client_addr, self._addr)
        msg_back_channel = TCPMsgBackChannel(
            conn_info, self._serializers, back_channel
        )

        while data:
            msg, data = self._serializer.deserialize(data)
            if msg is None:
                logger.warning("[%s] Got unreadable data. End receiving", self)
                return False

            logger.debug(
                '[%s] Message "%s" fields: %s', self, msg.id, msg.get_values()
            )
            self._msg_receiver.on_receive_msg(msg, msg_back_channel)

        logger.debug("[%s] The received data was handled ", self)
        return True
