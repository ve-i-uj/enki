from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, NoReturn, TypeAlias

from enki import msgspec
from enki.kbeenum import ClientType, ComponentType, ServerError
from enki.kbetype.pytypes.basic_data_types import KBEBlob, KBEInt8, KBEString
from enki.misc import devonly
from enki.misc.result import Result
from enki.misc.startable import IStartable
from enki.msg.imsg import IClientMsgReceiver
from enki.msg.message import Message
from enki.msg.msg_client import TcpMsgClient
from enki.msg_parser.client_msg_parser.client_msg_pasrser import (
    OnCreateAccountResultMsgParser,
    OnHelloCBMsgParser,
    OnLoginFailedMsgParser,
    OnLoginSuccessfullyMsgParser,
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
            onLoginFailed_res = OnLoginFailedMsgParser().parse(
                resp_msg
            )
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
