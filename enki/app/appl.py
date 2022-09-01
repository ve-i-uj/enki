"""KBEngine client application."""

import asyncio
import collections
import logging
from dataclasses import dataclass
import sys
from typing import Optional, Any

from tornado import iostream

from enki import exception, kbeclient, settings, command, kbeenum, descr
from enki.misc import devonly, runutil
from enki.interface import IApp, IResult

from . import handlers, managers
from .handlers import IHandler

logger = logging.getLogger(__name__)


@dataclass
class AppStartResult(IResult):
    success: bool
    text: str = ''


@dataclass
class _ReloginData:
    rnd_uuid: int = 0
    entity_id: int = 0

    @property
    def is_initialized(self) -> bool:
        return bool(self.rnd_uuid and self.entity_id)


class App(IApp):
    """KBEngine client application."""

    def __init__(self, login_app_addr: settings.AppAddr,
                 server_tick_period: float):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._login_app_addr = login_app_addr
        self._server_tick_period = server_tick_period
        self._client: Optional[kbeclient.Client] = None

        self._entity_mgr = managers.EntityMgr(app=self)
        self._sys_mgr = managers.SysMgr(app=self)
        self._space_data_mgr = managers.SpaceDataMgr()

        self._commands: list[command.Command] = []
        self._commands_msg_ids: set[int] = set()

        self._handlers: dict[int, IHandler] = {}
        self._handlers.update({
            i: h(self._entity_mgr) for i, h in handlers.E_HANDLER_CLS_BY_MSG_ID.items()
        })
        self._handlers.update({
            i: h(self._space_data_mgr) for i, h in handlers.S_HANDLER_CLS_BY_MSG_ID.items()
        })

        self._space_data: dict[int, dict[str, str]] = collections.defaultdict(dict)
        self._relogin_data = _ReloginData()

        logger.info('[%s] The application has been initialized', self)

    @property
    def client(self) -> Optional[kbeclient.Client]:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        return self._client

    async def stop(self):
        """Stop the application."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        if self._client is None:
            return
        await self._client.stop()
        self._client = None
        logger.info('[%s] The application has been stoped', self)

    async def start(self, account_name: str, password: str) -> IResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._client = kbeclient.Client(self._login_app_addr)
        try:
            await self._client.start()
        except iostream.StreamClosedError as err:
            text: str = f'The client cannot connect to the '\
                        f'{self._login_app_addr.host}:{self._login_app_addr.port}. Exit'
            return AppStartResult(False, text)
        self._client.set_msg_receiver(self)

        cmd = command.loginapp.HelloCommand(
            kbe_version='2.5.10',
            script_version='0.1.0',
            encrypted_key=b'',
            client=self._client
        )
        res = await self.send_command(cmd)
        if not res.success:
            text: str = f'The client cannot connect to the ' \
                        f'{self._login_app_addr.host}:{self._login_app_addr.port} ' \
                        f'({res.text}). Exit'
            return AppStartResult(False, text)

        cmd = command.loginapp.LoginCommand(
            client_type=kbeenum.ClientType.UNKNOWN, client_data=b'',
            account_name=account_name, password=password, force_login=False,
            client=self._client
        )
        login_result: command.loginapp.LoginCommandResult = await self.send_command(cmd)
        if login_result.ret_code != kbeenum.ServerError.SUCCESS:
            err_msg = login_result.data.decode()
            text = f'The client cannot connect to LoginApp ' \
                   f'(code = {login_result.ret_code}, msg = {err_msg})'
            return AppStartResult(False, text)

        # We got the BaseApp address and do not need the LoginApp connection
        # anymore
        await self._client.stop()
        self._client = None

        baseapp_addr = settings.AppAddr(
            host=login_result.host,
            port=login_result.tcp_port
        )
        self._client = kbeclient.Client(baseapp_addr)
        try:
            await self._client.start()
        except iostream.StreamClosedError as err:
            text: str = f'The client cannot connect to the "{baseapp_addr}". Exit'
            return AppStartResult(False, text)
        self._client.set_msg_receiver(self)

        cmd = command.baseapp.HelloCommand(
            kbe_version='2.5.10',
            script_version='0.1.0',
            encrypted_key=b'',
            client=self._client
        )
        res = await self.send_command(cmd)
        if not res.success:
            return AppStartResult(False, res.text)

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
            return AppStartResult(False, res.text)
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
            return AppStartResult(False, res.text)

        self._sys_mgr.start_server_tick(self._server_tick_period)

        logger.info('[%s] The application has been succesfully connected to '
                    'the KBEngine server', self)
        return AppStartResult(True, '')

    def on_receive_msg(self, msg: kbeclient.Message) -> bool:
        logger.info('[%s] %s', self, devonly.func_args_values())
        # TODO: [27.07.2021 burov_alexey@mail.ru]:
        # Переделать сам подход с командами
        if msg.id in self._commands_msg_ids:
            i = 0
            for i, cmd in enumerate(self._commands):
                # It returns true if it handles msg
                if cmd.on_receive_msg(msg):
                    self._commands_msg_ids.remove(msg.id)
                    break
            self._commands[:] = self._commands[:i] + self._commands[i+1:]
            return True

        handler = self._handlers.get(msg.id)
        if handler is None:
            logger.warning(f'[{self}] There is NO handler for the message '
                           f'"{msg.name}"')
            return False

        result: handlers.HandlerResult = handler.handle(msg)

        return result.success

    def on_end_receive_msg(self):
        for cmd in self._commands:
            cmd.on_end_receive_msg()

        async def stop_app():
            await self.stop()
            await runutil.shutdown()

        asyncio.ensure_future(stop_app())

    async def send_command(self, cmd: command.Command) -> Any:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._commands_msg_ids.update(cmd.waited_ids)
        self._commands.append(cmd)
        res = await cmd.execute()
        return res

    def send_message(self, msg: kbeclient.Message):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        if self._client is None:
            logger.warning(f'[{self}] There is no client! The message cannot '
                           f'be sent (msg = {msg}')
            return
        asyncio.create_task(self._client.send(msg))

    def set_relogin_data(self, rnd_uuid: int, entity_id: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._relogin_data.rnd_uuid = rnd_uuid
        self._relogin_data.entity_id = entity_id

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'
