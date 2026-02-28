from __future__ import annotations

import asyncio
import logging
import sys
from asyncio import Event, Future, Task
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Literal, TypeAlias

from enki import msgspec, settings
from enki.kbeenum import ClientType, ComponentType, ServerError
from enki.kbetype import *
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
    OnReqAccountResetPasswordCBMsgParser,
    OnScriptVersionNotMatchMsgParser,
    OnVersionNotMatchMsgParser,
)
from enki.settings import SECOND

if TYPE_CHECKING:
    from enki.msg.msg_descr import MsgId
    from enki.net.addr import Addr

logger = logging.getLogger(__name__)


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


@dataclass
class LoginappLoginResultData:
    ret_code: ServerError
    data: bytes
    baseapp_tcp_addr: Addr | None = None
    baseapp_udp_addr: Addr | None = None


class LoginappLoginResult(Result):
    success: bool
    result: LoginappLoginResultData
    text: str = ""


AccountName: TypeAlias = str
AccountEmail: TypeAlias = str
AccountPassword: TypeAlias = str
AccountData: TypeAlias = bytes


class CheckVersionResultDataEnum(Enum):
    OK = "OK"
    KBE_VERSION_MISMATCH = "KBE_VERSION_MISMATCH"
    ASSETS_VERSION_MISMATCH = "ASSETS_VERSION_MISMATCH"


@dataclass
class LoginappHelloResultData:
    flag: CheckVersionResultDataEnum

    encrypted_key: bytes

    kbe_version: str | None = None
    assets_version: str | None = None
    protocol_md5: str | None = None
    entity_def_md5: str | None = None
    component_type: ComponentType | None = None


@dataclass(frozen=True)
class LoginappHelloResult(Result):
    success: bool
    result: LoginappHelloResultData
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


@dataclass
class ReqAccountResetPasswordResultData:
    ret_code: ServerError


@dataclass(frozen=True)
class ReqAccountResetPasswordResult(Result):
    success: bool
    result: ReqAccountResetPasswordResultData
    text: str = ""


@dataclass
class OnClientActiveTickResultData:
    resp_dt: datetime


@dataclass(frozen=True)
class OnClientActiveTickResult(Result):
    success: bool
    result: OnClientActiveTickResultData
    text: str = ""


class LoginappConnectionError(Exception):
    pass


class LoginappNoResponseError(Exception):
    pass


class LoginappIsNotStartedError(Exception):
    pass


class LoginAppNotLoggedInError(Exception):
    """Исключение, когда пользователь не авторизован в LoginApp."""


WaitingRespTimeout: TypeAlias = float
_WAIT_FOREVER = WaitingRespTimeout(sys.maxsize)


@dataclass
class WaitingRespMsgData:
    msg: Message
    resp_msgs: list[MsgId]
    timeout: WaitingRespTimeout
    future: Future[Message]


class WaitingRespMsgStorage:

    def __init__(self) -> None:
        self._waiting_resp_msgs: list[WaitingRespMsgData] = []

    @property
    def is_empty(self) -> bool:
        return len(self._waiting_resp_msgs) == 0

    def get_all(self) -> list[WaitingRespMsgData]:
        return self._waiting_resp_msgs[:]

    def add_waiting_obj(self, waiting_resp_obj: WaitingRespMsgData) -> None:
        self._waiting_resp_msgs.append(waiting_resp_obj)

    def pop_waiting_obj(self, resp_msg_id: MsgId) -> WaitingRespMsgData | None:
        obj_for_deleting = None
        i_for_deleting = None
        for i, obj in enumerate(self._waiting_resp_msgs):
            if resp_msg_id in obj.resp_msgs:
                obj_for_deleting = obj
                i_for_deleting = i
                break

        if i_for_deleting is not None:
            del self._waiting_resp_msgs[i_for_deleting]
            assert obj_for_deleting is not None
            return obj_for_deleting

        return None


class LoginappClient(IStartable):
    """Клиент для серверного компонента KBEngine 'Loginapp'."""

    def __init__(
        self,
        loginapp_addr: Addr,
        client_type: Literal[
            ComponentType.CLIENT, ComponentType.BOTS, ComponentType.TOOL
        ],
        wait_response_seconds: int,
        server_tick_period: float,
    ) -> None:
        """server_tick_period - частота, с которой отправляется onClientActiveTick,."""
        self._tcp_msg_client: TcpMsgClient = TcpMsgClient(
            loginapp_addr,
            client_type,
            on_end_receive_msg_cb=self._on_end_receive_msg_cb,
        )

        self._wait_response_seconds = wait_response_seconds

        self._stopping = False
        self._logging_in = False
        self._logged_in = False

        self._waiting_resp_storage = WaitingRespMsgStorage()
        self._receiving_msgs_task: Task | None = None

        self._server_tick_period = server_tick_period
        self._server_tick_task: Task | None = None
        self._server_tick_last_dt: datetime | None = None
        self._server_tick_event = Event()

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
            text = f'Loginapp is not reachable. Reason: "{start_res.text}")'
            logger.debug("[%s] %s", self, text)
            return Result(success=False, result=None, text=text)

        self._start_receiving_msgs()
        self._server_tick_task = asyncio.create_task(
            self._send_periodical_tick(self._wait_response_seconds)
        )

        logger.info("Connected to Loginapp (%s)", self._tcp_msg_client)
        return Result(success=True, result=None)

    def stop(self) -> None:
        if self._stopping:
            logger.info("[%s] The client is already stopping", self)
            return

        self._stopping = True
        # После этого завершится цикл в _start_receiving_msgs. Но нужно ещё вывести
        # _send_periodical_tick из ожидания.
        self._tcp_msg_client.stop()
        self._server_tick_event.set()

        # Отменить все фьюче, ожидающие сообщения
        for obj in self._waiting_resp_storage.get_all():
            obj.future.cancel()

    async def wait_until_stop(self) -> None:
        """Ожидание, когда сервер завершит работу."""
        if self._receiving_msgs_task is not None:
            await self._receiving_msgs_task
            self._receiving_msgs_task = None

        if self._server_tick_task is not None:
            await self._server_tick_task
            self._server_tick_task = None

    def _check_client_is_started(self) -> None:
        if not self._tcp_msg_client.is_started:
            text = "There is no connection to Loginapp"
            logger.warning("[%s] %s", self, text)
            raise LoginappIsNotStartedError(text)

    @property
    def _is_logged_in(self) -> bool:
        return self._receiving_msgs_task is not None and not self._stopping

    def _check_client_is_logged_in(self) -> None:
        if not self._is_logged_in:
            text = "There is no login to Loginapp"
            logger.warning("[%s] %s", self, text)

            raise LoginAppNotLoggedInError(text)

    async def _send_msg(
        self,
        msg: Message,
        resp_wait_obj: WaitingRespMsgData | None = None,
    ) -> None:
        self._check_client_is_started()

        if resp_wait_obj is not None:
            self._waiting_resp_storage.add_waiting_obj(resp_wait_obj)

        success = await self._tcp_msg_client.send_msg(msg)
        if not success:
            if resp_wait_obj is not None:
                assert resp_wait_obj.resp_msgs
                self._waiting_resp_storage.pop_waiting_obj(resp_wait_obj.resp_msgs[0])
            err_text = (
                f"[{self}] The message is not sent (client = '{self._tcp_msg_client}', "
                f"msg = '{msg}')"
            )
            logger.warning(err_text)
            raise LoginappConnectionError(err_text)

    def _start_receiving_msgs(self) -> None:
        """Запустить получение сообщений."""

        async def receive_msgs() -> None:
            if self._tcp_msg_client is None or not self._tcp_msg_client.is_started:
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
        if not self._waiting_resp_storage.is_empty:
            waiting_resp_obj = self._waiting_resp_storage.pop_waiting_obj(msg.id)
            assert waiting_resp_obj is not None
            waiting_resp_obj.future.set_result(msg)
            return

    async def _send_periodical_tick(self, wait_timeout: int) -> None:
        self._check_client_is_started()

        # Пока можно получать ответные сообщения
        while self._stopping:
            try:
                res = await self.onClientActiveTick(wait_timeout)
                self._server_tick_last_dt = res.result.resp_dt
            except (
                LoginappIsNotStartedError,
                LoginappConnectionError,
                LoginappNoResponseError,
            ) as err:
                # Не получилось отправить сообщение о том, что клиент живой.
                # Предупреждение в лог и ждём, когда кикнут или будет понятно,
                # что проблемы с сетью. Сами ничего не делаем.
                logger.warning(
                    "[%s] Server tick is not sent. Last tick '%s' (err = %s)",
                    self,
                    (
                        self._server_tick_last_dt
                        if self._server_tick_last_dt is not None
                        else "<Never>"
                    ),
                    err,
                )

            self._server_tick_event.clear()

            try:
                async with asyncio.timeout(self._server_tick_period):
                    await self._server_tick_event.wait()
            except TimeoutError:
                pass

    def _on_end_receive_msg_cb(self) -> None:
        """Колбэк на окончание получения данных от сервера."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        if not self._stopping:
            # Это разрыв соединения
            logger.warning("[%s] The connection is lost", self)
            self.stop()

    async def hello(
        self,
        kbe_version: str,
        assets_version: str,
        encrypted_key: bytes,
        wait_seconds: int = 5 * SECOND,
    ) -> LoginappHelloResult:
        """Проверяет версии (Loginapp::hello)."""
        if not self._tcp_msg_client.is_started:
            text = "There is no connection to Loginapp"
            logger.warning("[%s] %s", self, text)
            raise LoginappIsNotStartedError(text)

        msg = Message.create(
            msgspec.loginapp.hello,
            values=(
                KBEString(kbe_version),
                KBEString(assets_version),
                KBEBlob(encrypted_key),
            ),
        )

        resp_wait_obj = WaitingRespMsgData(
            msg,
            resp_msgs=[
                msgspec.client.onVersionNotMatch.id,
                msgspec.client.onScriptVersionNotMatch.id,
                msgspec.client.onHelloCB.id,
            ],
            timeout=wait_seconds,
            future=Future(),
        )
        await self._send_msg(msg, resp_wait_obj)

        try:
            async with asyncio.timeout(resp_wait_obj.timeout):
                resp_msg = await resp_wait_obj.future
        except TimeoutError:
            self._waiting_resp_storage.pop_waiting_obj(resp_wait_obj.resp_msgs[0])

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
            return LoginappHelloResult(
                success=False,
                result=LoginappHelloResultData(
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
            return LoginappHelloResult(
                success=False,
                result=LoginappHelloResultData(
                    flag=CheckVersionResultDataEnum.ASSETS_VERSION_MISMATCH,
                    assets_version=server_assets_version,
                    encrypted_key=encrypted_key,
                ),
                text=text,
            )

        onHelloCB_res = OnHelloCBMsgParser().parse(resp_msg)  # noqa: N806
        assert onHelloCB_res.result is not None

        onHelloCB_pd = onHelloCB_res.result  # noqa: N806

        return LoginappHelloResult(
            success=True,
            result=LoginappHelloResultData(
                flag=CheckVersionResultDataEnum.OK,
                encrypted_key=encrypted_key,
                kbe_version=onHelloCB_pd.kbe_version,
                assets_version=onHelloCB_pd.assets_version,
                protocol_md5=onHelloCB_pd.protocol_md5,
                entity_def_md5=onHelloCB_pd.entity_def_md5,
                component_type=onHelloCB_pd.component_type,
            ),
        )

    async def login(
        self,
        client_type: ClientType,
        client_data: bytes,
        account_name: AccountName,
        password: AccountPassword,
        entitydefs_hash: str,
        force_login: bool,
        wait_seconds: float = 5 * SECOND,
    ) -> LoginappLoginResult:
        """Получить адрес Baseapp (Loginapp::login)."""
        if self._logging_in:
            return LoginappLoginResult(
                success=False, result=None, text="It's already trying login"
            )
        if self._logged_in:
            return LoginappLoginResult(
                success=False, result=None, text="It's already logged in"
            )

        self._check_client_is_started()

        self._logging_in = True

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

        resp_wait_obj = WaitingRespMsgData(
            msg,
            resp_msgs=[
                msgspec.client.onLoginFailed.id,
                msgspec.client.onLoginSuccessfully.id,
            ],
            timeout=wait_seconds,
            future=Future(),
        )
        await self._send_msg(msg, resp_wait_obj)
        try:
            async with asyncio.timeout(resp_wait_obj.timeout):
                resp_msg = await resp_wait_obj.future
        except TimeoutError:
            self._waiting_resp_storage.pop_waiting_obj(resp_wait_obj.resp_msgs[0])

            err_text = (
                f"[{self}] There is no response. Waiting stopped by timeout "
                f"(client = '{self._tcp_msg_client}', msg = '{msg}')"
            )
            logger.warning(err_text)

            raise LoginappNoResponseError(err_text)

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
            return LoginappLoginResult(
                success=False,
                result=LoginappLoginResultData(
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

        self._logged_in = True

        return LoginappLoginResult(
            success=True,
            result=LoginappLoginResultData(
                ServerError.SUCCESS,
                pd.data,
                pd.baseapp_tcp_address,
                pd.baseapp_udp_address,
            ),
        )

    async def reqCreateAccount(
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
                KBERowByteData(create_account_data),
            ),
        )

        resp_wait_obj = WaitingRespMsgData(
            msg,
            resp_msgs=[msgspec.client.onCreateAccountResult.id],
            timeout=wait_seconds,
            future=Future(),
        )
        await self._send_msg(msg, resp_wait_obj)

        try:
            async with asyncio.timeout(resp_wait_obj.timeout):
                resp_msg = await resp_wait_obj.future
        except TimeoutError:
            self._waiting_resp_storage.pop_waiting_obj(resp_wait_obj.resp_msgs[0])

            err_text = (
                f"[{self}] There is no response. Waiting stopped by timeout "
                f"(client = '{self._tcp_msg_client}', msg = '{msg}')"
            )
            logger.warning(err_text)

            raise LoginappNoResponseError(err_text)

        assert resp_msg.id == msgspec.client.onCreateAccountResult.id

        res = OnCreateAccountResultMsgParser().parse(resp_msg)
        assert res.result is not None
        pd = res.result

        if res.result.ret_code != ServerError.SUCCESS:
            return CreateAccountResult(
                False, CreateAccountResultData(pd.ret_code, pd.data)
            )

        return CreateAccountResult(True, CreateAccountResultData(pd.ret_code, pd.data))

    async def reqCreateMailAccount(
        self,
        email: AccountEmail,
        password: AccountPassword,
        create_account_data: AccountData,
        wait_seconds: float = 5 * SECOND,
    ) -> CreateAccountResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())

        msg = Message.create(
            msgspec.loginapp.reqCreateMailAccount,
            values=(
                KBEString(email),
                KBEString(password),
                KBEBlob(create_account_data),
            ),
        )

        resp_wait_obj = WaitingRespMsgData(
            msg,
            resp_msgs=[msgspec.client.onCreateAccountResult.id],
            timeout=wait_seconds,
            future=Future(),
        )
        await self._send_msg(msg, resp_wait_obj)

        try:
            async with asyncio.timeout(resp_wait_obj.timeout):
                resp_msg = await resp_wait_obj.future
        except TimeoutError:
            self._waiting_resp_storage.pop_waiting_obj(resp_wait_obj.resp_msgs[0])

            err_text = (
                f"[{self}] There is no response. Waiting stopped by timeout "
                f"(client = '{self._tcp_msg_client}', msg = '{msg}')"
            )
            logger.warning(err_text)

            raise LoginappNoResponseError(err_text)

        assert resp_msg.id == msgspec.client.onCreateAccountResult.id

        res = OnCreateAccountResultMsgParser().parse(resp_msg)
        assert res.result is not None
        pd = res.result

        if res.result.ret_code != ServerError.SUCCESS:
            return CreateAccountResult(
                False, CreateAccountResultData(pd.ret_code, pd.data)
            )

        return CreateAccountResult(True, CreateAccountResultData(pd.ret_code, pd.data))

    async def reqAccountResetPassword(
        self,
        account_name: AccountName,
        wait_seconds: float = 5 * SECOND,
    ) -> ReqAccountResetPasswordResult:
        """Запрос на сброс пароля аккаунта (Loginapp::reqAccountResetPassword).

        Args:
            account_name: Имя аккаунта
            wait_seconds: Таймаут ожидания ответа в секундах

        Returns:
            Result: результат операции. success=True означает, что запрос принят
                    и сервер отправит письмо для сброса пароля на email аккаунта.
                    В случае ошибки в result будет SERVER_ERROR_CODE.

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        self._check_client_is_started()

        msg = Message.create(
            msgspec.loginapp.reqAccountResetPassword,
            values=(KBEString(account_name),),
        )

        resp_wait_obj = WaitingRespMsgData(
            msg,
            resp_msgs=[msgspec.client.onReqAccountResetPasswordCB.id],
            timeout=wait_seconds,
            future=Future(),
        )
        await self._send_msg(msg, resp_wait_obj)

        try:
            async with asyncio.timeout(resp_wait_obj.timeout):
                resp_msg = await resp_wait_obj.future
        except TimeoutError:
            self._waiting_resp_storage.pop_waiting_obj(resp_wait_obj.resp_msgs[0])

            err_text = (
                f"[{self}] There is no response. Waiting stopped by timeout "
                f"(client = '{self._tcp_msg_client}', msg = '{msg}')"
            )
            logger.warning(err_text)

            raise LoginappNoResponseError(err_text)

        assert resp_msg.id == msgspec.client.onReqAccountResetPasswordCB.id

        res = OnReqAccountResetPasswordCBMsgParser().parse(resp_msg)

        if not res.success:
            return ReqAccountResetPasswordResult(
                success=False,
                result=ReqAccountResetPasswordResultData(res.result.ret_code),
                text=f"Failed to parse response: {res.text}",
            )

        ret_code = res.result.ret_code

        if ret_code != ServerError.SUCCESS:
            return ReqAccountResetPasswordResult(
                success=False,
                result=ReqAccountResetPasswordResultData(res.result.ret_code),
                text=f"Account password reset failed with code: {ret_code.name}",
            )

        logger.info(
            "[%s] Account password reset request accepted for account '%s'",
            self,
            account_name,
        )

        return ReqAccountResetPasswordResult(
            success=True,
            result=ReqAccountResetPasswordResultData(res.result.ret_code),
            text="Account password reset request accepted",
        )

    async def importClientMessages(self) -> None:
        pass

    async def importServerErrorsDescr(self) -> None:
        pass

    async def importClientSDK(self) -> None:
        pass

    async def onClientActiveTick(self, wait_seconds: int) -> OnClientActiveTickResult:
        """Отправляет серверу сигнал, что клиент активен и ожидает подтверждения.

        Отправляет сообщение Loginapp::onClientActiveTick и ожидает ответ
        Client::onAppActiveTickCB от сервера.

        Raises:
            LoginappIsNotStartedError: Если клиент не запущен
            LoginappConnectionError: Если не удалось отправить сообщение
            LoginappNoResponseError: Если нет ответа от сервера в течение таймаута

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        self._check_client_is_started()

        msg = Message.create(msgspec.loginapp.onClientActiveTick, ())

        resp_wait_obj = WaitingRespMsgData(
            msg,
            resp_msgs=[msgspec.client.onAppActiveTickCB.id],
            timeout=wait_seconds,
            future=Future(),
        )

        await self._send_msg(msg, resp_wait_obj)

        try:
            async with asyncio.timeout(resp_wait_obj.timeout):
                _resp_msg = await resp_wait_obj.future

            logger.debug("[%s] Received Loginapp::onAppActiveTickCB response", self)
        except TimeoutError:
            self._waiting_resp_storage.pop_waiting_obj(resp_wait_obj.resp_msgs[0])

            err_text = (
                f"[{self}] No Loginapp::onAppActiveTickCB response from server. "
                f"Waiting stopped by timeout (client = '{self._tcp_msg_client}')"
            )
            logger.warning(err_text)
            raise LoginappNoResponseError(err_text)

        return OnClientActiveTickResult(
            success=True, result=OnClientActiveTickResultData(resp_dt=datetime.now())
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    __repr__ = __str__
