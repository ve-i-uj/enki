"""Модуль содержит классы серверов, обслуживающих сетевые соединения."""

from __future__ import annotations

import asyncio
import logging
import socket
from asyncio import (
    BaseTransport,
    DatagramProtocol,
    DatagramTransport,
    Server,
    StreamReader,
    StreamWriter,
    Task,
)
from typing import ClassVar

from enki import settings
from enki.misc import devonly
from enki.misc.result import Result
from enki.misc.startable import IStartable
from enki.net.addr import Addr
from enki.net.conninfo import ConnInfo
from enki.net.inet import (
    ITCPBackChannel,
    ITCPServerDataReceiver,
    IUDPServerDataReceiver,
)

logger = logging.getLogger(__name__)


def get_free_port() -> int:
    """Возвращает значение свободного порта.

    Returns:
        int: свободный порт

    """
    sock = socket.socket()
    sock.bind(("", 0))
    return sock.getsockname()[1]


def get_real_host_ip(docker_container_name: str) -> str:
    """Возвращает реальный ip адрес по имени контейнера.

    Args:
        docker_container_name (str): имя docker-контейнера

    Returns:
        str: ip-адрес

    """
    sock = socket.socket()
    sock.bind((docker_container_name, 0))
    return sock.getsockname()[0]


class _UDPServerProtocol(DatagramProtocol):
    """Протокол асинхронного приёма UDP-датаграм."""

    def __init__(
        self, addr: tuple[str, int], data_receiver: IUDPServerDataReceiver
    ) -> None:
        """Конструктор.

        Args:
            addr (tuple[str, int]): UDP-адрес прослушивания
            data_receiver (IServerDataReceiver): получатель пришедших данных

        """
        self._addr = addr
        self._data_receiver = data_receiver
        self._transport: BaseTransport | None = None

    def connection_made(self, transport: BaseTransport) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._transport = transport

    def connection_lost(self, exc: Exception | None) -> None:
        logger.info("[%s] %s", self, exc)
        self._data_receiver.on_stop_receive_data()

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._data_receiver.on_receive_data(memoryview(data), addr)

    def error_received(self, exc: Exception | None) -> None:
        logger.error("[%s] %s", self, exc)
        self._data_receiver.on_stop_receive_data()

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}(addr={self._addr}, "
            f"data_receiver={self._data_receiver})"
        )

    __repr__ = __str__


class UDPServer(IStartable, IUDPServerDataReceiver):
    """UDP-сервер."""

    def __init__(
        self,
        addr: Addr,
    ) -> None:
        """UDP-сервер.

        Для получения данных от сервера нужно:

        1) переопределить методы интерфейса `IUDPServerDataReceiver`

        Args:
            addr (ComponentAddr): адрес прослушивания UDP-сервером

        """
        self._addr = addr
        self._transport: DatagramTransport | None = None

    @property
    def served_addr(self) -> Addr:
        """Обслуживаемый адрес."""
        return self._addr.copy()

    async def start(self) -> Result:
        """Запустить UDP-сервер.

        Returns:
            Result: объект результата запуска

        """
        loop = asyncio.get_running_loop()
        try:
            self._transport, _ = await loop.create_datagram_endpoint(
                lambda: _UDPServerProtocol(
                    self._addr.to_tuple(), data_receiver=self
                ),
                local_addr=(self._addr.host, self._addr.port),
            )
        except (asyncio.TimeoutError, OSError, ConnectionError) as err:
            return Result(success=False, result=None, text=str(err))

        logger.info("[%s] Start listening", self)
        return Result(success=True, result=None)

    def stop(self) -> None:
        """Остановить UDP-сервер."""
        if self._transport is None or self._transport.is_closing():
            self._transport = None
            logger.info("[%s] The server has been already stopped", self)
            return

        self._transport.close()
        self._transport = None

    @property
    def is_alive(self) -> bool:
        """Флаг запущен ли UDP-сервер.

        Returns:
            bool: запущен ли UDP-сервер

        """
        return self._transport is not None

    def on_receive_data(self, data: memoryview, addr: tuple[str, int]) -> None:
        """Колбэк на обработку сырых данных от компонента.

        Args:
            data (memoryview): данные
            addr (ComponentAddr): адрес отправителя

        """
        logger.debug("[%s] Received data (%s, %s)", self, data.obj, addr)

    def on_stop_receive_data(self) -> None:
        """Колбэк на остановку прослушки со стороны транспортной библиотеки."""
        self.stop()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(addr={self._addr})"

    __repr__ = __str__


class TCPBackChannel(ITCPBackChannel):
    """Канал обратной связи на данные полученные по TCP."""

    def __init__(
        self, connection_info: ConnInfo, writer: StreamWriter
    ) -> None:
        """Канал обратной связи на данные полученные по TCP.

        Args:
            connection_info (ConnInfo): информация о подключении
            writer (StreamWriter): asyncio обёртка вокруг транспорта

        """
        self._connection_info = connection_info
        self._writer = writer

    @property
    def connection_info(self) -> ConnInfo:
        """Информация о подключении."""
        return self._connection_info

    async def send_data(self, data: bytes) -> bool:
        """Отправить данные по сетевому подключению.

        Args:
            data (bytes): данные для отправки

        Returns:
            bool: флаг получилось ли отправить данные

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        if self._writer.is_closing():
            logger.debug(
                "[%s] The data cannot be sent. The connection is closing", self
            )
            return False

        self._writer.write(data)
        await self._writer.drain()

        logger.debug("[%s] The data sent", self)
        return True

    def close(self) -> None:
        """Закрыть канал обратной связи."""
        logger.debug("[%s] The back channel is closed", self)
        if not self._writer.is_closing():
            self._writer.close()


class TCPServer(IStartable, ITCPServerDataReceiver[TCPBackChannel]):
    """TCP-сервер."""

    _TCP_CHUNK_SIZE: ClassVar = settings.TCP_CHUNK_SIZE

    def __init__(
        self,
        addr: Addr,
    ) -> None:
        """TCP-сервер.

        Для получения данных от клиентов во внешний код нужно:

            1) переопределить методы интерфейса `ITCPServerDataReceiver`

        Args:
            addr (ComponentAddr): адрес прослушивания

        """
        self._addr = addr

        self._server: Server | None = None
        self._serve_forever_task: Task | None = None

    @property
    def served_addr(self) -> Addr:
        """Обслуживаемый адрес."""
        return self._addr.copy()

    def on_receive_client_data(
        self,
        data: memoryview,  # noqa: ARG002
        back_channel: TCPBackChannel,  # noqa: ARG002
    ) -> bool:
        """Обработчик сырых данных от компонента.

        Args:
            data (memoryview): данные
            back_channel (ITCPBackChannel): канал обратной связи

        Returns:
            bool: были ли обработаны данные

        """
        return True

    def on_end_receive_client_data(self, conn_info: ConnInfo) -> None:  # noqa: ARG002
        """Колбэк на закрытие соединения клиентом.

        Может вызываться несколько раз.

        Args:
            conn_info (ConnInfo): соединение, которое закрылось

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

    async def start(self) -> Result:
        """Запустить TCP-сервер.

        Returns:
            Result: объект результата запуска

        """
        try:
            self._server = await asyncio.start_server(
                self._handle_connection, self._addr.host, self._addr.port
            )
        except (asyncio.TimeoutError, OSError, ConnectionError) as err:
            return Result(success=False, result=None, text=str(err))

        async def serve_forever(server: Server) -> None:
            await server.start_serving()

        self._serve_forever_task = asyncio.create_task(
            serve_forever(self._server)
        )

        logger.info("[%s] Start listening", self)
        return Result(success=True, result=None)

    async def _handle_connection(
        self, reader: StreamReader, writer: StreamWriter
    ) -> None:
        """Обработать tcp-подключение.

        Args:
            reader (StreamReader): API для чтения данных из IO стрим
            writer (StreamWriter): API для записи данных в IO стрим

        """
        addr = writer.get_extra_info("peername")
        conn_info = ConnInfo(Addr(addr[0], addr[1]), self._addr)
        channel = TCPBackChannel(conn_info, writer)

        buffer = b""
        try:
            while True:
                data = await reader.read(settings.TCP_CHUNK_SIZE)
                if not data:
                    logger.debug(
                        "[%s] The client closed the connection (conn_info = '%s')",
                        self,
                        conn_info,
                    )
                    break

                # обработка данных

                buffer += data

                # Вызов интерфейсного метода
                data_handled = self.on_receive_client_data(
                    memoryview(buffer), channel
                )
                if not data_handled:
                    # Сообщение могло не уместиться в один tcp-пакет
                    logger.warning(
                        "[%s] The data packet was not handled", self
                    )
                    continue

                buffer = b""

        except ConnectionResetError:
            logger.exception(
                "[%s] The client closed the connection unexpectedly", self
            )
        except ConnectionAbortedError:
            logger.exception("[%s] Client error", self)
        finally:
            writer.close()
            await writer.wait_closed()

            channel.close()
            # Вызов интерфейсного метода
            self.on_end_receive_client_data(conn_info)

    def stop(self) -> None:
        """Остановить TCP-сервер."""
        if self._server is None:
            logger.warning("[%s] The server has been already stopped", self)
            return

        self._server.close()

        if self._serve_forever_task is not None:
            self._serve_forever_task.cancel()

        self._server = None
        self._serve_forever_task = None

    @property
    def is_alive(self) -> bool:
        """Флаг запущен ли tcp-сервер.

        Returns:
            bool: флаг запущен ли tcp-сервер

        """
        return self._server is not None

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self._addr})"
