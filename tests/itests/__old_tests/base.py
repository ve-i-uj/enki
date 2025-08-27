"""Родительский класс для тестов на сетевой стороне (если бы были трэды, то это был бы ioloop)."""

import asyncio
import time
import unittest
from typing import TYPE_CHECKING
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock

from enki import command, kbeenum, msgspec, settings
from enki.app import client
from enki.apps.clientapp import KBEngine
from enki.apps.clientapp.appl import App
from enki.apps.clientapp.layer import ilayer
from enki.apps.clientapp.layer.thlayer import IGameLayer, INetLayer
from enki.net.addr import Addr
from enki.net.client import MsgTCPClient
from tests.data import descr, entities

if TYPE_CHECKING:
    from tests.data.entities import Account

LOGINAPP_ADDR = Addr("0.0.0.0", 20013)


class IBaseAppMockedLayersTestCase(IsolatedAsyncioTestCase):
    """Тесты со стороны сетевого слоя с замоканами слоями."""

    async def asyncSetUp(self) -> None:
        entity_serializer_by_uid = {
            cls.ENTITY_CLS_ID: cls
            for cls in descr.eserializer.SERIAZER_BY_ECLS_NAME.values()
        }
        self._app = App(
            LOGINAPP_ADDR,
            descr.description.DESC_BY_UID,
            entity_serializer_by_uid,
            descr.kbenginexml.root(),
            settings.SERVER_TICK_PERIOD,
        )
        net_layer = Mock(spec=INetLayer)
        game_layer = Mock(spec=IGameLayer)
        ilayer.init(net_layer, game_layer)

        res = await self._app.start("1", "1")
        assert res.success, res.text

    async def asyncTearDown(self) -> None:
        await self._app.stop()


class IBaseAppThreadedTestCase(unittest.TestCase):
    """Родительский класс для тестов, где нужен игрвой API.

    Войти в игру, получить аватаров и т.д..
    """

    def setUp(self):
        super().setUp()
        client.start(
            Addr("localhost", 20013),
            descr.description.DESC_BY_UID,
            descr.eserializer.SERIAZER_BY_ECLS_NAME,
            descr.kbenginexml.root(),
            entities.ENTITY_CLS_BY_NAME,
        )

    def tearDown(self) -> None:
        super().tearDown()
        client.stop()

    @property
    def app(self) -> App:
        return client._app

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return client._loop

    def handle_msges(self, secs: int):
        end_time = time.time() + secs
        while time.time() < end_time:
            client.sync_layers()
            time.sleep(1)

    def call_selectAvatarGame(self):
        acc: Account = KBEngine.player()  # type: ignore
        assert acc is not None

        acc.base.reqAvatarList()
        client.sync_layers(settings.SECOND * 0.5)

        if acc.current_avatar_dbid == NoValue.NO_ID:
            acc.base.reqCreateAvatar(1, f"itest_bot_{acc.id}")
            client.sync_layers(settings.SECOND * 0.5)

        assert acc.current_avatar_dbid != NoValue.NO_ID

        acc.base.selectAvatarGame(acc.current_avatar_dbid)
        client.sync_layers(settings.SECOND * 0.5)


class IntegrationLoginAppBaseTestCase(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self._client = MsgTCPClient(LOGINAPP_ADDR, msgspec.client.SPEC_BY_ID)
        await self._client.start()

        hello_cmd = command.loginapp.HelloCommand(
            kbe_version="2.5.10",
            script_version="0.1.0",
            encrypted_key=b"",
            client=self._client,
        )
        self._client.set_msg_receiver(hello_cmd)
        res = await hello_cmd.execute()
        assert res.success

        cmd = command.loginapp.LoginCommand(
            client_type=kbeenum.ClientType.UNKNOWN,
            client_data=b"",
            account_name="1",
            password="1",
            force_login=False,
            client=self._client,
        )
        self._client.set_msg_receiver(cmd)
        login_res = await cmd.execute()
        assert login_res.success, login_res.text

    async def asyncTearDown(self) -> None:
        self._client.stop()

    @property
    def client(self) -> MsgTCPClient:
        return self._client
