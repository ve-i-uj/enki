"""???"""

import asyncio
import asynctest

from enki import layer
from enki import settings

from enki.enkitype import AppAddr

from enki.net import command
from enki.net.kbeclient import Client

from enki.app.appl import App
from enki.app.thlayer import ThreadedGameLayer, ThreadedNetLayer
from enki.app.handler import *

from tests.data.demo_descr import description, kbenginexml, eserializer
from tests.data import entities

LOGIN_APP_ADDR = AppAddr('localhost', 20013)


class IntegrationBaseAppBaseTestCase(asynctest.TestCase):

    async def setUp(self) -> None:
        app = App(
            LOGIN_APP_ADDR,
            description.DESC_BY_UID,
            {cls.ENTITY_CLS_ID: cls for cls in eserializer.SERIAZER_BY_ECLS_NAME.values()},
            kbenginexml.root(),
            settings.SERVER_TICK_PERIOD
        )
        net_layer = ThreadedNetLayer(
            eserializer.SERIAZER_BY_ECLS_NAME, app
        )
        game_layer = ThreadedGameLayer(entities.ENTITY_CLS_BY_NAME)

        layer.init(net_layer, game_layer)

        res = await app.start(
            '1', '1'
        )
        assert res.success, res.text

        self._app = app
        self._gama_layer = game_layer

    async def tearDown(self) -> None:
        if getattr(self, '_app', None) is None:
            return
        await self._app.stop()

    @property
    def app(self) -> App:
        return self._app

    async def call_selectAvatarGame(self):
        acc: Account = self._gama_layer.get_game_state().get_player()  # type: ignore
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
        self._client = kbeclient.Client(LOGIN_APP_ADDR)
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
            client_type=kbeenum.ClientType.UNKNOWN,
            client_data=b'',
            account_name='1',
            password='1',
            force_login=False,
            client=self._client
        )
        self._client.set_msg_receiver(cmd)
        login_res = await cmd.execute()
        assert login_res.success, login_res.text

    async def tearDown(self) -> None:
        self._client.stop()

    @property
    def client(self) -> Client:
        return self._client
