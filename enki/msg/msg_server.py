"""Классы серверов для работы с сообщениями."""

import logging

from enki.misc import devonly
from enki.msg.imsg import IMsgBackChannel, IServerMsgReceiver
from enki.msg.message import Message
from enki.msg.msg_descr import MsgSpecById
from enki.msg.msg_serializer import ComponentMsgSpecById, MessageSerializer
from enki.net.addr import Addr
from enki.net.client import UDPClient
from enki.net.conninfo import ConnInfo
from enki.net.inet import ITCPServerDataReceiver, IUDPServerDataReceiver
from enki.net.server import TCPServer, UDPServer

logger = logging.getLogger(__name__)


class ClosedMsgBackChannelError(Exception):
    """Используется уже закрытый канал обратной связи."""


# TODO: [burov_alexey@mail.ru 09.07.2025 06:53]
# Если канал умеет отправлять сообщения, то он должен уметь отличать для какого
# компонента сообщения. Там, вроде id одинаковые есть? Если нет, то нужно
# составлять одно большое описание сообщений. А сериализатор сообщений будет
# один на всех. Может его в какой-то отдельный интерфейс вынести.
#
# Возможно, сообщению стоит знать для какого они компонента.
#
# Посмотрел. Да, действительно полно одинаковых id сообщений. Тогда на
# инициализации сообщение что-ли должно знать для какого оно компонента.
#
# Скорей всего получатель - это и есть его компонент. Сериализатор знает для
# какого компонента он работает и для какого компонента получает сообщения.
#
# Нужно связать id сообщения и компонент, к оторому оно пренадлежит на уровне
# спецификации классов. Просто сделать все сообщения в классе, а не в модуле.
# И добавить имя компонента.
#
#


class UDPMsgBackChannel(IMsgBackChannel):
    """Канал обратной связи для ответа на соощение.

    Способ отправлять KBEngine-сообщения через слой сообщений.
    """

    def __init__(self, conn_info: ConnInfo, serializer: MessageSerializer) -> None:
        """Конструктор канала обратной связи для ответа на соощение.

        Args:
            conn_info (ConnInfo): информация соединения
            serializer (MessageSerializer): сериализатор сообщений

        """
        self._conn_info = conn_info
        self._serializer = serializer
        self._closed = False

    @property
    def conn_info(self) -> ConnInfo:
        """Данные соединения."""
        return self._conn_info

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

        data = self._serializer.serialize(msg)

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

        data = self._serializer.serialize(msg, only_data=True)

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
    ) -> None:
        """UDP-сервер сериализующий KBEngine-сообщения.

        Слой между бинарным представлением сообщений и объектом сообщения.

        Args:
            addr (ComponentAddr): адрес прослушивания
            comp_msg_spec_by_id (MsgSpecById): маппинг id сообщения к описанию
                сообщения
            msg_receiver (IServerMsgReceiver): получатель десериализованного
                сообщения

        """
        super().__init__(addr)
        self._msg_receiver = msg_receiver
        self._serializer = MessageSerializer(comp_msg_spec_by_id)

    def on_receive_data(self, data: memoryview, addr: Addr) -> None:
        """Колбэк на полученное сериализованное сообщение.

        Args:
            data (memoryview): данные сериализованного сообщения
            addr (ComponentAddr): адрес компонента отправителя

        """
        logger.debug("[%s] Received data (%s)", self, data.obj)
        super().on_receive_data(data, addr)

        conn_info = ConnInfo(addr, self._addr)
        back_channel = UDPMsgBackChannel(conn_info, self._serializer)

        while data:
            msg, data = self._serializer.deserialize(data)
            if msg is None:
                logger.warning("[%s] Got unreadable data. End receiving", self)
                break

            logger.debug(
                '[%s] Message "%s" fields: %s', self, msg.id, msg.get_values()
            )
            self._msg_receiver.on_receive_msg(msg, back_channel)


class TCPMsgServer(TCPServer):
    """TCP-сервер для приёма по UDP сериализованных KBEngine-сообщений."""

    def __init__(
        self,
        addr: Addr,
    ) -> None:
        """Конструктор.

        Args:
            addr (ComponentAddr): _description_
            msg_spec_by_id (MsgSpecById): _description_
            on_receive_data_cb (TCPServerOnReceiveDataCallback | None, optional):
                колбэк на получение данных от сервера, если задан
            on_end_receive_data_cb (TCPServerOnEndReceiveDataCallback | None, optional):
                колбэк на окончание получения данных от сервера, если задан

        """
        self._addr = addr
        self._on_receive_data_cb: TCPServerOnReceiveDataCallback = (
            on_receive_data_cb
            if on_receive_data_cb is not None
            else lambda _data: None
        )
        self._on_end_receive_data_cb: TCPServerOnEndReceiveDataCallback = (
            on_end_receive_data_cb
            if on_end_receive_data_cb is not None
            else lambda: None
        )

        self._addr = addr
        self._transport: Transport | None = None
        self._serializer = MessageSerializer(msg_spec_by_id)
        self._msg_receiver = msg_receiver
        self._server: Optional[Server] = None
        self._serve_forever_task: Optional[Task] = None

    @property
    def addr(self) -> Addr:
        return self._addr.copy()

    async def start(self) -> Result:
        try:
            self._server = await asyncio.start_server(
                self.handle_connection, self._addr.host, self._addr.port
            )
        except (asyncio.TimeoutError, OSError, ConnectionError) as err:
            return Result(False, None, str(err))

        async def serve_forever(server: Server) -> None:
            await server.start_serving()

        self._serve_forever_task = asyncio.create_task(serve_forever(self._server))

        return Result(success=True, result=None)

    async def handle_connection(
        self, reader: StreamReader, writer: StreamWriter
    ) -> None:
        addr = writer.get_extra_info("peername")
        conn_info = ConnInfo(Addr(addr[0], addr[1]), self._addr)
        channel = TCPChannel(conn_info, writer)

        buffer = bytes()
        while not reader.at_eof():
            data = await reader.read(settings.TCP_CHUNK_SIZE)
            if not data:
                continue
            if buffer:
                data = buffer + data
            msg, data_tail = self._serializer.deserialize(memoryview(data))
            if msg is None:
                logger.info(
                    f"[{self}] Data cannot be decoded to the message (%s)",
                    self,
                    data,
                )
                buffer = data
                continue
            buffer = data_tail.tobytes()
            logger.debug(
                '[%s] Message "%s" fields: %s', self, msg.name, msg.get_values()
            )
            await self._msg_receiver.on_receive_msg(msg, channel)

    def stop(self) -> None:
        if self._server is None:
            logger.warning("[%s] The server has been already stopped", self)
            return

        self._server.close()
        self._server = None

        assert self._serve_forever_task is not None
        self._serve_forever_task.cancel()

    @property
    def is_alive(self) -> bool:
        return self._server is not None

    def send_data(self, data: bytes) -> bool:
        return False

    def __str__(self) -> str:
        return f"{__class__.__name__}()"
