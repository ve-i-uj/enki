"""KBEngine client application."""

import logging
from typing import Optional, Dict

from enki import kbeclient, settings, command, kbeenum, descr
from damkina import entitymgr, receiver, apphandler

logger = logging.getLogger(__name__)


class App(kbeclient.IMsgReceiver):
    """KBEngine client application."""

    def __init__(self, login_app_addr: settings.AppAddr):
        self._login_app_addr = login_app_addr
        # TODO: [24.07.2021 burov_alexey@mail.ru]:
        # Давать ссылку на само себя (через set_receiver) и иметь ссылку на клиент.
        self._client: Optional[kbeclient.Client] = None
        self._entity_mgr = entitymgr.EntityMgr(receiver=self)

        self._handlers: Dict[int, apphandler.IHandler] = {
            descr.app.client.onUpdatePropertys.id: apphandler.OnUpdatePropertysHandler(self._entity_mgr),
            descr.app.client.onCreatedProxies.id: apphandler.OnCreatedProxiesHandler(self._entity_mgr),
        }

    async def check_alive(self):
        # TODO: [24.07.2021 burov_alexey@mail.ru]:
        # Периодический опрос сервера делать, что живой (клиент
        # прежде всего живой).
        pass

    async def stop(self):
        """Stop the old session."""
        if self._client is not None:
            await self._client.stop()
            self._client = None

    async def start(self, account_name: str, password: str) -> tuple[bool, str]:
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

    def on_receive_msg(self, msg: kbeclient.Message) -> bool:
        handler = self._handlers.get(msg.id)
        if handler is None:
            logger.warning(f'[{self}] There is NO handler for the message '
                           f'"{msg.name}"')
            return False

        result: apphandler.HandlerResult = handler.handle(msg)

        return True
