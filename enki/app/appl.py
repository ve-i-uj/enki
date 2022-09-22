"""KBEngine client application."""

from __future__ import annotations

import asyncio
import collections
import logging
from dataclasses import dataclass
from typing import Callable, Optional, Any, Type

from enki import msgspec, kbeclient, command, kbeenum
from enki.dcdescr import EntityDesc
from enki.misc import devonly
from enki.interface import IApp, IEntity, IKBEClientEntity, IMessage, IResult, IHandler, AppAddr
from enki.command import Command
from tools.data import default_kbenginexml

from . import handlers, managers

logger = logging.getLogger(__name__)


@dataclass
class AppStartResult(IResult):
    success: bool
    result: Any = None
    text: str = ''


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
            if not self.is_connected:
                logger.info(f"The function \"{func.__name__}\" wouldn't be called "\
                            f"(the client is not connected)")
                feature = asyncio.get_running_loop().create_future()
                feature.set_result(None)
                return asyncio.get_running_loop().create_future()
            return func(self, *args, **kwargs)

        return wrapper

    def wrapper(self: App, *args, **kwargs) -> Any:
        if not self.is_connected:
            logger.info(f"The function \"{func.__name__}\" wouldn't be called "\
                        f"(the client is not connected)")
            return None
        return func(self, *args, **kwargs)

    return wrapper


class App(IApp):
    """KBEngine client application."""

    def __init__(self, login_app_addr: AppAddr,
                 server_tick_period: float,
                 entity_desc_by_uid: dict[int, EntityDesc],
                 entity_impl_by_uid: dict[int, Type[IEntity]],
                 kbenginexml: default_kbenginexml.root):
        logger.debug('')
        self._kbenginexml = kbenginexml
        self._wait_until_stop_future = asyncio.get_event_loop().create_future()

        self._login_app_addr = login_app_addr
        self._server_tick_period = server_tick_period
        self._client: Optional[kbeclient.Client] = None

        self._entity_mgr = managers.EntityMgr(
            self, entity_desc_by_uid, entity_impl_by_uid
        )
        self._sys_mgr = managers.SysMgr(app=self)
        self._space_data_mgr = managers.SpaceDataMgr()
        self._stream_data_mgr = managers.StreamDataMgr()

        self._commands_by_msg_id: dict[int, list[Command]] = collections.defaultdict(list)

        self._handlers: dict[int, IHandler] = {}
        self._handlers.update({
            i: h(self._entity_mgr) for i, h in handlers.E_HANDLER_CLS_BY_MSG_ID.items()
        })
        self._handlers.update({
            i: h(self._space_data_mgr) for i, h in handlers.SD_HANDLER_CLS_BY_MSG_ID.items()
        })
        self._handlers.update({
            i: h(self._stream_data_mgr) for i, h in handlers.STREAM_HANDLER_CLS_BY_MSG_ID.items()
        })
        self._handlers[msgspec.app.client.onKicked.id] = handlers.OnKickedHandler(app=self)

        self._space_data: dict[int, dict[str, str]] = collections.defaultdict(dict)
        self._relogin_data = _ReloginData()

        self._connected: bool = False
        self._stopping: bool = False

        logger.info('[%s] The application has been initialized', self)

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def client(self) -> kbeclient.Client:
        assert self._client is not None
        return self._client

    async def stop(self):
        """Stop the application."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        if self._stopping or self._client is None:
            return
        self._stopping = True

        for cmds in self._commands_by_msg_id.values():
            for cmd in cmds:
                cmd.on_end_receive_msg()
        self._commands_by_msg_id.clear()

        await self._sys_mgr.stop_server_tick()
        self._client.stop()
        self._connected = False
        self._client = None
        if not self._wait_until_stop_future.done():
            self._wait_until_stop_future.set_result(None)

        logger.info('[%s] The application has been stopped', self)

    async def start(self, account_name: str, password: str) -> IResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._client = kbeclient.Client(self._login_app_addr)
        res = await self._client.start()
        if not res.success:
            text: str = f'The client cannot connect to the '\
                        f'{self._login_app_addr.host}:{self._login_app_addr.port} ' \
                        f'(err = {res.text})'
            await self.stop()
            return AppStartResult(False, text=text)
        self._client.set_msg_receiver(self)

        self._connected = True
        self._stopping = False

        cmd = command.loginapp.HelloCommand(
            kbe_version='2.5.10',
            script_version='0.1.0',
            encrypted_key=b'',
            client=self._client
        )
        res = await self.send_command(cmd)
        if not res.success:
            text: str = f'The client cannot connect to the ' \
                        f'{self._login_app_addr} ' \
                        f'(err = {res.text})'
            await self.stop()
            return AppStartResult(False, text=text)

        cmd = command.loginapp.LoginCommand(
            client_type=kbeenum.ClientType.UNKNOWN, client_data=b'',
            account_name=account_name, password=password, force_login=False,
            client=self._client
        )
        login_res: command.loginapp.LoginCommandResult = await self.send_command(cmd)
        if not login_res.success:
            text = f'The client cannot connect to LoginApp ' \
                   f'(code = {login_res.result.ret_code}, msg = {login_res.text})'
            await self.stop()
            return AppStartResult(False, text=text)

        # We got the BaseApp address and do not need the LoginApp connection
        # anymore
        self._client.stop()
        self._client = None

        baseapp_addr = AppAddr(
            host=login_res.result.host,
            port=login_res.result.tcp_port
        )
        client = kbeclient.Client(baseapp_addr)
        res = await client.start()
        if not res.success:
            text: str = f'The client cannot connect to the "{baseapp_addr}". Exit'
            await self.stop()
            return AppStartResult(False, text=text)

        self._client = client
        self._client.set_msg_receiver(self)
        self._connected = True

        cmd = command.baseapp.HelloCommand(
            kbe_version='2.5.10',
            script_version='0.1.0',
            encrypted_key=b'',
            client=self._client
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
        res: IResult = await self.send_command(cmd)
        if not res.success:
            logger.error(res.text)
            await self.stop()
            return AppStartResult(False, text=res.text)
        # The message "onLoginBaseappFailed" cannot be received because
        # the server closes the connection too fast. Let's do another check.
        cmd = command.baseapp.HelloCommand(
            kbe_version='2.5.10',
            script_version='0.1.0',
            encrypted_key=b'',
            client=self._client
        )
        resp: IResult = await self.send_command(cmd)
        if not resp.success:
            await self.stop()
            return AppStartResult(False, text=res.text)

        self._sys_mgr.start_server_tick(self._server_tick_period)

        logger.info('[%s] The application has been succesfully connected to '
                    'the KBEngine server', self)
        return AppStartResult(True)

    @if_app_is_connected
    def on_receive_msg(self, msg: IMessage) -> bool:
        logger.info('[%s] %s', self, devonly.func_args_values())

        async def _on_receive_msg(msg: IMessage) -> bool:
            if msg.id in self._commands_by_msg_id:
                cmds = self._commands_by_msg_id[msg.id]
                assert cmds
                cmd = cmds[0]
                cmd.on_receive_msg(msg)
                return True

            handler = self._handlers.get(msg.id)
            if handler is None:
                logger.warning(f'[{self}] There is NO handler for the message '
                            f'"{msg.name}"')
                return False

            result = handler.handle(msg)
            return result.success

        asyncio.create_task(_on_receive_msg(msg))

        return True

    @if_app_is_connected
    def on_end_receive_msg(self):
        self._connected = False
        asyncio.create_task(self.stop())

    @if_app_is_connected
    async def send_command(self, cmd: Command) -> Any:
        logger.info('[%s] %s', self, devonly.func_args_values())
        for msg_id in cmd.waiting_for_ids:
            self._commands_by_msg_id[msg_id].append(cmd)
        res = await cmd.execute()
        for msg_id in cmd.waiting_for_ids:
            cmds = self._commands_by_msg_id[msg_id]
            assert cmds
            cmds.pop()
            if not cmds:
                self._commands_by_msg_id.pop(msg_id)
        return res

    @if_app_is_connected
    def send_message(self, msg: kbeclient.Message):
        logger.info('[%s] %s', self, devonly.func_args_values())
        assert self._client is not None
        asyncio.create_task(self._client.send(msg))

    def get_relogin_data(self) -> tuple[int, int]:
        return self._relogin_data.rnd_uuid, self._relogin_data.entity_id

    def set_relogin_data(self, rnd_uuid: int, entity_id: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._relogin_data.rnd_uuid = rnd_uuid
        self._relogin_data.entity_id = entity_id

    def get_kbenginexml(self) -> default_kbenginexml.root:
        return self._kbenginexml

    def wait_until_stop(self) -> asyncio.Future:
        return self._wait_until_stop_future

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(client={self._client})'
