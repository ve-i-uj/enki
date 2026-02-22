"""KBEngine client application."""

from __future__ import annotations

import asyncio
import collections
import enum
import logging
from asyncio import Task
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, Callable, ClassVar

from enki import command, kbeenum, msgspec
from enki.command.baseapp import (
    ReqAccountBindEmailCommand,
    ReqAccountNewPasswordCommand,
)
from enki.misc import devonly
from enki.misc.result import Result
from enki.net.addr import Addr

if TYPE_CHECKING:
    from enki import default_kbenginexml
    from enki.kbeentity.entity_descr import EntityDesc
    from enki.msg.message import Message

    from .entity_sub_system.ientity_serializer import IEntityRPCSerializer

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AppStartResult(Result):
    success: bool
    result: Any = None
    text: str = ""


@dataclass
class _ReloginData:
    rnd_uuid: int = 0
    entity_id: int = 0

    @property
    def is_initialized(self) -> bool:
        return bool(self.rnd_uuid and self.entity_id)


# TODO: [2022-09-22 09:06 burov_alexey@mail.ru]:
# Так ломается тип функции. Это можно надевать только на тех, кто возвращает None
def if_app_is_connected(func: Callable) -> Callable:
    if asyncio.iscoroutinefunction(func):

        def wrapper(self: App, *args, **kwargs) -> Any:
            if self.state not in _AppStateEnum.get_working_states():
                logger.info(
                    f'The function "{func.__name__}" wouldn\'t be called '
                    f"(the client is not connected)"
                )
                future = asyncio.get_running_loop().create_future()
                future.set_result(None)
                return asyncio.get_running_loop().create_future()

            return func(self, *args, **kwargs)

        return wrapper

    def wrapper(self: App, *args, **kwargs) -> Any:
        if self.state not in _AppStateEnum.get_working_states():
            logger.info(
                f'The function "{func.__name__}" wouldn\'t be called '
                f"(the client is not connected)"
            )
            return None

        return func(self, *args, **kwargs)

    return wrapper


class ClientStub(MsgTCPClient):
    def set_msg_receiver(self, receiver: IClientMsgReceiver) -> None:
        logger.info("The function does nothing (It'a client stub)")

    async def send(self, msg: Message) -> None:
        logger.info("The function does nothing (It'a client stub)")

    def start(self) -> Result:
        return Result(
            False, None, "The function does nothing (It'a client stub)"
        )

    def stop(self) -> None:
        logger.info("The function does nothing (It'a client stub)")


# TODO: [2023-01-16 20:32 burov_alexey@mail.ru]:
# Нужно переделывать состояния. Ввести то, к чему подключается
class _AppStateEnum(enum.Enum):
    NOT_INITED = enum.auto()
    INITED = enum.auto()
    STARTING = enum.auto()
    CONNECTED = enum.auto()
    DISCONNECTED = enum.auto()
    STOPPING = enum.auto()
    STOPPED = enum.auto()

    @staticmethod
    def get_working_states() -> tuple[_AppStateEnum, ...]:
        return (_AppStateEnum.STARTING, _AppStateEnum.CONNECTED)


class App:
    """KBEngine client application."""

    _NEVER_TICK_TIME: ClassVar = datetime.now(timezone.utc) - timedelta(
        days=9999
    )

    def __init__(
        self,
        login_app_addr: Addr,
        entity_desc_by_uid: dict[int, EntityDesc],
        entity_serializer_by_uid: dict[int, type[IEntityRPCSerializer]],
        kbenginexml: default_kbenginexml.root,
        server_tick_period: float,
    ) -> None:
        """server_tick_period - частота, с которой отправляется onClientActiveTick,
            это какая-то настройка сервера в конфиге, но сходу не нашёл.
        entity_desc_by_uid - это описание типа (какие есть свойства, методы и т.д.),
        game_entity_by_type_name - это нагенеренные игровые сущности (классы),.
        """
        logger.debug("")
        self._state = _AppStateEnum.NOT_INITED

        self._wait_until_stop_future = asyncio.get_event_loop().create_future()

        self._login_app_addr = login_app_addr
        self._client = ClientStub(
            self._login_app_addr, msgspec.client.SPEC_BY_ID
        )

        self._server_tick_period = server_tick_period
        self._last_server_tick_time: datetime = self._NEVER_TICK_TIME
        self._server_tick_task: Task | None = None

        self._space_data_mgr = SpaceDataMgr()
        self._stream_data_mgr = StreamDataMgr()

        self._commands_by_msg_id: dict[int, list[TCPCommand]] = (
            collections.defaultdict(list)
        )

        self._handlers: dict[int, Handler] = {}
        entity_helper = EntityHelper(
            entity_desc_by_uid, entity_serializer_by_uid, kbenginexml
        )
        self._handlers.update(
            {
                i: h(entity_helper)
                for i, h in handlers.E_HANDLER_CLS_BY_MSG_ID.items()
            }
        )
        # Нужно подменить хэндлеры для сообщений, для которых нужно взаимодействовать
        # с приложением (релогин, пересылка сообщений)
        self._handlers[msgspec.client.onUpdatePropertys.id] = (
            OnUpdatePropertysClientAppHandler(entity_helper, self)
        )
        self._handlers[msgspec.client.onUpdatePropertysOptimized.id] = (
            OnUpdatePropertysOptimizedClientAppHandler(entity_helper, self)
        )
        self._handlers[msgspec.client.onCreatedProxies.id] = (
            OnCreatedProxiesClientAppHandler(entity_helper, self)
        )
        self._handlers[msgspec.client.onEntityEnterWorld.id] = (
            OnEntityEnterWorldClientAppHandler(entity_helper, self)
        )

        self._handlers[msgspec.client.onKicked.id] = OnKickedHandler(app=self)

        self._handlers.update(
            {
                i: h(self._space_data_mgr)
                for i, h in handlers.SD_HANDLER_CLS_BY_MSG_ID.items()
            }
        )
        self._handlers.update(
            {
                i: h(self._stream_data_mgr)
                for i, h in handlers.STREAM_HANDLER_CLS_BY_MSG_ID.items()
            }
        )

        self._space_data: dict[int, dict[str, str]] = collections.defaultdict(
            dict
        )
        self._relogin_data = _ReloginData()

        self._state = _AppStateEnum.INITED

        self._pending_msgs_by_entity_id: dict[int, list[Message]] = (
            collections.defaultdict(list)
        )

        logger.info("[%s] The application has been initialized", self)

    @property
    def state(self) -> _AppStateEnum:
        return self._state

    @property
    def is_connected(self) -> bool:
        """The application has been connected to the server."""
        return self._state == _AppStateEnum.CONNECTED

    # TODO: [2025-09-04 11:50 burov_alexey@mail.ru]:
    # Непонятно зачем кому-то отдавать клиент. Скорей всего только частный
    # атрибут должен быть.

    # # TODO: [2022-11-13 09:57 burov_alexey@mail.ru]:
    # # Возможно стоит переделать логику, чтобы не нужно было колдовать с TCPClient, IClient
    # @property
    # def client(self) -> MsgTCPClient:
    #     """The client connected to the server."""
    #     return self._client

    async def stop(self) -> None:
        """Stop the application."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        if self._state not in (
            _AppStateEnum.CONNECTED,
            _AppStateEnum.DISCONNECTED,
        ):
            return
        self._state = _AppStateEnum.STOPPING

        for cmds in self._commands_by_msg_id.values():
            for cmd in cmds:
                cmd.on_end_receive_msg()
        self._commands_by_msg_id.clear()

        if self._server_tick_task is not None:
            self._server_tick_task.cancel()
            self._server_tick_task = None

        self._client.stop()
        self._client = ClientStub(
            self._login_app_addr, msgspec.client.SPEC_BY_ID
        )
        if not self._wait_until_stop_future.done():
            self._wait_until_stop_future.set_result(None)

        self._state = _AppStateEnum.STOPPED
        logger.info("[%s] The application has been stopped", self)

    async def connect_to_loginapp(self) -> AppStartResult:
        self._state = _AppStateEnum.STARTING
        self._client = MsgTCPClient(
            self._login_app_addr, msgspec.client.SPEC_BY_ID
        )
        res = await self._client.start()
        if not res.success:
            text: str = (
                f"The client cannot connect to the "
                f"{self._login_app_addr.ip_addr}:{self._login_app_addr.port} "
                f"(err = {res.text})"
            )
            await self.stop()
            return AppStartResult(False, text=text)
        self._client.set_msg_receiver(self)

        cmd = command.loginapp.HelloCommand(
            kbe_version="2.5.10",
            script_version="0.1.0",
            encrypted_key=b"",
            client=self._client,
        )
        res = await self.send_command(cmd)
        if not res.success:
            text: str = (
                f"The client cannot connect to the "
                f"{self._login_app_addr} "
                f"(err = {res.text})"
            )
            await self.stop()
            return AppStartResult(False, text=text)

        return AppStartResult(True)

    async def start(self, account_name: str, password: str) -> Result:
        """Start the application."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        res = await self.connect_to_loginapp()
        if not res.success:
            return res

        cmd = command.loginapp.LoginCommand(
            client_type=kbeenum.ClientType.UNKNOWN,
            client_data=b"",
            account_name=account_name,
            password=password,
            force_login=False,
            client=self._client,
        )
        login_res: Result = await self.send_command(cmd)
        if not login_res.success:
            text = (
                f"The client cannot connect to LoginApp "
                f"(code = {login_res.result.ret_code}, msg = {login_res.text})"
            )
            await self.stop()
            return AppStartResult(False, text=text)

        # We got the BaseApp address and do not need the LoginApp connection
        # anymore
        self._client.stop()
        self._client = ClientStub(
            self._login_app_addr, msgspec.client.SPEC_BY_ID
        )

        baseapp_addr = Addr(
            ip_addr=login_res.result.host, port=login_res.result.tcp_port
        )
        client = MsgTCPClient(baseapp_addr, msgspec.client.SPEC_BY_ID)
        res = await client.start()
        if not res.success:
            text: str = f'The client cannot connect to the "{baseapp_addr}"'
            await self.stop()
            return AppStartResult(False, text=text)

        self._client = client
        self._client.set_msg_receiver(self)

        cmd = command.baseapp.HelloCommand(
            kbe_version="2.5.10",
            script_version="0.1.0",
            encrypted_key=b"",
            client=self._client,
        )
        res = await self.send_command(cmd)
        if not res.success:
            await self.stop()
            return AppStartResult(False, text=res.text)

        # This message starts the client-server communication. The server will
        # send many initial messages in the response. But it also can return
        # nothing (no server response and stop waiting by timeout).
        # Set the application receiver.
        cmd = command.baseapp.LoginBaseappCommand(
            self._client, account_name, password
        )
        res: Result = await self.send_command(cmd)
        if not res.success:
            logger.error(res.text)
            await self.stop()
            return AppStartResult(False, text=res.text)
        # The message "onLoginBaseappFailed" cannot be received because
        # the server closes the connection too fast. Let's do another check.
        cmd = command.baseapp.HelloCommand(
            kbe_version="2.5.10",
            script_version="0.1.0",
            encrypted_key=b"",
            client=self._client,
        )
        resp: Result = await self.send_command(cmd)
        if not resp.success:
            await self.stop()
            return AppStartResult(False, text=res.text)

        self._server_tick_task = asyncio.create_task(self._send_tick())

        self._state = _AppStateEnum.CONNECTED

        logger.info(
            "[%s] The application has been succesfully connected to "
            "the KBEngine server",
            self,
        )
        return AppStartResult(True)

    @if_app_is_connected
    def on_receive_msg(self, msg: Message) -> bool:
        logger.info("[%s] %s", self, devonly.func_args_values())
        asyncio.create_task(self._on_receive_msg(msg))
        return True

    async def _on_receive_msg(self, msg: Message) -> bool:
        if msg.id in self._commands_by_msg_id:
            cmds = self._commands_by_msg_id[msg.id]
            assert cmds
            cmd = cmds[0]
            cmd.on_receive_msg(msg)
            return True

        handler = self._handlers.get(msg.id)
        if handler is None:
            logger.warning(
                f'[{self}] There is NO handler for the message "{msg.name}"'
            )
            return False

        result = handler.handle(msg)
        return result.success

    @if_app_is_connected
    def on_end_receive_msg(self) -> None:
        if self._state == _AppStateEnum.STARTING:
            return
        self._state = _AppStateEnum.DISCONNECTED
        asyncio.create_task(self.stop())

    async def send_command(self, cmd: TCPCommand) -> Result:
        logger.info("[%s] %s", self, devonly.func_args_values())
        # The command will handle a disconnected client.
        # That's why it doesn't need to know if the client is connected or not.
        for msg_id in cmd.waiting_for_ids:
            self._commands_by_msg_id[msg_id].append(cmd)
        res = await cmd.execute()
        # When the application is stopping it cleans up self._commands_by_msg_id
        if self._commands_by_msg_id:
            for msg_id in cmd.waiting_for_ids:
                cmds = self._commands_by_msg_id[msg_id]
                assert cmds
                cmds.pop()
                if not cmds:
                    self._commands_by_msg_id.pop(msg_id)
        return res

    @if_app_is_connected
    def send_message(self, msg: Message) -> None:
        """Send the message to the server."""
        logger.info("[%s] %s", self, devonly.func_args_values())
        asyncio.create_task(self._client.send_msg(msg))

    def get_relogin_data(self) -> tuple[int, int]:
        return self._relogin_data.rnd_uuid, self._relogin_data.entity_id

    def set_relogin_data(self, rnd_uuid: int, entity_id: int) -> None:
        """Set data that is necessary for relogin of application."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._relogin_data.rnd_uuid = rnd_uuid
        self._relogin_data.entity_id = entity_id

    async def wait_until_stop(self) -> None:
        await self._wait_until_stop_future

    async def _send_tick(self) -> None:
        while self._state in _AppStateEnum.get_working_states():
            cmd = command.baseapp.OnClientActiveTickCommand(
                client=self.client,  # type: ignore
                timeout=self._server_tick_period,
            )
            res: Result = await self.send_command(cmd)
            if not res.success:
                logger.warning(f"[{self}] No connection with the server")
                self.on_end_receive_msg()
                return
            self._last_server_tick_time = datetime.datetime.now()
            await asyncio.sleep(self._server_tick_period)

    async def create_account(self, account_name: str, password: str) -> Result:
        cmd = ReqCreateAccountCommand(
            self.client, account_name, password, b"enki-create-account-data"
        )
        return await self.send_command(cmd)

    async def reset_password(self, account_name: str) -> Result:
        cmd = ReqAccountResetPasswordCommand(self.client, account_name)
        return await self.send_command(cmd)

    async def bind_account_email(
        self, entity_id: int, password: str, email: str
    ) -> Result:
        cmd = ReqAccountBindEmailCommand(
            self.client, entity_id, password, email
        )
        return await self.send_command(cmd)

    async def set_new_password(
        self, entity_id: int, oldpassword: str, newpassword: str
    ) -> Result:
        cmd = ReqAccountNewPasswordCommand(
            self.client, entity_id, oldpassword, newpassword
        )
        return await self.send_command(cmd)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(client={self._client}, state={self._state.name})"

    def add_pending_msg(self, entity_id: int, msg: Message) -> None:
        self._pending_msgs_by_entity_id[entity_id].append(msg)

    def resend_pending_msgs(self, entity_id: int) -> None:
        if entity_id in self._pending_msgs_by_entity_id:
            logger.debug("There are pending messages. Resend them ...")
            for msg in self._pending_msgs_by_entity_id[entity_id]:
                self.on_receive_msg(msg)
            self._pending_msgs_by_entity_id.pop(entity_id)
