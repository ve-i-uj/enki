"""Родительский класс для тестов на сетевой стороне (если бы были трэды, то это был бы ioloop)"""

import asyncio
import time
import unittest
from unittest.mock import Mock

import asynctest

import enki
from enki import layer
from enki import settings
from enki import KBEngine

from enki.enkitype import AppAddr

from enki.net import command
from enki.net.kbeclient import Client

from enki.app.appl import App
from enki.app.thlayer import ThreadedGameLayer, ThreadedNetLayer
from enki.app.handler import *

from enki.layer import INetLayer, IGameLayer

from tests.data.descr import description, kbenginexml, eserializer
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
        layer.init(net_layer, game_layer)

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
        enki.spawn(
            AppAddr('localhost', 20013),
            descr.description.DESC_BY_UID,
            descr.eserializer.SERIAZER_BY_ECLS_NAME,
            descr.kbenginexml.root(),
            entities.ENTITY_CLS_BY_NAME
        )

    def tearDown(self) -> None:
        super().tearDown()
        enki.stop()

    @property
    def app(self) -> App:
        return enki._app

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return enki._loop

    def handle_msges(self, secs: int):
        end_time = time.time() + secs
        while time.time() < end_time:
            enki._th_game_layer.sync_layers()
            time.sleep(1)

    def call_selectAvatarGame(self):
        acc: Account = KBEngine.player()  # type: ignore
        assert acc is not None

        acc.base.reqAvatarList()
        enki.sync_layers(settings.SECOND * 0.5)

        if acc.current_avatar_dbid == settings.NO_ID:
            acc.base.reqCreateAvatar(1, f'itest_bot_{acc.id}')
            enki.sync_layers(settings.SECOND * 0.5)

        assert acc.current_avatar_dbid != settings.NO_ID

        acc.base.selectAvatarGame(acc.current_avatar_dbid)
        enki.sync_layers(settings.SECOND * 0.5)


class IntegrationLoginAppBaseTestCase(asynctest.TestCase):

    async def setUp(self) -> None:
        self._client = kbeclient.Client(LOGIN_APP_ADDR, msgspec.app.client.SPEC_BY_ID)
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
