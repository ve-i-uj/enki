"""Классы серверов для работы с сообщениями."""

import logging

from enki.kbeenum import ComponentType
from enki.misc import devonly
from enki.msg.imsg import (
    IMsgBackChannel,
    IServerMsgReceiver,
    NoSerializerForComponentError,
)
from enki.msg.message import Message
from enki.msg.msg_descr import CompenentMsgSpecs, ComponentMsgSpecById
from enki.msg.msg_serializer import MessageSerializer
from enki.net.addr import Addr
from enki.net.client import TCPClient, UDPClient
from enki.net.conninfo import ConnInfo
from enki.net.server import TCPBackChannel, TCPServer, UDPServer

logger = logging.getLogger(__name__)


class ClosedMsgBackChannelError(Exception):
    """Используется уже закрытый канал обратной связи."""


class UDPMsgBackChannel(IMsgBackChannel):
    """Канал обратной связи для ответа на соощение.

    Способ отправлять KBEngine-сообщения через слой сообщений.
    """

    def __init__(self, conn_info: ConnInfo, comp_msg_specs: CompenentMsgSpecs) -> None:
        """Конструктор канала обратной связи для ответа на соощение.

        Args:
            conn_info (ConnInfo): информация соединения
            comp_msg_specs (CompenentMsgSpecs): спецификации сообщений
                компонентов-получателей

        """
        self._conn_info = conn_info
        self._comp_msg_specs = comp_msg_specs

    @property
    def conn_info(self) -> ConnInfo:
        """Данные соединения."""
        return self._conn_info

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
        if component not in self._comp_msg_specs:
            err_msg = f"There is no serializator for the component '{component.name}'"
            logger.error("%s (Logic error)", err_msg)
            raise NoSerializerForComponentError(err_msg)

        comp_msg_spec = self._comp_msg_specs[component]
        return MessageSerializer(comp_msg_spec)

    async def send_msg(self, msg: Message, addr: Addr) -> bool:
        """Отправить сообщение по UDP-транспорту на заданный адрес.

        Args:
            msg (Message): сообщение для отправки на компонент
            addr (Addr): адрес KBEngine-компонента

        Returns:
            bool: получилось или нет отправить сообщение

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

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

        data = self._get_serializer(msg.component).serialize(msg, only_data=True)

        if addr.is_broadcast_ip:
            client = UDPClient(addr, broadcast=True)
            return await client.send_data(data)

        client = UDPClient(addr)
        return await client.send_data(data)

    def close(self) -> None:
        """Закрыть канал обратной связи."""
        # Для UDP это не имеет смысла


class UDPMsgServer(UDPServer):
    """UDP-сервер сериализующий KBEngine-сообщения.

    Слой между бинарным представлением сообщения и объектом сообщения.
    """

    def __init__(
        self,
        addr: Addr,
        comp_msg_spec_by_id: ComponentMsgSpecById,
        msg_receiver: IServerMsgReceiver,
        comp_msg_specs: CompenentMsgSpecs,
    ) -> None:
        """UDP-сервер десериализующий / сериализующий KBEngine-сообщения.

        Args:
            addr (ComponentAddr): адрес прослушивания
            comp_msg_spec_by_id (ComponentMsgSpecById): маппинг id сообщения к
                описанию сообщения **компонента, который обслуживает сервер**
            msg_receiver (IServerMsgReceiver): получатель десериализованного
                сообщения
            comp_msg_specs (CompenentMsgSpecs): спецификации сообщений
                компонентов-получателей

        """
        super().__init__(addr)
        self._msg_receiver = msg_receiver
        self._serializer = MessageSerializer(comp_msg_spec_by_id)
        self._comp_msg_specs = comp_msg_specs

    def on_receive_data(self, data: memoryview, addr: Addr) -> None:
        """Колбэк на полученное сериализованное сообщение.

        Args:
            data (memoryview): данные сериализованного сообщения
            addr (ComponentAddr): адрес компонента отправителя

        """
        logger.debug("[%s] Received data (%s)", self, data.obj)
        super().on_receive_data(data, addr)

        conn_info = ConnInfo(addr, self._addr)
        back_channel = UDPMsgBackChannel(conn_info, self._comp_msg_specs)

        while data:
            msg, data = self._serializer.deserialize(data)
            if msg is None:
                logger.warning("[%s] Got unreadable data. The data rejected", self)
                break

            logger.debug('[%s] Message "%s" fields: %s', self, msg.id, msg.get_values())
            self._msg_receiver.on_receive_msg(msg, back_channel)


class TCPMsgBackChannel(IMsgBackChannel):
    """Канал обратной связи по TCP для ответа на сообщение."""

    def __init__(
        self,
        conn_info: ConnInfo,
        comp_msg_specs: CompenentMsgSpecs,
        tcp_back_channel: TCPBackChannel,
    ) -> None:
        """Конструктор канала обратной связи по TCP для ответа на соощение.

        Args:
            conn_info (ConnInfo): информация соединения
            comp_msg_specs (CompenentMsgSpecs): спецификации сообщений
                компонентов-получателей
            tcp_back_channel (TCPBackChannel): канал обратной связи для данных

        """
        self._conn_info = conn_info
        self._comp_msg_specs = comp_msg_specs
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

        Raises:
            NoSerializerForComponentError: если для нужного компонента нет
                сериализатора

        Returns:
            MessageSerializer: сериализатор сообщений

        """
        if component not in self._comp_msg_specs:
            err_msg = f"There is no serializator for the component '{component.name}'"
            logger.error("%s (Logic error)", err_msg)
            raise NoSerializerForComponentError(err_msg)

        comp_msg_spec = self._comp_msg_specs[component]
        return MessageSerializer(comp_msg_spec)

    async def _send_msg_to_address(
        self, addr: Addr, msg: Message, *, only_data: bool = False
    ) -> bool:
        """Отправить KBEngine-сообщение на TCP адрес."""
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
        # Нужно закрыть клиентское подключение, т.к. это разовая отправка
        client.stop()

        return True

    async def send_msg(self, msg: Message, addr: Addr) -> bool:
        """Отправить сообщение.

        Если адрес получателя отличается от клиентского соединения, то
        сообщение будет отправлено "в один конец" без возможности получить
        ответное сообщение по новому соединению.

        Args:
            msg (Message): сообщение для отправки на компонент
            addr (Addr): адрес KBEngine-компонента, которому отправляется
                сообщение

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
                "equal (response addr = '%s', back channel addr = '%s')",
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

    def close(self) -> None:
        """Закрыть канал обратной связи.

        После закрытия отправка сообщений будет невозможна.
        """
        self._closed = True
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
        msg_back_channel = TCPMsgBackChannel(
            conn_info, self._comp_msg_specs, back_channel
        )

        while data:
            msg, data = self._serializer.deserialize(data)
            if msg is None:
                logger.warning(
                    "[%s] Unreadable data received. Possibly long "
                    "message or invalid data. The data is not handled",
                    self,
                )
                return False

            logger.debug('[%s] Message "%s" fields: %s', self, msg.id, msg.get_values())
            self._msg_receiver.on_receive_msg(msg, msg_back_channel)

        # Объект канал обратной связи остаётся открытым. Он или закроется
        # вызывающим кодом или он закроется транспортной библиотекой при
        # закрытии клиентского клиентского подключения.

        logger.debug("[%s] The received data was handled ", self)
        return True

    # TODO: [2025-07-21 10:12 burov_alexey@mail.ru]:
    # Возможно, нужно будет отслеживать отпавшие соединения. Тогда нужно
    # добавить интерфейс для уведомлений об этом. Пока не используется,
    # оставляю так.
    def on_end_receive_client_data(self, conn_info: ConnInfo) -> None:  # noqa: ARG002
        """Колбэк на закрытие соединения клиентом.

        Args:
            conn_info (ConnInfo): соединение, которое закрылось

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
