"""Приложение клиента KBEngine.

Принимает и отправляет сообщения. Создаёт события в игровой слой (слой
пользователя).
"""

from __future__ import annotations

import collections
import logging
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, NoReturn, TypeAlias

from enki import msgspec
from enki.kbeenum import ClientType, ComponentType, ServerError
from enki.kbetype.pytypes.basic_data_types import KBEBlob, KBEInt8, KBEString
from enki.misc import devonly
from enki.misc.result import Result
from enki.misc.startable import IStartable
from enki.msg.imsg import IClientMsgReceiver
from enki.msg.message import Message
from enki.msg.msg_client import TcpMsgClient
from enki.msg_parser.client_msg_parser import (
    OnCreateAccountResultMsgParser,
    OnHelloCBMsgParser,
    OnLoginFailedMsgParser,
    OnLoginSuccessfullyMsgParser,
    OnScriptVersionNotMatchMsgParser,
    OnVersionNotMatchMsgParser,
)
from enki.settings import SECOND

if TYPE_CHECKING:
    from enki.apps.clientapp.entity_sub_system.entity_msg_parsers import (
        EntityId,
    )
    from enki.apps.clientapp.layer.thlayer import ThreadedGameLayer
    from enki.kbeentity.entity_descr import EntityDesc
    from enki.net.addr import Addr


import asyncio
from asyncio import Task
from typing import TYPE_CHECKING

from enki import settings
from enki.msg_parser.client_msg_parser import (
    OnLoginBaseappFailedMsgParser,
)

if TYPE_CHECKING:
    from enki.net.addr import Addr


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from asyncio import Task

logger = logging.getLogger(__name__)


class ClientApp(IStartable, IClientMsgReceiver):
    """Приложение клиента KBEngine."""

    def __init__(
        self,
        *,
        loginapp_addr: Addr,
        server_tick_period: float,
        force_login: bool,
        game_layer: ThreadedGameLayer,
        entity_desc_by_uid: dict[int, EntityDesc],
    ) -> None:
        """Конструктор.

        Args:
            server_tick_period (float): частота, с которой отправляется
                onClientActiveTick
            force_login: принудительно делать логин (???)
            entity_desc_by_uid - это описание типа (какие есть свойства, методы
                и т.д.),
            game_entity_by_type_name - это нагенеренные игровые сущности (классы),

        """
        self._force_login = force_login
        self._server_tick_period = server_tick_period

        self._loginapp_client: LoginappClient = LoginappClient(loginapp_addr)
        self._baseapp_client: BaseappClient | None = None

        self._receiving_msgs_task: Task | None = None

        self._pending_msgs_by_entity_id: dict[EntityId, list[Message]] = (
            collections.defaultdict(list)
        )

        self._game_layer = game_layer

        # entity_helper = EntityHelper(
        #     entity_desc_by_uid, entity_serializer_by_uid, kbenginexml
        # )

        # OnUpdatePropertysClientAppHandler()

    @property
    def game(self) -> ThreadedGameLayer:
        return self._game_layer

    def add_pending_msg(self, entity_id: int, msg: Message) -> None:
        self._pending_msgs_by_entity_id[entity_id].append(msg)

    def resend_pending_msgs(self, entity_id: int) -> None:
        if entity_id in self._pending_msgs_by_entity_id:
            logger.debug("There are pending messages. Resend them ...")
            for msg in self._pending_msgs_by_entity_id[entity_id]:
                self.on_receive_msg(msg)
            self._pending_msgs_by_entity_id.pop(entity_id)

    @property
    def loginapp_client(self) -> LoginappClient:
        return self._loginapp_client

    # [2026-02-16 12:17 burov_alexey@mail.ru]:
    # Подумать бы с инициализацией этого клиента как-то по другому. Здесь
    # порядок нелогичен.
    @property
    def baseapp_client(self) -> BaseappClient:
        assert self._baseapp_client is not None
        return self._baseapp_client

    def create_baseapp_client(self, baseapp_addr: Addr) -> BaseappClient:
        self._baseapp_client = BaseappClient(baseapp_addr, app=self)
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
        if self._loginapp_client.is_started:
            self._loginapp_client.stop()

        if self._baseapp_client is not None and self._baseapp_client.is_started:
            self._baseapp_client.stop()
            self._baseapp_client = None

    def on_receive_msg(self, msg: Message) -> None:
        """Колбэк на получение сообщения."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        # Сообщения, касающиеся сущностей. В этой точке мы определяем какие
        # колбэки нужно вызвать в игровом слое.

    def on_end_receive_msg(self) -> None:
        """Колбэк, что сообщения больше приходить не будут."""
        logger.debug("[%s] %s", self, devonly.func_args_values())

    # [2026-02-21 16:27 burov_alexey@mail.ru]:
    # Если приложение не остановлено и закончилось получение сообщений - это и
    # есть разрыв по ошибке. Этот метод со всеми его колбэками до транспортной
    # библиотеки не нужен.
    def on_end_receive_msg_by_error(self, err: Any = None) -> None:
        """Колбэк, что сообщения больше приходить не будут из-за ошибки."""
        logger.debug("[%s] %s", self, devonly.func_args_values())


@dataclass
class GetBaseappAddressResultData:
    ret_code: ServerError
    data: bytes
    baseapp_tcp_addr: Addr | None = None
    baseapp_udp_addr: Addr | None = None


class GetBaseappAddressResult(Result):
    success: bool
    result: GetBaseappAddressResultData
    text: str = ""


AccountName: TypeAlias = str
AccountPassword: TypeAlias = str
AccountData: TypeAlias = bytes


class CheckVersionResultDataEnum(Enum):
    OK = "OK"
    KBE_VERSION_MISMATCH = "KBE_VERSION_MISMATCH"
    ASSETS_VERSION_MISMATCH = "ASSETS_VERSION_MISMATCH"


@dataclass
class CheckVersionResultData:
    flag: CheckVersionResultDataEnum

    encrypted_key: bytes

    kbe_version: str | None = None
    assets_version: str | None = None
    protocol_md5: str | None = None
    entity_def_md5: str | None = None
    component_type: ComponentType | None = None


@dataclass(frozen=True)
class CheckVersionResult(Result):
    success: bool
    result: CheckVersionResultData
    text: str = ""


@dataclass
class CreateAccountResultData:
    ret_code: ServerError
    # хз что тут
    data: bytes


@dataclass(frozen=True)
class CreateAccountResult(Result):
    success: bool
    result: CreateAccountResultData
    text: str = ""


class LoginappConnectionError(Exception):
    pass


class LoginappNoResponseError(Exception):
    pass


class LoginappClient(IStartable):

    def __init__(
        self,
        loginapp_addr: Addr,
    ) -> None:
        self._tcp_msg_client: TcpMsgClient = TcpMsgClient(
            loginapp_addr,
            ComponentType.CLIENT,
            on_end_receive_msg_cb=self._on_end_receive_msg_cb,
        )

    async def _get_started_tcp_msg_client(self) -> TcpMsgClient:
        if self._tcp_msg_client.is_started:
            return self._tcp_msg_client

        res = await self._tcp_msg_client.start()
        if not res.success:
            raise LoginappConnectionError(res.text)

        return self._tcp_msg_client

    @property
    def is_started(self) -> bool:
        return self._tcp_msg_client.is_started

    def stop(self) -> None:
        self._tcp_msg_client.stop()

    async def start(self) -> Result:
        """Запустить объект.

        Returns:
            Result: результат запуска объекта

        """
        start_res = await self._tcp_msg_client.start()
        if not start_res.success:
            text = f'Loginapp is not reachable. Reason: "{start_res.text}")'
            logger.debug("[%s] %s", self, text)
            return Result(success=False, result=None, text=text)

        logger.info("Connected to Loginapp (%s)", self._tcp_msg_client)
        return Result(success=True, result=None)

    async def check_version(
        self,
        kbe_version: str,
        assets_version: str,
        encrypted_key: bytes,
        wait_seconds: int = 5 * SECOND,
    ) -> CheckVersionResult:
        """Проверяет версии.

        Returns:
            bool: True если сервер доступен, иначе False.

        """
        msg = Message.create(
            msgspec.loginapp.hello,
            values=(
                KBEString(kbe_version),
                KBEString(assets_version),
                KBEBlob(encrypted_key),
            ),
        )

        if not self._tcp_msg_client.is_started:
            err_text = (
                f"[{self}] The client is not alive (client = '{self._tcp_msg_client}', "
                f"msg = '{msg}')"
            )
            logger.warning(err_text)

            raise LoginappConnectionError(err_text)

        success = await self._tcp_msg_client.send_msg(msg)
        if not success:
            err_text = (
                f"[{self}] The message is not sent (client = '{self._tcp_msg_client}', "
                f"msg = '{msg}')"
            )
            logger.warning(err_text)

            raise LoginappConnectionError(err_text)

        resp_msg = await self._tcp_msg_client.wait_only_first_resp_msg(
            wait_seconds
        )
        if resp_msg is None:
            err_text = (
                f"[{self}] There is no response. Waiting stopped by timeout "
                f"(client = '{self._tcp_msg_client}', msg = '{msg}')"
            )
            logger.warning(err_text)

            raise LoginappNoResponseError(err_text)

        if resp_msg.id == msgspec.client.onVersionNotMatch.id:
            onVersionNotMatch_res = OnVersionNotMatchMsgParser().parse(resp_msg)
            assert onVersionNotMatch_res.result is not None
            onVersionNotMatch_pd = onVersionNotMatch_res.result  # noqa: N806

            plugin_kbe_version = msg.get_values()[0]
            server_kbe_version = onVersionNotMatch_pd.kbe_version
            text = (
                f'Plugin designed for KBEngine version "{plugin_kbe_version}". '
                f'But actual KBEngine version is "{server_kbe_version}"'
            )
            logger.warning("[%s] %s", self, text)
            return CheckVersionResult(
                success=False,
                result=CheckVersionResultData(
                    flag=CheckVersionResultDataEnum.KBE_VERSION_MISMATCH,
                    kbe_version=server_kbe_version,
                    encrypted_key=encrypted_key,
                ),
                text=text,
            )

        if resp_msg.id == msgspec.client.onScriptVersionNotMatch.id:
            onScriptVersionNotMatch_res = (  # noqa: N806
                OnScriptVersionNotMatchMsgParser().parse(resp_msg)
            )
            assert onScriptVersionNotMatch_res.result is not None
            onScriptVersionNotMatch_pd = onScriptVersionNotMatch_res.result

            plugin_assets_version = msg.get_values()[1]
            server_assets_version = onScriptVersionNotMatch_pd.assets_version
            text = (
                f'Plugin designed for assets version "{plugin_assets_version}". '
                f'But actual script version is "{server_assets_version}"'
            )
            return CheckVersionResult(
                success=False,
                result=CheckVersionResultData(
                    flag=CheckVersionResultDataEnum.ASSETS_VERSION_MISMATCH,
                    assets_version=server_assets_version,
                    encrypted_key=encrypted_key,
                ),
                text=text,
            )

        onHelloCB_res = OnHelloCBMsgParser().parse(resp_msg)  # noqa: N806
        assert onHelloCB_res.result is not None

        onHelloCB_pd = onHelloCB_res.result  # noqa: N806

        return CheckVersionResult(
            success=True,
            result=CheckVersionResultData(
                flag=CheckVersionResultDataEnum.OK,
                encrypted_key=encrypted_key,
                kbe_version=onHelloCB_pd.kbe_version,
                assets_version=onHelloCB_pd.assets_version,
                protocol_md5=onHelloCB_pd.protocol_md5,
                entity_def_md5=onHelloCB_pd.entity_def_md5,
                component_type=onHelloCB_pd.component_type,
            ),
        )

    async def get_baseapp_address(
        self,
        client_type: ClientType,
        client_data: bytes,
        account_name: AccountName,
        password: AccountPassword,
        entitydefs_hash: str,
        force_login: bool,
        wait_seconds: int = 5 * SECOND,
    ) -> GetBaseappAddressResult:
        """Получить адрес Baseapp."""
        # [2026-02-10 00:00 burov_alexey@mail.ru]:
        # Нужна блокировка на только одну отправку сообщения. Иначе чужие \
        # ответы будут ловиться.
        tcp_msg_client = await self._get_started_tcp_msg_client()

        msg = Message.create(
            msgspec.loginapp.login,
            values=(
                KBEInt8(client_type.value),
                KBEBlob(client_data),
                KBEString(account_name),
                KBEString(password),
                KBEString(entitydefs_hash),
                KBEString("1" if force_login else ""),
            ),
        )

        logger.debug("[%s] Send the message ...", self)

        success = await tcp_msg_client.send_msg(msg)
        if not success:
            err_text = (
                f"[{self}] The message is not sent (client = '{tcp_msg_client}', "
                f"msg = '{msg}')"
            )
            logger.warning(err_text)
            raise LoginappConnectionError(err_text)

        logger.info("[%s] The message was sent. Waiting for response ...", self)
        resp_msg = await tcp_msg_client.wait_only_first_resp_msg(wait_seconds)
        if resp_msg is None:
            err_text = (
                f"[{self}] There is no response. Waiting stopped by timeout or "
                f"closed by the server"
            )
            logger.warning(err_text)
            raise LoginappConnectionError(err_text)

        if resp_msg.id == msgspec.client.onLoginFailed.id:
            onLoginFailed_res = OnLoginFailedMsgParser().parse(resp_msg)
            assert onLoginFailed_res.result is not None
            onLoginFailed_pd = onLoginFailed_res.result  # noqa: N806

            err_text = (
                f"Login Falied (reason = "
                f"'{onLoginFailed_pd.ret_code.name}', data = "
                f"'{onLoginFailed_pd.data.decode()}')"
            )
            logger.info("%s", err_text)
            return GetBaseappAddressResult(
                success=False,
                result=GetBaseappAddressResultData(
                    ret_code=onLoginFailed_pd.ret_code,
                    data=onLoginFailed_pd.data,
                ),
                text=err_text,
            )

        res = OnLoginSuccessfullyMsgParser().parse(resp_msg)
        assert res.result is not None
        pd = res.result

        logger.info(
            "The LoginApp login is successful. The BaseApp address is %s and %s",
            pd.baseapp_tcp_address,
            pd.baseapp_udp_address,
        )

        return GetBaseappAddressResult(
            success=True,
            result=GetBaseappAddressResultData(
                ServerError.SUCCESS,
                pd.data,
                pd.baseapp_tcp_address,
                pd.baseapp_udp_address,
            ),
        )

    async def reset_password(self, username: str) -> None:
        """Скинуть пароль."""

    def bind_account_email(
        self, entity_id: int, password: str, email: str
    ) -> NoReturn:
        """Привязать попробовать email к аккаунту."""
        raise NotImplementedError

    def set_new_password(
        self, entity_id: int, oldpassword: str, newpassword: str
    ) -> NoReturn:
        """Задать новый пароль."""
        raise NotImplementedError

    async def create_account(
        self,
        username: AccountName,
        password: AccountPassword,
        create_account_data: AccountData,
        wait_seconds: int = 5 * SECOND,
    ) -> CreateAccountResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())

        msg = Message.create(
            msgspec.loginapp.reqCreateAccount,
            values=(
                KBEString(username),
                KBEString(password),
                KBEBlob(create_account_data),
            ),
        )

        tcp_msg_client = await self._get_started_tcp_msg_client()

        success = await tcp_msg_client.send_msg(msg)
        if not success:
            err_text = (
                f"[{self}] The message is not sent (client = '{tcp_msg_client}', "
                f"msg = '{msg}')"
            )
            logger.warning(err_text)

            raise LoginappConnectionError(err_text)

        resp_msg = await tcp_msg_client.wait_only_first_resp_msg(wait_seconds)
        if resp_msg is None:
            err_text = (
                f"[{self}] There is no response. Waiting stopped by timeout "
                f"(client = '{tcp_msg_client}', msg = '{msg}')"
            )
            logger.warning(err_text)

            raise LoginappNoResponseError(err_text)

        assert resp_msg.name == msgspec.client.onCreateAccountResult.name

        res = OnCreateAccountResultMsgParser().parse(resp_msg)
        assert res.result is not None
        pd = res.result

        if res.result.ret_code != ServerError.SUCCESS:
            return CreateAccountResult(
                False, CreateAccountResultData(pd.ret_code, pd.data)
            )

        return CreateAccountResult(
            True, CreateAccountResultData(pd.ret_code, pd.data)
        )

    def _on_end_receive_msg_cb(self) -> None:
        """Колбэк на окончание получения данных от сервера."""
        logger.debug("[%s] %s", self, devonly.func_args_values())

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    __repr__ = __str__


class _ClientMsgReceiver(IClientMsgReceiver):

    def on_receive_msg(self, msg: Message) -> None:
        """Колбэк на получение сообщения."""
        raise NotImplementedError

    def on_end_receive_msg(self) -> None:
        """Колбэк, что сообщения больше приходить не будут."""
        raise NotImplementedError

    def on_end_receive_msg_by_error(self) -> None:
        """Колбэк, что сообщения больше приходить не будут из-за ошибки."""
        raise NotImplementedError


class BaseappConnectionError(Exception):
    pass


class BaseappNoResponseError(Exception):
    pass


@dataclass(frozen=True)
class BaseappCheckVersionResult(Result):
    success: bool
    result: CheckVersionResultData
    text: str = ""


@dataclass(frozen=True)
class BaseappLoginResult(Result):
    success: bool
    result: ServerError
    text: str = ""


class _OnClientActiveTickPeriodicalTask:
    """Задача по периодической отправке сообщения Baseapp::onClientActiveTick.

    Уведомления, что клиент живой.
    """

    def __init__(self, client: TcpMsgClient, period: float) -> None:
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


class BaseappClient(IStartable):

    def __init__(
        self,
        baseapp_addr: Addr,
        app: ClientApp,
    ) -> None:
        self._tcp_msg_client = TcpMsgClient(
            baseapp_addr,
            ComponentType.CLIENT,
            on_end_receive_msg_cb=self._on_end_receive_msg_cb,
        )
        self._app = app

        self._is_alive_task: _OnClientActiveTickPeriodicalTask | None = None
        self._receiving_msgs_task: Task | None = None

    @property
    def is_started(self) -> bool:
        return self._tcp_msg_client.is_started

    async def start(self) -> Result:
        """Запустить объект.

        Returns:
            Result: результат запуска объекта

        """
        start_res = await self._tcp_msg_client.start()
        if not start_res.success:
            text = f'Baseapp is not reachable. Reason: "{start_res.text}")'
            logger.debug("[%s] %s", self, text)
            return Result(success=False, result=None, text=text)

        logger.info("Connected to Baseapp (%s)", self._tcp_msg_client)
        return Result(success=True, result=None)

    def stop(self) -> None:
        if self._is_alive_task is not None:
            self._is_alive_task.stop_periodical_task()
            self._is_alive_task = None

        self._tcp_msg_client.stop()

    async def _get_started_tcp_msg_client(self) -> TcpMsgClient:
        if self._tcp_msg_client.is_started:
            return self._tcp_msg_client

        res = await self._tcp_msg_client.start()
        if not res.success:
            raise BaseappConnectionError(res.text)

        return self._tcp_msg_client

    async def login(
        self, account_name: str, password: str, wait_seconds: int = 5 * SECOND
    ) -> BaseappLoginResult:
        self._tcp_msg_client = await self._get_started_tcp_msg_client()

        logger.info("Connected to Baseapp (%s)", self._tcp_msg_client.addr)

        # Запустить переиодическую отправку уведомлений, что клиент живой
        self._is_alive_task = _OnClientActiveTickPeriodicalTask(
            self._tcp_msg_client, settings.SERVER_TICK_PERIOD
        )
        await self._is_alive_task.start_periodical_task()

        # После удачного логина посыпятся сообщения на синхронизацию состояния
        # (данные сущности аккаунта). На данном моменте есть подключение к
        # Baseapp, проверены версии движка и скриптов. Можно делать логин.
        # Нужно дождаться ответа на логин и потом отдать управление приложению.

        baseapp_login_msg = Message.create(
            msgspec.baseapp.loginBaseapp,
            (KBEString(account_name), KBEString(password)),
        )
        success = await self._tcp_msg_client.send_msg(baseapp_login_msg)
        if not success:
            text = (
                f"[{self}] The message is not sent (client = '{self._tcp_msg_client}', "
                f"msg = '{baseapp_login_msg}')"
            )
            logger.warning(text)
            raise BaseappConnectionError(text)

        logger.debug("[%s] The login message to Baseapp has been sent", self)

        msg: Message | None = None
        async for msg in self._tcp_msg_client.wait_and_iterate_resp_msgs(
            wait_seconds
        ):
            # Есть ответное сообщение

            if msg.id == msgspec.client.onLoginBaseappFailed.id:
                onLoginBaseappFailed_res = (
                    OnLoginBaseappFailedMsgParser().parse(msg)
                )

                text = (
                    f"Baseapp login failed "
                    f"(reason = '{onLoginBaseappFailed_res.result.ret_code.name}')"
                )
                assert onLoginBaseappFailed_res.result is not None
                logger.debug(text)

                return BaseappLoginResult(
                    success=False,
                    result=onLoginBaseappFailed_res.result.ret_code,
                    text=text,
                )

            # Это ответное сообщение уже начало синхронизации. А значит логин
            # удачно завершён. Нужно отдать полученное сообщение приложению на
            # обработку. И отдать получение сообщений приложению.

            break

        if msg is None:
            # Не было ответа на логин. Или сеть, или в сервере логика. Но это
            # неудачный логин из-за нестандартной ситуации.
            err_text = (
                f"[{self}] There is no response. Waiting stopped by timeout "
                f"(client = '{self._tcp_msg_client}', msg = '{baseapp_login_msg}')"
            )
            logger.warning(err_text)

            raise BaseappNoResponseError(err_text)

        self._handle_msg(msg)

        self._start_receiving_msgs()

        return BaseappLoginResult(success=True, result=ServerError.SUCCESS)

    def _start_receiving_msgs(self) -> None:
        """Запустить получение сообщений."""

        async def receive_msgs() -> None:
            if (
                self._tcp_msg_client is None
                or not self._tcp_msg_client.is_started
            ):
                logger.warning("[%s] There is not started Baseapp client", self)
                return

            # TODO: [2026-02-10 20:49 burov_alexey@mail.ru]:
            # Больше SERVER_TICK_PERIOD должен быть сброс со стороны Baseapp.
            # Таймаут стоит на ожидание ответа. При каждом новом ответе таймаут
            # тоже обновляется.
            # Это нужно оформить.
            async for msg in self._tcp_msg_client.wait_and_iterate_resp_msgs(
                settings.SERVER_TICK_PERIOD * 1.5
            ):
                self._handle_msg(msg)

            logger.debug("[%s] Receiving messgaes is stopped", self)

        self._receiving_msgs_task = asyncio.create_task(receive_msgs())

    def _handle_msg(self, msg: Message) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._app.on_receive_msg(msg)

    def _on_end_receive_msg_cb(self) -> None:
        """Колбэк на окончание получения данных от сервера."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._app.on_end_receive_msg()

    def _on_end_receive_msg_by_error_cb(self, err: Any = None) -> None:
        """Колбэк на окончание получения данных от сервера."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._app.on_end_receive_msg_by_error(err)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    __repr__ = __str__

    async def check_version(
        self,
        kbe_version: str,
        assets_version: str,
        encrypted_key: bytes,
        wait_seconds: int = 5 * SECOND,
    ) -> BaseappCheckVersionResult:
        """Проверяет версии.

        Returns:
            bool: True если сервер доступен, иначе False.

        """
        msg = Message.create(
            msgspec.baseapp.hello,
            values=(
                KBEString(kbe_version),
                KBEString(assets_version),
                KBEBlob(encrypted_key),
            ),
        )

        if not self._tcp_msg_client.is_started:
            err_text = (
                f"[{self}] The client is not alive (client = '{self._tcp_msg_client}', "
                f"msg = '{msg}')"
            )
            logger.warning(err_text)

            raise BaseappConnectionError(err_text)

        success = await self._tcp_msg_client.send_msg(msg)
        if not success:
            err_text = (
                f"[{self}] The message is not sent (client = '{self._tcp_msg_client}', "
                f"msg = '{msg}')"
            )
            logger.warning(err_text)

            raise BaseappConnectionError(err_text)

        resp_msg = await self._tcp_msg_client.wait_only_first_resp_msg(
            wait_seconds
        )
        if resp_msg is None:
            err_text = (
                f"[{self}] There is no response. Waiting stopped by timeout "
                f"(client = '{self._tcp_msg_client}', msg = '{msg}')"
            )
            logger.warning(err_text)

            raise BaseappNoResponseError(err_text)

        if resp_msg.id == msgspec.client.onVersionNotMatch.id:
            onVersionNotMatch_res = OnVersionNotMatchMsgParser().parse(resp_msg)
            assert onVersionNotMatch_res.result is not None
            onVersionNotMatch_pd = onVersionNotMatch_res.result  # noqa: N806

            plugin_kbe_version = msg.get_values()[0]
            server_kbe_version = onVersionNotMatch_pd.kbe_version
            text = (
                f'Plugin designed for KBEngine version "{plugin_kbe_version}". '
                f'But actual KBEngine version is "{server_kbe_version}"'
            )
            logger.warning("[%s] %s", self, text)
            return BaseappCheckVersionResult(
                success=False,
                result=CheckVersionResultData(
                    flag=CheckVersionResultDataEnum.KBE_VERSION_MISMATCH,
                    kbe_version=server_kbe_version,
                    encrypted_key=encrypted_key,
                ),
                text=text,
            )

        if resp_msg.id == msgspec.client.onScriptVersionNotMatch.id:
            onScriptVersionNotMatch_res = (  # noqa: N806
                OnScriptVersionNotMatchMsgParser().parse(resp_msg)
            )
            assert onScriptVersionNotMatch_res.result is not None
            onScriptVersionNotMatch_pd = onScriptVersionNotMatch_res.result

            plugin_assets_version = msg.get_values()[1]
            server_assets_version = onScriptVersionNotMatch_pd.assets_version
            text = (
                f'Plugin designed for assets version "{plugin_assets_version}". '
                f'But actual script version is "{server_assets_version}"'
            )
            return BaseappCheckVersionResult(
                success=False,
                result=CheckVersionResultData(
                    flag=CheckVersionResultDataEnum.ASSETS_VERSION_MISMATCH,
                    assets_version=server_assets_version,
                    encrypted_key=encrypted_key,
                ),
                text=text,
            )

        onHelloCB_res = OnHelloCBMsgParser().parse(resp_msg)  # noqa: N806
        assert onHelloCB_res.result is not None

        onHelloCB_pd = onHelloCB_res.result  # noqa: N806

        return BaseappCheckVersionResult(
            success=True,
            result=CheckVersionResultData(
                flag=CheckVersionResultDataEnum.OK,
                encrypted_key=encrypted_key,
                kbe_version=onHelloCB_pd.kbe_version,
                assets_version=onHelloCB_pd.assets_version,
                protocol_md5=onHelloCB_pd.protocol_md5,
                entity_def_md5=onHelloCB_pd.entity_def_md5,
                component_type=onHelloCB_pd.component_type,
            ),
        )

    async def bind_main(self, account_name: str) -> None:
        # Baseapp::reqAccountBindEmail
        #     --> Client::onReqAccountBindEmailCB
        pass

    async def update_password(self, account_name) -> None:
        # * Baseapp::reqAccountNewPassword
        #     --> Client::onReqAccountNewPasswordCB
        pass

    async def logout(self) -> None:
        # Baseapp::logoutBaseapp
        pass

    async def relogin(self) -> None:
        # Baseapp::reloginBaseapp
        pass
