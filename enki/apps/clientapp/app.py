"""Приложение клиента KBEngine.

Принимает и отправляет сообщения. Создаёт события в игровой слой (слой
пользователя).
"""

import asyncio
import logging
from asyncio import Task

from enki import msgspec
from enki.command.baseapp import BaseappHelloCommand
from enki.command.loginapp import LoginappHelloCommand, LoginappLoginCommand
from enki.kbeenum import ClientType, ComponentType
from enki.kbetype.pytypes.basic_data_types import KBEString
from enki.misc import devonly
from enki.misc.periodical_task import IPeriodicalTask, LoopPeriod
from enki.misc.result import Result
from enki.misc.startable import IStartable
from enki.msg.message import Message
from enki.msg.msg_client import TcpMsgClient
from enki.net.addr import Addr, Port
from enki.settings import SECOND

logger = logging.getLogger(__name__)


class ClientApp(IStartable):
    """Приложение клиента KBEngine."""

    def __init__(
        self,
        *,
        loginapp_addr: Addr,
        login_name: str,
        password: str,
        client_data: bytes,
        entitydefs_hash: str,
        client_type: ClientType,
        kbe_version: str,
        script_version: str,
        encrypted_key: bytes,
        server_tick_period: float,
        force_login: bool,
    ) -> None:
        """Конструктор.

        Args:
            loginapp_addr (Addr): адрес LoginApp

            login_name (str): логин
            password (str): пароль аккаунта
            client_data (bytes): дополнинтельные данные от клиента
            entitydefs_hash (str): хэш игровых скриптов
            client_type (ClientType): тип клиента
            kbe_version (str): версия KBEngine
            script_version (str): версия скриптов (кода на питоне / assets'ов)
            encrypted_key (bytes): ключ шифрования (???)
            server_tick_period (float): частота, с которой отправляется
                onClientActiveTick
            force_login: принудительно делать логин (???)

        """
        self._loginapp_addr = loginapp_addr

        self._login_name = login_name
        self._password = password
        self._client_data = client_data
        self._entitydefs_hash = entitydefs_hash
        self._client_type = client_type
        self._force_login = force_login

        self._kbe_version = kbe_version
        self._script_version = script_version
        self._encrypted_key = encrypted_key

        self._server_tick_period = server_tick_period

        self._loginapp_client: TcpMsgClient | None = None
        self._baseapp_client: TcpMsgClient | None = None

        self._is_alive_task: _OnClientActiveTickPeriodicalTask | None = None
        self._receiving_msgs_task: Task | None = None

    @property
    def is_alive(self) -> bool:
        """Флаг запущен ли экземпляр класса.

        Returns:
            bool: флаг запущен ли экземпляр класса

        """
        # Пока предполагаем, что есть только одно подключение или к Loginapp,
        # или к Baseapp
        if self._loginapp_client is not None:
            return self._loginapp_client.is_alive

        if self._baseapp_client is not None:
            return self._baseapp_client.is_alive

        return False

    async def start(self) -> Result:  # noqa: PLR0911
        """Запустить объект.

        Returns:
            Result: результат запуска объекта

        """
        self._loginapp_client = TcpMsgClient(
            self._loginapp_addr,
            ComponentType.CLIENT,
            on_end_receive_msg_cb=self._on_end_receive_msg_cb,
        )
        start_res = await self._loginapp_client.start()
        if not start_res.success:
            text = f'Loginapp is not reachable. Reason: "{start_res.text}")'
            return Result(success=False, result=None, text=text)

        logger.info("Connected to Loginapp (%s)", self._loginapp_client)

        loginapp_hello_cmd = LoginappHelloCommand(
            self._kbe_version,
            self._script_version,
            self._encrypted_key,
            self._loginapp_client,
        )
        hello_res = await loginapp_hello_cmd.execute()
        if not hello_res.success:
            text = (
                f'Loginapp hello is not successful. Reason: "{hello_res.text}")'
            )
            return Result(success=False, result=None, text=text)

        loginapp_login_cmd = LoginappLoginCommand(
            ClientType.UNKNOWN,
            client_data=self._client_data,
            login_name=self._login_name,
            password=self._password,
            digest=self._entitydefs_hash,
            force_login=self._force_login,
            started_client=self._loginapp_client,
        )
        loginapp_login_res = await loginapp_login_cmd.execute()
        if not loginapp_login_res.success:
            text = f'Login is not success. Reason: "{loginapp_login_res.text}")'
            return Result(success=False, result=None, text=text)

        assert loginapp_login_res.result is not None

        self._loginapp_client.stop()
        self._loginapp_client = None

        baseapp_addr = Addr(
            ip_addr=loginapp_login_res.result.host,
            port=Port(loginapp_login_res.result.tcp_port),
        )
        logger.info(
            "The LoginApp login is successful. The BaseApp adress is %s",
            baseapp_addr,
        )

        # Добавляется колбэк в приложение, чтобы знать о разрыве,
        # переподключении и прочем
        self._baseapp_client = TcpMsgClient(
            baseapp_addr,
            ComponentType.CLIENT,
            on_end_receive_msg_cb=self._on_end_receive_msg_cb,
        )
        start_res = await self._baseapp_client.start()
        if not start_res.success:
            text = (
                f'Cannot connect to the "{baseapp_addr}" Baseapp address '
                f'Reason: "{start_res.text}"'
            )
            logger.error(text)
            return Result(success=False, result=None, text=start_res.text)

        logger.info("Connected to Baseapp (%s)", self._baseapp_client)

        baseapp_hello_cmd = BaseappHelloCommand(
            self._kbe_version,
            self._script_version,
            self._encrypted_key,
            self._baseapp_client,
            resp_timeout=5 * SECOND,
        )
        baseapp_hello_res = await baseapp_hello_cmd.execute()
        if not baseapp_hello_res.success:
            text = f'Baseapp hello is not successful. Reason: "{hello_res.text}")'
            return Result(success=False, result=None, text=text)

        # Запустить переиодическую отправку уведомлений, что клиент живой
        self._is_alive_task = _OnClientActiveTickPeriodicalTask(
            self._baseapp_client, self._server_tick_period
        )
        await self._is_alive_task.start_periodical_task()

        # После удачного логина посыпятся сообщения на синхронизацию состояния
        # (данные сущности аккаунта). На данном моменте есть подключение к
        # Baseapp, проверены версии движка и скриптов. Можно делать логин.
        # А приложение на этой точке считается запущенным. Если логин к Baseapp
        # будет неудачным, то это уже будет обработано в общем обработчике
        # сообщений приложения.

        baseapp_login_msg = Message.create(
            msgspec.baseapp.loginBaseapp,
            (KBEString(self._login_name), KBEString(self._password)),
        )
        success = await self._baseapp_client.send_msg(baseapp_login_msg)
        if not success:
            text = (
                f"[{self}] The message is not sent (client = '{self._baseapp_client}', "
                f"msg = '{baseapp_login_msg}')"
            )
            logger.warning(text)
            return Result(success=False, result=None, text=text)

        logger.debug("[%s] The login message to Baseapp has been sent", self)

        self._start_receiving_msgs()

        return Result(success=True, result=None)

    def stop(self) -> None:
        """Остановить объект."""
        if self._is_alive_task is not None:
            self._is_alive_task.stop_periodical_task()
            self._is_alive_task = None

        if self._receiving_msgs_task is not None:
            self._receiving_msgs_task.cancel()
            self._receiving_msgs_task = None

        if self._loginapp_client is not None and self._loginapp_client.is_alive:
            self._loginapp_client.stop()
            self._loginapp_client = None

        if self._baseapp_client is not None and self._baseapp_client.is_alive:
            self._baseapp_client.stop()
            self._baseapp_client = None

    def _on_end_receive_msg_cb(self) -> None:
        """Колбэк на окончание получения данных от сервера."""
        logger.debug("[%s] %s", self, devonly.func_args_values())

    def _start_receiving_msgs(self) -> None:
        """Запустить получение сообщений."""

        async def receive_msgs() -> None:
            if self._baseapp_client is None or not self._baseapp_client.is_alive:
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
        if not self._client.is_alive:
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
