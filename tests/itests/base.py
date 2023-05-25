"""Родительский класс для тестов на сетевой стороне (если бы были трэды, то это был бы ioloop)"""

import asyncio
import time
import unittest
from unittest.mock import Mock

import asynctest

from enki import settings
from enki import command
from enki.core.enkitype import AppAddr, NoValue
from enki.net.client import MsgTCPClient
from enki.app import clientapp
from enki.app.clientapp.layer import ilayer
from enki.app.clientapp import KBEngine
from enki.app.clientapp.appl import App
from enki.app.clientapp.clienthandler import *
from enki.app.clientapp.layer.thlayer import INetLayer, IGameLayer

from tests.data import entities, descr
from tests.data.entities import Account

LOGIN_APP_ADDR = AppAddr('localhost', 20013)


class IBaseAppMockedLayersTestCase(asynctest.TestCase):
    """Тесты со стороны сетевого слоя с замоканами слоями."""

    async def setUp(self) -> None:
        entity_serializer_by_uid = {
            cls.ENTITY_CLS_ID: cls for cls in descr.eserializer.SERIAZER_BY_ECLS_NAME.values()
        }
        self._app = App(
            LOGIN_APP_ADDR,
            descr.description.DESC_BY_UID,
            entity_serializer_by_uid,
            descr.kbenginexml.root(),
            settings.SERVER_TICK_PERIOD
        )
        net_layer = Mock(spec=INetLayer)
        game_layer = Mock(spec=IGameLayer)
        ilayer.init(net_layer, game_layer)

        res = await self._app.start('1', '1')
        assert res.success, res.text

    async def tearDown(self) -> None:
        await self._app.stop()


class IBaseAppThreadedTestCase(unittest.TestCase):
    """Родительский класс для тестов, где нужен игрвой API

    Войти в игру, получить аватаров и т.д..
    """

    def setUp(self):
        super().setUp()
        clientapp.start(
            AppAddr('localhost', 20013),
            descr.description.DESC_BY_UID,
            descr.eserializer.SERIAZER_BY_ECLS_NAME,
            descr.kbenginexml.root(),
            entities.ENTITY_CLS_BY_NAME
        )

    def tearDown(self) -> None:
        super().tearDown()
        clientapp.stop()

    @property
    def app(self) -> App:
        return clientapp._app

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return clientapp._loop

    def handle_msges(self, secs: int):
        end_time = time.time() + secs
        while time.time() < end_time:
            clientapp.sync_layers()
            time.sleep(1)

    def call_selectAvatarGame(self):
        acc: Account = KBEngine.player()  # type: ignore
        assert acc is not None

        acc.base.reqAvatarList()
        clientapp.sync_layers(settings.SECOND * 0.5)

        if acc.current_avatar_dbid == NoValue.NO_ID:
            acc.base.reqCreateAvatar(1, f'itest_bot_{acc.id}')
            clientapp.sync_layers(settings.SECOND * 0.5)

        assert acc.current_avatar_dbid != NoValue.NO_ID

        acc.base.selectAvatarGame(acc.current_avatar_dbid)
        clientapp.sync_layers(settings.SECOND * 0.5)


class IntegrationLoginAppBaseTestCase(asynctest.TestCase):

    async def setUp(self) -> None:
        self._client = MsgTCPClient(LOGIN_APP_ADDR, msgspec.app.client.SPEC_BY_ID)
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
    def client(self) -> MsgTCPClient:
        return self._client
