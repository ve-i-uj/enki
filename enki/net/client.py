"""Клиенты для подключения к компонентам KBEngine (транспортный уровень OSI)."""

from __future__ import annotations

import asyncio
import logging
import socket
import typing
from asyncio import (
    BaseTransport,
    CancelledError,
    DatagramProtocol,
    DatagramTransport,
    Event,
    Future,
    Protocol,
    Transport,
)
from collections import deque
from typing import Callable, Self, TypeAlias

from enki import settings
from enki.misc import devonly
from enki.misc.result import Result
from enki.net.addr import Addr  # noqa: TC001
from enki.net.inet import (
    IClientDataReceiver,
    IClientDataSender,
    IClosable,
    IConnectableClient,
    IResponseAwaitable,
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

    def connection_lost(self, exc: Exception | None) -> None:
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


class TCPClient(IConnectableClient, IClientDataReceiver, IClientDataSender):
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
    def is_connected(self) -> bool:
        """Флаг запущен ли экземпляр класса."""
        return self._transport is not None

    async def connect(self) -> Result:
        """Запустить tcp-клиент.

        Returns:
            Result: объект результата запуска клиента

        """
        loop = asyncio.get_running_loop()
        future = loop.create_connection(
            lambda: _TCPClientProtocol(self),
            self._addr.ip_addr,
            self._addr.port,
        )
        logger.info("Connecting to the server '%s' ...", self._addr)
        try:
            self._transport, _protocol = await asyncio.wait_for(
                future, settings.CONNECT_TO_SERVER_TIMEOUT
            )
        except (asyncio.TimeoutError, OSError, ConnectionError) as err:
            logger.error(
                "The client cannot connect to the server (err = '%s')",
                err,
            )
            return Result(success=False, result=None, text=str(err))

        logger.debug("[%s] Connected", self)
        return Result(success=True, result=None)

    def disconnect(self) -> None:
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
            logger.info(
                "[%s] Empty chunk. Connection unexpectedly closed", self
            )
            self.on_end_receive_data()
            return

        self._on_receive_data_cb(data)

    def on_end_receive_data(self) -> None:
        """Колбэк окончания передачи данных от транспортной библиотеки."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self.disconnect()
        self._on_end_receive_data_cb()

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

    def connection_lost(self, exc) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._data_receiver.on_end_receive_data()

    def error_received(self, exc) -> None:
        logger.error("[%s] %s", self, devonly.func_args_values())
        self._data_receiver.on_end_receive_data()

    def datagram_received(self, data, addr) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._data_receiver.on_receive_data(data)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self._addr})"

    __repr__ = __str__


class UDPClient(IClientDataReceiver, IClientDataSender, IClosable):
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

        self._transport: DatagramTransport | None = None

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
            transport, _protocol = await loop.create_datagram_endpoint(
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
            transport, _protocol = await loop.create_datagram_endpoint(
                lambda: _UDPClientProtocol(
                    self._addr.to_tuple(),
                    data,
                    on_data_sent_future,
                    data_receiver=self,
                ),
                remote_addr=(self._addr.ip_addr, self._addr.port),
            )

        self._transport = transport

        return await on_data_sent_future

    def on_receive_data(self, data: bytes) -> None:
        """Колбэк на получение сырых данных от компонента."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._on_receive_data_cb(data)

    def on_end_receive_data(self) -> None:
        """Колбэк окончания передачи данных от транспортной библиотеки."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._on_end_receive_data_cb()

    def close(self) -> None:
        """Закрыть."""
        if self._transport is not None:
            self._transport.close()

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}({self._addr}, "
            f"broadcast={self._broadcast})"
        )

    __repr__ = __str__


class ResponseAwaitableClientMixin(IResponseAwaitable, IClientDataReceiver):
    """Миксин для получения ответов через 'async for' по таймауту.

    Для работы нужно выставить флаг '_need_resp_waiting' в True в наследнике
    в момент, когда начинается ожидание ответа.
    """

    def __init__(self) -> None:
        """Конструктор."""
        # Ответы, которые приходят в IClientDataReceiver.on_receive_data
        self._responses: deque[bytes] = deque()
        # Событие, чтобы узнать, что есть ответ
        self._data_event = Event()
        # Флаг, что нужно получать ответы.
        # Получать ответы можно только после отправки данных, т.к. это клиент,
        # а не сервер
        self._need_resp_waiting = False
        # Значение таймаута выставляется в
        # IResponseAwaitable.wait_and_iterate_responses
        self._timeout = 0.0

    def need_resp_waiting(self) -> bool:
        """Hужно ли ждать ответы.

        Returns:
            bool: флаг того, нужно ли ждать ответы

        """
        return self._need_resp_waiting

    def wait_and_iterate_responses(self, timeout: float) -> Self:
        """Возвращает итератор данных от сервера с таймаутом ожидания.

        Args:
            timeout (float, optional): время ожидания ответа

        Returns:
            Self: итератор данных от сервера

        """
        self._timeout = timeout
        return self

    def __aiter__(self) -> Self:
        return self

    async def __anext__(self) -> bytes:
        if self._responses:
            # Если есть ответ, отдаём ответ
            return self._responses.popleft()

        # Если нужно завершить ожидание, останавливаем цикл итератора
        if not self.need_resp_waiting():
            raise StopAsyncIteration

        # Все ответы обработаны. Очищаем событие
        self._data_event.clear()
        try:
            # Ожидаем, когда придут новые данные
            await asyncio.wait_for(self._data_event.wait(), self._timeout)
        except TimeoutError as err:
            logger.info(
                "[%s] The data receiving stopped by timeout (timeout = %s)",
                self,
                self._timeout,
            )
            raise StopAsyncIteration from err

        except CancelledError as err:
            logger.info(
                "[%s] No response. Waiting was canceled",
                self,
            )
            raise StopAsyncIteration from err

        return await self.__anext__()

    def on_receive_data(self, data: bytes) -> None:  # noqa: D102
        logger.debug("[%s] ", self)
        # Сохраняем ответ и сообщаем об этом через событие
        self._responses.append(data)
        self._data_event.set()

    def on_end_receive_data(self) -> None:  # noqa: D102
        logger.debug("[%s] ", self)
        # Клиент больше не будет получать данные. Больше не нужно ждать ответы.
        self._need_resp_waiting = False
        # Чтобы async for завершилось через  StopAsyncIteration
        self._data_event.set()


class IResponseAwaitableClient(
    IResponseAwaitable, IClientDataReceiver, IClientDataSender
):
    """Общий интерфейс для клиента вне зависимости от транспорта."""


class ResponseAwaitableTCPClient(
    TCPClient,
    ResponseAwaitableClientMixin,
    IResponseAwaitableClient,
):
    """TCP-клиент, ожидающий данные от сервера с таймаутом."""

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
        TCPClient.__init__(
            self, addr, on_receive_data_cb, on_end_receive_data_cb
        )
        ResponseAwaitableClientMixin.__init__(self)

    def on_receive_data(self, data: bytes) -> None:  # noqa: D102
        logger.debug("[%s] ", self)
        TCPClient.on_receive_data(self, data)
        ResponseAwaitableClientMixin.on_receive_data(self, data)

    def on_end_receive_data(self) -> None:  # noqa: D102
        logger.debug("[%s] ", self)
        TCPClient.on_end_receive_data(self)
        ResponseAwaitableClientMixin.on_end_receive_data(self)

    async def connect(self) -> Result:  # noqa: D102
        logger.debug("[%s] ", self)
        res = await super().connect()
        # После подключения к серверу можно начать принимать ответы
        self._need_resp_waiting = True
        return res


class ResponseAwaitableUDPClient(
    IResponseAwaitableClient,
    UDPClient,
    ResponseAwaitableClientMixin,
):
    """UDP-клиент, ожидающий данные от сервера с таймаутом."""

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
        UDPClient.__init__(
            self,
            addr,
            on_receive_data_cb,
            on_end_receive_data_cb,
            broadcast=broadcast,
        )
        ResponseAwaitableClientMixin.__init__(self)

    def on_receive_data(self, data: bytes) -> None:  # noqa: D102
        logger.debug("[%s] ", self)
        UDPClient.on_receive_data(self, data)
        ResponseAwaitableClientMixin.on_receive_data(self, data)

    def on_end_receive_data(self) -> None:  # noqa: D102
        logger.debug("[%s] ", self)
        UDPClient.on_end_receive_data(self)
        ResponseAwaitableClientMixin.on_end_receive_data(self)

    async def send_data(self, data: bytes) -> bool:  # noqa: D102
        logger.debug("[%s] %s", self, devonly.func_args_values())
        res = await super().send_data(data)
        # После отправки данных, можно принимать ответы
        self._need_resp_waiting = True
        return res
