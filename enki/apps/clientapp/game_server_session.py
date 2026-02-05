import enum
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from enki import msgspec
from enki.apps.clientapp.iclientapp import IGameServerSession
from enki.kbeenum import ClientType, ComponentType
from enki.kbetype.pytypes.basic_data_types import KBEBlob, KBEString
from enki.misc import devonly
from enki.misc.result import Result
from enki.msg.message import Message
from enki.msg.msg_client import TcpMsgClient
from enki.net.addr import Addr

logger = logging.getLogger(__name__)


class LoginappSyncStatusEnum(Enum):
    INIT = enum.auto()
    LOGINAPP_IS_REACHABLE = enum.auto()
    LOGINAPP_IS_NOT_REACHABLE = enum.auto()
    LOGINAPP_KBE_VERSION_IS_NOT_MATCHED = enum.auto()
    LOGINAPP_KBE_SCRIPTS_VERSION_IS_NOT_MATCHED = enum.auto()


class BaseappSyncStatusEnum(Enum):
    INIT = enum.auto()
    BASEAPP_IS_REACHABLE = enum.auto()
    BASEAPP_IS_NOT_REACHABLE = enum.auto()
    BASEAPP_KBE_VERSION_IS_NOT_MATCHED = enum.auto()
    BASEAPP_KBE_SCRIPTS_VERSION_IS_NOT_MATCHED = enum.auto()


class ConnectedKBEComponentEnum(Enum):
    LOGINAPP = ComponentType.LOGINAPP
    BASEAPP = ComponentType.BASEAPP


@dataclass
class CompSyncStatus:
    status: LoginappSyncStatusEnum
    current_component: ConnectedKBEComponentEnum


@dataclass
class LoginappSyncStatus:
    status: LoginappSyncStatusEnum
    current_component: ConnectedKBEComponentEnum = (
        ConnectedKBEComponentEnum.LOGINAPP
    )


@dataclass
class BasepappSyncStatus:
    status: LoginappSyncStatusEnum
    current_component: ConnectedKBEComponentEnum = (
        ConnectedKBEComponentEnum.LOGINAPP
    )


class GameServerSession(IGameServerSession):
    """Реализации сессии с игровым сервером.

    Keep alive, переподключение к серверу, ::hello.
    """

    def __init__(
        self,
        loginapp_addr: Addr,
        kbe_version: str,
        script_version: str,
        encrypted_key: bytes,
    ) -> None:
        self._loginapp_addr = loginapp_addr
        self._loginapp_client: TcpMsgClient | None = None

        self._kbe_version = kbe_version
        self._script_version = script_version
        self._encrypted_key = encrypted_key

    def _on_end_receive_msg_cb(self) -> None:
        """Колбэк на окончание получения данных от сервера."""
        logger.debug("[%s] %s", self, devonly.func_args_values())

    async def start(self) -> Result:
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
        return Result(success=True, result=None)

    async def _check_loginapp(self) -> GameServerSessionSyncStatusResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        assert self._loginapp_client is not None

        msg = Message.create(
            msgspec.loginapp.hello,
            values=(
                KBEString(self._kbe_version),
                KBEString(self._script_version),
                KBEBlob(self._encrypted_key),
            ),
        )
        success = await self._loginapp_client.send_msg(msg)
        if not success:
            err_text = (
                f"[{self}] The message is not sent (client = '{self._loginapp_client}', "
                f"msg = '{msg}')"
            )
            logger.warning(err_text)
            return GameServerSessionSyncStatusResult(
                success=False,
                result=GameServerSessionSyncStatus.LOGINAPP_IS_NOT_REACHABLE,
                text=err_text,
            )

        return GameServerSessionSyncStatusResult()

    async def check_game_server_sync(
        self,
    ) -> GameServerSessionSyncStatusResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        assert self._loginapp_client is not None

        await self._check_loginapp()

        resp_msg = await self._loginapp_client.wait_only_first_resp_msg(
            5 * SECOND
        )
        if resp_msg is None:
            err_text = (
                f"[{self}] There is no response. Waiting stopped by timeout "
                f"(client = '{self._loginapp_client}', msg = '{self._msg}')"
            )
            logger.warning(err_text)
            return HelloCommandResult(success=False, text=err_text)

        if resp_msg.id == msgspec.client.onVersionNotMatch.id:
            onVersionNotMatch_res = OnVersionNotMatchMsgParser().parse(resp_msg)
            assert onVersionNotMatch_res.result is not None
            onVersionNotMatch_pd = onVersionNotMatch_res.result  # noqa: N806

            plugin_kbe_version = msg.get_values()[0]
            server_kbe_version = onVersionNotMatch_pd.kbe_version
            msg = (
                f'Plugin designed for KBEngine version "{plugin_kbe_version}". '
                f'But actual KBEngine version is "{server_kbe_version}"'
            )
            return GameServerSessionSyncStatusResult(success=False, text=msg)

        if resp_msg.id == msgspec.client.onScriptVersionNotMatch.id:
            onScriptVersionNotMatch_res = (  # noqa: N806
                OnScriptVersionNotMatchMsgParser().parse(resp_msg)
            )
            assert onScriptVersionNotMatch_res.result is not None
            onScriptVersionNotMatch_pd = onScriptVersionNotMatch_res.result

            plugin_assets_version = msg.get_values()[1]
            server_assets_version = onScriptVersionNotMatch_pd.assets_version
            msg = (
                f'Plugin designed for assets version "{plugin_assets_version}". '
                f'But actual script version is "{server_assets_version}"'
            )
            return GameServerSessionSyncStatusResult(success=False, text=msg)

        onHelloCB_res = OnHelloCBMsgParser().parse(resp_msg)  # noqa: N806
        assert onHelloCB_res.result is not None

        onHelloCB_pd = onHelloCB_res.result  # noqa: N806

        return GameServerSessionSyncStatusResult(
            success=True,
            result=HelloCommandResultData(
                onHelloCB_pd.kbe_version,
                onHelloCB_pd.assets_version,
                onHelloCB_pd.protocol_md5,
                onHelloCB_pd.entity_def_md5,
                onHelloCB_pd.component_type,
            ),
        )

    def login_to_game_server(self, credentials: dict[str, Any]) -> bool:
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
            "The LoginApp login is successful. The BaseApp address is %s",
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
            text = (
                f'Baseapp hello is not successful. Reason: "{hello_res.text}")'
            )
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

    def start_game_server_sync(self) -> bool:
        return False
