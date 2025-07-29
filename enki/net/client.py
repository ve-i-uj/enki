"""Клиенты для подключения к компонентам KBEngine (транспортный уровень OSI)."""

from __future__ import annotations

import asyncio
import logging
import socket
import typing
from asyncio import (
    BaseTransport,
    DatagramProtocol,
    DatagramTransport,
    Future,
    Protocol,
    Transport,
)
from typing import Callable, TypeAlias

from enki import settings
from enki.misc import devonly
from enki.misc.result import Result
from enki.misc.startable import IStartable
from enki.net.addr import Addr  # noqa: TC001
from enki.net.inet import (
    IClientDataReceiver,
    IClientDataSender,
)

logger = logging.getLogger(__name__)


class _TCPClientProtocol(Protocol):
    """Реализация asyncio клиентского tcp-протокола.

    State machine of calls:

      start -> CM [-> DR*] [-> ER?] -> CL -> end

    * CM: connection_made()
    * DR: data_received()
    * ER: eof_received()
    * CL: connection_lost()
    """

    def __init__(self, data_receiver: IClientDataReceiver) -> None:
        """Конструктор.

        Args:
            data_receiver (IClientDataReceiver): получатель данных, реализующий
                интерфейс

        """
        super().__init__()
        self._data_receiver = data_receiver
        self._transport: BaseTransport | None = None

    def connection_made(self, transport: BaseTransport) -> None:
        logger.debug("[%s]", self)
        self._transport = transport

    def connection_lost(self, _exc: Exception | None) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._data_receiver.on_end_receive_data()

    def pause_writing(self) -> None:
        logger.warning("[%s] %s", self, devonly.func_args_values())

    def resume_writing(self) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())

    def data_received(self, data: bytes) -> None:
        logger.debug("[%s] %s", self, data)
        self._data_receiver.on_receive_data(data)

    def eof_received(self) -> bool:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._data_receiver.on_end_receive_data()
        return False

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"


OnReceiveDataCallback: TypeAlias = Callable[[bytes], None]
OnEndReceiveDataCallback: TypeAlias = Callable[[], None]


class TCPClient(IStartable, IClientDataReceiver, IClientDataSender):
    """KBEngine TCP-клиент для отправки и получения данных."""

    def __init__(
        self,
        addr: Addr,
        on_receive_data_cb: OnReceiveDataCallback | None = None,
        on_end_receive_data_cb: OnEndReceiveDataCallback | None = None,
    ) -> None:
        """KBEngine TCP-клиент для отправки данных.

        Args:
            addr (AppAddr): адрес компонента, к которому будет подключение
            on_receive_data_cb (OnReceiveDataCallback | None, optional): колбэк
                на получение данных от сервера. Defaults to None.
            on_end_receive_data_cb (OnEndReceiveDataCallback | None, optional):
                колбэк на окончание получения данных от сервера. Defaults to None.

        """
        self._addr = addr
        self._transport: Transport | None = None
        self._on_receive_data_cb: OnReceiveDataCallback = (
            on_receive_data_cb
            if on_receive_data_cb is not None
            else lambda _data: None
        )
        self._on_end_receive_data_cb: OnEndReceiveDataCallback = (
            on_end_receive_data_cb
            if on_end_receive_data_cb is not None
            else lambda: None
        )

    @property
    def is_alive(self) -> bool:
        """Флаг запущен ли экземпляр класса."""
        return self._transport is not None

    async def start(self) -> Result:
        """Запустить tcp-клиент.

        Returns:
            Result: объект результата запуска клиента

        """
        loop = asyncio.get_running_loop()
        future = loop.create_connection(
            lambda: _TCPClientProtocol(self),
            self._addr.host,
            self._addr.port,
        )
        logger.info("[%s] Connecting to the server ...", self)
        try:
            self._transport, _protocol = await asyncio.wait_for(
                future, settings.CONNECT_TO_SERVER_TIMEOUT
            )
        except (asyncio.TimeoutError, OSError, ConnectionError) as err:
            logger.exception("[%s]", self)
            return Result(success=False, result=None, text=str(err))

        logger.debug("[%s] Connected", self)
        return Result(success=True, result=None)

    def stop(self) -> None:
        """Остановить объект tcp-клиента."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        if self._transport is None:
            logger.debug("[%s] The client has already stopped", self)
            return

        self._transport.close()
        self._transport = None

    def on_receive_data(self, data: bytes) -> None:
        """Колбэк на получение сырых данных от компонента."""
        logger.debug("[%s] Received data (%s)", self, data)
        if not data:
            logger.info("[%s] Empty chunk. Connection unexpectedly closed", self)
            self.stop()
            return

        self._on_receive_data_cb(data)

    def on_end_receive_data(self) -> None:
        """Колбэк окончания передачи данных от транспортной библиотеки."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._on_end_receive_data_cb()
        self.stop()

    async def send_data(self, data: bytes) -> bool:
        """Отправить данные по сетевому подключению.

        Args:
            data (bytes): данные для отправки

        Returns:
            bool: флаг удачно или нет отправились данные

        """
        if self._transport is None:
            logger.warning(
                "[%s] The connection is not connected (data = %s)",
                self,
                data,
            )
            return False

        try:
            self._transport.write(data)
        except (ConnectionError, OSError, RuntimeError):
            logger.exception("[%s] The data cannot be sent", self)
            return False

        logger.debug("[%s] Data has been sent", self)
        return True

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self._addr})"


class _UDPClientProtocol(DatagramProtocol):
    """Протокол для колбэков UDP-соединения."""

    def __init__(
        self,
        addr: tuple[str, int],
        data: bytes,
        on_data_sent_future: Future[bool],
        *,
        data_receiver: IClientDataReceiver,
    ) -> None:
        """Конструктор.

        Args:
            addr (tuple[str, int]): адрес энпоинта, которому отправятся данные
                по UDP
            data (bytes): данные для отправки
            on_data_sent_future (Future[bool]): фьюче-объект об успешной отправке
            data_receiver (IClientDataReceiver): получатель данных, реализующий
                интерфейс

        """
        self._addr = addr
        self._data = data
        self._transport: DatagramTransport | None = None

        self._on_data_sent_future: Future[bool] = on_data_sent_future
        self._data_receiver = data_receiver

    def connection_made(self, transport: BaseTransport) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        transport = typing.cast("DatagramTransport", transport)
        self._transport = transport
        try:
            self._transport.sendto(self._data, self._addr)
        except (OSError, RuntimeError):
            logger.exception("[%s] The data cannot be sent", self)
            self._on_data_sent_future.set_result(False)
            return

        self._on_data_sent_future.set_result(True)

    def connection_lost(self, exc):
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._data_receiver.on_end_receive_data()

    def error_received(self, exc):
        logger.error("[%s] %s", self, devonly.func_args_values())
        self._data_receiver.on_end_receive_data()

    def datagram_received(self, data, addr):
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._data_receiver.on_receive_data(data)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self._addr})"

    __repr__ = __str__


class UDPClient(IClientDataSender, IClientDataReceiver):
    """UDP-клиент."""

    def __init__(
        self,
        addr: Addr,
        on_receive_data_cb: OnReceiveDataCallback | None = None,
        on_end_receive_data_cb: OnEndReceiveDataCallback | None = None,
        *,
        broadcast: bool = False,
    ) -> None:
        """UDP-клиент для отправки данных KBEngine компоненту.

        Args:
            addr (AppAddr): адрес эндпоинта
            on_receive_data_cb (OnReceiveDataCallback | None, optional): колбэк
                на получение данных от сервера. Defaults to None.
            on_end_receive_data_cb (OnEndReceiveDataCallback | None, optional):
                колбэк на окончание получения данных от сервера. Defaults to None.
            broadcast (bool, optional): флаг нужно ли отправлять бродкастом.
                Defaults to False.

        """
        self._addr = addr
        self._broadcast = broadcast

        self._on_receive_data_cb: OnReceiveDataCallback = (
            on_receive_data_cb
            if on_receive_data_cb is not None
            else lambda _data: None
        )
        self._on_end_receive_data_cb: OnEndReceiveDataCallback = (
            on_end_receive_data_cb
            if on_end_receive_data_cb is not None
            else lambda: None
        )

    async def send_data(self, data: bytes) -> bool:
        """Отправить данные KBEngine-компоненту по UDP-подключению.

        Args:
            data (bytes): данные

        Returns:
            bool: флаг удачного отправления

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        loop = asyncio.get_running_loop()

        on_data_sent_future: Future[bool] = Future()

        if self._broadcast:
            _transport, _protocol = await loop.create_datagram_endpoint(
                lambda: _UDPClientProtocol(
                    self._addr.to_tuple(),
                    data,
                    on_data_sent_future,
                    data_receiver=self,
                ),
                family=socket.AF_INET,
                proto=socket.IPPROTO_UDP,
                allow_broadcast=True,
                local_addr=None,
            )
        else:
            _transport, _protocol = await loop.create_datagram_endpoint(
                lambda: _UDPClientProtocol(
                    self._addr.to_tuple(),
                    data,
                    on_data_sent_future,
                    data_receiver=self,
                ),
                remote_addr=(self._addr.host, self._addr.port),
            )

        return await on_data_sent_future

    def on_receive_data(self, data: bytes) -> None:
        """Колбэк на получение сырых данных от компонента."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._on_receive_data_cb(data)

    def on_end_receive_data(self) -> None:
        """Колбэк окончания передачи данных от транспортной библиотеки."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._on_end_receive_data_cb()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self._addr}, broadcast={self._broadcast})"

    __repr__ = __str__
