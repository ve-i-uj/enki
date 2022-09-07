"""???"""

import asyncio
import asynctest

from enki.app import appl
from enki import settings, kbeclient, command, kbeenum
from enki.app.entities.account import Account
from enki.interface import IApp, IClient, IEntity


class IntegrationBaseAppBaseTestCase(asynctest.TestCase):

    async def setUp(self) -> None:
        app = appl.App(settings.LOGIN_APP_ADDR, settings.SERVER_TICK_PERIOD)
        start_res = await app.start(settings.ACCOUNT_NAME, settings.PASSWORD)
        assert start_res.success, start_res.text
        self._app = app

    async def tearDown(self) -> None:
        if getattr(self, '_app', None) is None:
            return
        await self._app.stop()

    @property
    def proxy_entity(self) -> IEntity:
        entities = list(self._app._entity_mgr._entities.values())
        assert len(entities) == 1
        return entities[0]

    @property
    def app(self) -> appl.App:
        return self._app

    @property
    def player(self) -> IEntity:
        return self.app._entity_mgr.get_player()  # type: ignore

    async def call_selectAvatarGame(self):
        acc: Account = self.player  # type: ignore
        acc.base.reqAvatarList()
        await asyncio.sleep(1)
        if not acc._avatars:
            acc.base.reqCreateAvatar(1, 'Damkina')
            await asyncio.sleep(2)
            acc.base.reqAvatarList()
            await asyncio.sleep(1)
        acc.base.selectAvatarGame(list(acc._avatars.keys())[0])
        await asyncio.sleep(2)


class IntegrationLoginAppBaseTestCase(asynctest.TestCase):

    async def setUp(self) -> None:
        self._client = kbeclient.Client(settings.LOGIN_APP_ADDR)
        await self._client.start()

        cmd = command.loginapp.HelloCommand(
            kbe_version='2.5.10',
            script_version='0.1.0',
            encrypted_key=b'',
            client=self._client
        )
        self._client.set_msg_receiver(cmd)
        res = await cmd.execute()
        assert res.success

        cmd = command.loginapp.LoginCommand(
            client_type=kbeenum.ClientType.UNKNOWN, client_data=b'',
            account_name=settings.ACCOUNT_NAME, password=settings.PASSWORD,
            force_login=False,
            client=self._client
        )
        self._client.set_msg_receiver(cmd)
        login_res = await cmd.execute()
        assert login_res.success, login_res.text

    async def tearDown(self) -> None:
        await self._client.stop()

    @property
    def client(self) -> IClient:
        return self._client
