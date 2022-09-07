"""KBEngine client application."""

import asyncio
import collections
import logging
from dataclasses import dataclass
from typing import Optional, Any

from tornado import iostream

from enki import descr, kbeclient, settings, command, kbeenum
from enki.misc import devonly, runutil
from enki.interface import IApp, IResult, IHandler
from enki.command import Command

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
        self._handlers[descr.app.client.onKicked.id] = handlers.OnKickedHandler(app=self)

        self._space_data: dict[int, dict[str, str]] = collections.defaultdict(dict)
        self._relogin_data = _ReloginData()

        logger.info('[%s] The application has been initialized', self)

    @property
    def is_connected(self) -> bool:
        return self._client is not None

    @property
    def client(self) -> kbeclient.Client:
        assert self._client
        return self._client

    async def stop(self):
        """Stop the application."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        if self._client is None:
            return
        for cmds in self._commands_by_msg_id.values():
            for cmd in cmds:
                cmd.on_end_receive_msg()
        self._commands_by_msg_id.clear()
        await self._sys_mgr.stop_server_tick()
        await self._client.stop()
        self._client = None
        # TODO: [2022-09-04 13:58 burov_alexey@mail.ru]:
        # Пока вместе с закрытием соединения завершается и процесс,
        # но при добавлнении переподключения нужно это убрать
        # Run shutdown in the next tick.
        asyncio.ensure_future(runutil.shutdown())
        logger.info('[%s] The application has been stoped', self)

    async def start(self, account_name: str, password: str) -> IResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._client = kbeclient.Client(self._login_app_addr)
        try:
            await self._client.start()
        except iostream.StreamClosedError as err:
            text: str = f'The client cannot connect to the '\
                        f'{self._login_app_addr.host}:{self._login_app_addr.port}. Exit'
            return AppStartResult(False, text=text)
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
            return AppStartResult(False, text=text)

        # We got the BaseApp address and do not need the LoginApp connection
        # anymore
        await self._client.stop()
        self._client = None

        baseapp_addr = settings.AppAddr(
            host=login_res.result.host,
            port=login_res.result.tcp_port
        )
        self._client = kbeclient.Client(baseapp_addr)
        try:
            await self._client.start()
        except iostream.StreamClosedError as err:
            text: str = f'The client cannot connect to the "{baseapp_addr}". Exit'
            return AppStartResult(False, text=text)
        self._client.set_msg_receiver(self)

        cmd = command.baseapp.HelloCommand(
            kbe_version='2.5.10',
            script_version='0.1.0',
            encrypted_key=b'',
            client=self._client
        )
        res = await self.send_command(cmd)
        if not res.success:
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
            return AppStartResult(False, text=res.text)

        self._sys_mgr.start_server_tick(self._server_tick_period)

        logger.info('[%s] The application has been succesfully connected to '
                    'the KBEngine server', self)
        return AppStartResult(True)

    def on_receive_msg(self, msg: kbeclient.Message) -> bool:
        logger.info('[%s] %s', self, devonly.func_args_values())
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

        result: handlers.HandlerResult = handler.handle(msg)

        return result.success

    def on_end_receive_msg(self):
        asyncio.ensure_future(self.stop())

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

    def send_message(self, msg: kbeclient.Message):
        logger.info('[%s] %s', self, devonly.func_args_values())
        if self._client is None:
            logger.warning(f'[{self}] There is no client! The message cannot '
                           f'be sent (msg = {msg}')
            return
        asyncio.create_task(self._client.send(msg))

    def get_relogin_data(self) -> tuple[int, int]:
        return self._relogin_data.rnd_uuid, self._relogin_data.entity_id

    def set_relogin_data(self, rnd_uuid: int, entity_id: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._relogin_data.rnd_uuid = rnd_uuid
        self._relogin_data.entity_id = entity_id

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'