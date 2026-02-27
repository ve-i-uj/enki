from __future__ import annotations

import asyncio
import logging
from asyncio import Task
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

from enki import msgspec, settings
from enki.kbeenum import ComponentType
from enki.kbetype.decoders.custom_decoders import KBEEntityId
from enki.kbetype.pytypes.basic_data_types import KBEBlob, KBEString
from enki.misc import devonly
from enki.misc.result import Result
from enki.misc.startable import IStartable
from enki.msg.imsg import IClientMsgReceiver
from enki.msg.message import Message
from enki.msg.msg_client import TcpMsgClient
from enki.msg_parser.client_msg_parser import (
    OnHelloCBMsgParser,
    OnScriptVersionNotMatchMsgParser,
    OnVersionNotMatchMsgParser,
)
from enki.settings import SECOND

if TYPE_CHECKING:
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


class BaseappConnectionError(Exception):
    pass


class BaseappNoResponseError(Exception):
    pass


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
class BaseappCheckVersionResult(Result):
    success: bool
    result: CheckVersionResultData
    text: str = ""


@dataclass(frozen=True)
class BaseappLoginResult(Result):
    success: bool
    result: Any
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
    ) -> None:
        self._tcp_msg_client = TcpMsgClient(
            baseapp_addr,
            ComponentType.CLIENT,
            on_end_receive_msg_cb=self._on_end_receive_msg_cb,
        )
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
        self, account_name: str, password: str
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
        # А приложение на этой точке считается запущенным. Если логин к Baseapp
        # будет неудачным, то это уже будет обработано в общем обработчике
        # сообщений приложения.

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

        self._start_receiving_msgs()

        return BaseappLoginResult(success=True, result=None)

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

    def _on_end_receive_msg_cb(self) -> None:
        """Колбэк на окончание получения данных от сервера."""
        logger.debug("[%s] %s", self, devonly.func_args_values())

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

    async def reqAccountBindEmail(
        self,
        entity_id: int,
        password: str,
        email: str,
        wait_seconds: int = 5 * SECOND,
    ) -> Result:
        """Привязать email к аккаунту (Baseapp::reqAccountBindEmail).

        Реализация адаптирована из `ReqAccountBindEmailCommand`, но использует
        подход ожидания ответа как в методах `hello` и `login`.
        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        msg = Message.create(
            msgspec.baseapp.reqAccountBindEmail,
            values=(
                KBEEntityId(entity_id),
                KBEString(password),
                KBEString(email),
            ),
        )

        resp_wait_obj = WaitingRespMsgData(
            msg=msg,
            resp_msgs=[msgspec.client.onReqAccountBindEmailCB.id],
            timeout=wait_seconds,
            future=Future(),
        )
        await self._send_msg(msg, resp_wait_obj)

        try:
            async with asyncio.timeout(resp_wait_obj.timeout):
                resp_msg = await resp_wait_obj.future
        except TimeoutError:
            self._waiting_resp_storage.pop_waiting_obj(
                resp_wait_obj.resp_msgs[0]
            )

            err_text = (
                f"[{self}] There is no response. Waiting stopped by timeout "
                f"(client = '{self._tcp_msg_client}', msg = '{msg}')"
            )
            logger.warning(err_text)

            raise LoginappNoResponseError(err_text)

        res = OnReqAccountBindEmailCBMsgParser().parse(resp_msg)
        assert res.result is not None
        pd = res.result

        if pd.ret_code != ServerError.SUCCESS:
            err_text = str(pd.ret_code)
            logger.info("[%s] Account email binding failed: %s", self, err_text)
            return Result(success=False, result=pd.ret_code, text=err_text)

        logger.info("[%s] Account email binding succeeded: %s", self)
        return Result(success=True, result=pd.ret_code)
