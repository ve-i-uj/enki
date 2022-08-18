"""KBEngine client application."""

import asyncio
import logging
from typing import Optional, Any

from enki import kbeclient, settings, command, kbeenum, descr
from enki.interface import IMsgReceiver
from enki.misc import devonly
from damkina import interface
from damkina import entitymgr, apphandler, sysmgr

logger = logging.getLogger(__name__)


class App(interface.IApp, IMsgReceiver):
    """KBEngine client application."""

    def __init__(self, login_app_addr: settings.AppAddr,
                 server_tick_period: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._login_app_addr = login_app_addr
        self._server_tick_period = server_tick_period
        self._client: Optional[kbeclient.Client] = None
        self._entity_mgr = entitymgr.EntityMgr(app=self)
        self._sys_mgr = sysmgr.SysMgr(app=self)

        self._commands: list[command.Command] = []
        self._commands_msg_ids: set[int] = set()

        self._handlers: dict[int, apphandler.IHandler] = {
            descr.app.client.onUpdatePropertys.id: apphandler.OnUpdatePropertysHandler(self._entity_mgr),
            descr.app.client.onCreatedProxies.id: apphandler.OnCreatedProxiesHandler(self._entity_mgr),

            descr.app.client.onRemoteMethodCall.id: apphandler.entity.OnRemoteMethodCallHandler(self._entity_mgr),
        }

    @property
    def client(self) -> Optional[kbeclient.Client]:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        return self._client

    async def check_alive(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        # TODO: [24.07.2021 burov_alexey@mail.ru]:
        # Периодический опрос сервера делать, что живой (клиент
        # прежде всего живой).

    async def stop(self):
        """Stop the old session."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        if self._client is not None:
            await self._client.stop()
            self._client = None

    async def start(self, account_name: str, password: str) -> tuple[bool, str]:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        await self.stop()
        self._client = kbeclient.Client(self._login_app_addr)
        await self._client.start()

        cmd = command.loginapp.HelloCommand(
            kbe_version='2.5.10',
            script_version='0.1.0',
            encrypted_key=b'',
            client=self._client
        )
        success, err_msg = await cmd.execute()
        if not success:
            logger.error(err_msg)
            return False, err_msg

        cmd = command.loginapp.LoginCommand(
            client_type=kbeenum.ClientType.UNKNOWN, client_data=b'',
            account_name=account_name, password=password, force_login=False,
            client=self._client
        )
        login_result: command.loginapp.LoginCommandResult = await cmd.execute()

        if login_result.ret_code != kbeenum.ServerError.SUCCESS:
            err_msg = login_result.data.decode()
            msg = f'The client cannot connect to LoginApp ' \
                  f'(code = {login_result.ret_code}, msg = {err_msg})'
            logger.warning(msg)
            return False, msg

        # We got the BaseApp address and do not need the LoginApp connection
        # anymore
        await self._client.stop()
        self._client = None

        baseapp_addr = settings.AppAddr(host=login_result.host,
                                        port=login_result.tcp_port)
        self._client = kbeclient.Client(baseapp_addr)
        await self._client.start()

        cmd = command.baseapp.HelloCommand(
            kbe_version='2.5.10',
            script_version='0.1.0',
            encrypted_key=b'',
            client=self._client
        )
        success, err_msg = await cmd.execute()
        if not success:
            logger.error(err_msg)
            return False, err_msg

        # This message starts the client-server communication. The server will
        # send many initial messages in the response. But it also can return
        # nothing (no server response and stop waiting by timeout).
        # Set the application receiver.
        self._client.set_msg_receiver(receiver=self)
        msg = kbeclient.Message(descr.app.baseapp.loginBaseapp,
                                (account_name, password))
        await self._client.send(msg)

        self._sys_mgr.start_server_tick(self._server_tick_period)

    def on_receive_msg(self, msg: kbeclient.Message) -> bool:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        # TODO: [27.07.2021 burov_alexey@mail.ru]:
        # Переделать сам подход с командами
        if msg.id in self._commands_msg_ids:
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

        result: apphandler.HandlerResult = handler.handle(msg)

        return result.success

    async def send_command(self, cmd: command.Command) -> Any:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._commands_msg_ids.update(cmd.waited_ids)
        self._commands.append(cmd)
        res = await cmd.execute()
        return res

    def send_message(self, msg: kbeclient.Message):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        asyncio.create_task(self._client.send(msg))

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'
