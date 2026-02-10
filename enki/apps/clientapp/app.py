"""Приложение клиента KBEngine.

Принимает и отправляет сообщения. Создаёт события в игровой слой (слой
пользователя).
"""

import asyncio
import logging
from asyncio import Task

from enki import msgspec
from enki.apps.clientapp.clients.baseapp_client import BaseappClient
from enki.apps.clientapp.clients.loginapp_client import LoginappClient
from enki.misc import devonly
from enki.misc.periodical_task import IPeriodicalTask, LoopPeriod
from enki.misc.result import Result
from enki.misc.startable import IStartable
from enki.msg.message import Message
from enki.msg.msg_client import TcpMsgClient
from enki.net.addr import Addr

logger = logging.getLogger(__name__)


class ClientApp(IStartable):
    """Приложение клиента KBEngine."""

    def __init__(
        self,
        *,
        loginapp_addr: Addr,
        server_tick_period: float,
        force_login: bool,
    ) -> None:
        """Конструктор.

        Args:
            server_tick_period (float): частота, с которой отправляется
                onClientActiveTick
            force_login: принудительно делать логин (???)

        """
        self._force_login = force_login
        self._server_tick_period = server_tick_period

        self._loginapp_client: LoginappClient = LoginappClient(loginapp_addr)
        self._baseapp_client: BaseappClient | None = None

        self._is_alive_task: _OnClientActiveTickPeriodicalTask | None = None
        self._receiving_msgs_task: Task | None = None

    @property
    def loginapp_client(self) -> LoginappClient:
        return self._loginapp_client

    @property
    def baseapp_client(self) -> BaseappClient:
        assert self._baseapp_client is not None
        return self._baseapp_client

    def create_baseapp_client(self, baseapp_addr: Addr) -> BaseappClient:
        self._baseapp_client = BaseappClient(baseapp_addr)
        return self._baseapp_client

    @property
    def is_started(self) -> bool:
        """Флаг запущен ли экземпляр класса.

        Returns:
            bool: флаг запущен ли экземпляр класса

        """
        # Пока предполагаем, что есть только одно подключение или к Loginapp,
        # или к Baseapp
        if self._loginapp_client is not None:
            return self._loginapp_client.is_started

        if self._baseapp_client is not None:
            return self._baseapp_client.is_started

        return False

    async def start(self) -> Result:
        return await self._loginapp_client.start()

    def stop(self) -> None:
        """Остановить объект."""
        if self._is_alive_task is not None:
            self._is_alive_task.stop_periodical_task()
            self._is_alive_task = None

        if self._receiving_msgs_task is not None:
            self._receiving_msgs_task.cancel()
            self._receiving_msgs_task = None

        if (
            self._loginapp_client is not None
            and self._loginapp_client.is_started
        ):
            self._loginapp_client.stop()
            self._loginapp_client = None

        if self._baseapp_client is not None and self._baseapp_client.is_started:
            self._baseapp_client.stop()
            self._baseapp_client = None

    def _on_end_receive_msg_cb(self) -> None:
        """Колбэк на окончание получения данных от сервера."""
        logger.debug("[%s] %s", self, devonly.func_args_values())

    def _start_receiving_msgs(self) -> None:
        """Запустить получение сообщений."""

        async def receive_msgs() -> None:
            if (
                self._baseapp_client is None
                or not self._baseapp_client.is_started
            ):
                logger.warning("[%s] There is not started Baseapp client", self)
                return

            async for msg in self._baseapp_client:
                self._handle_msg(msg)

            logger.debug("[%s] Receiving messgaes is stopped", self)

        self._receiving_msgs_task = asyncio.create_task(receive_msgs())

    def _handle_msg(self, msg: Message) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())


class _OnClientActiveTickPeriodicalTask(IPeriodicalTask):
    """Задача по периодической отправке сообщения Baseapp::onClientActiveTick.

    Уведомления, что клиент живой.
    """

    def __init__(self, client: TcpMsgClient, period: LoopPeriod) -> None:
        """Конструктор."""
        self._client: TcpMsgClient | None = client
        self._period = period
        self._task: Task | None = None

    async def _send_msg(self) -> None:
        msg = Message.create(msgspec.baseapp.onClientActiveTick, ())
        assert self._client is not None
        if not self._client.is_started:
            logger.warning(
                "[%s] The client is not alive. The periodical task should be stopped",
                self,
            )
            return

        success = await self._client.send_msg(msg)
        if not success:
            logger.warning("[%s] The message '%s' is not sent", self, msg.name)
            return

        logger.debug(
            "[%s] The message 'Baseapp::onClientActiveTick' is successfuly sent",
            self,
        )

    async def start_periodical_task(self) -> None:
        """Запустить периодическую задачу."""

        async def periodical() -> None:
            while True:
                await self._send_msg()
                await asyncio.sleep(self._period)

        self._task = asyncio.create_task(periodical())

    def stop_periodical_task(self) -> None:
        """Остановить периодическую задачу."""
        if self._task is not None:
            self._task.cancel()
            self._task = None
        if self._client is not None:
            self._client = None
