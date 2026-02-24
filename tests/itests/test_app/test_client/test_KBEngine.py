"""Интеграционны тесты на публичный интерфейс модуля KBEngine.

Тесты осуществляются при подключении к kbe_demo_assets . Тесты находятся
в игровом трэде. Сетевой трэд инициализируется вместе с Энки.
"""

import asyncio
import logging
import time
from queue import Queue
from threading import Thread
from unittest.mock import MagicMock

import pytest

from enki.apps.clientapp import KBEngine
from enki.apps.clientapp.app import ClientApp
from enki.apps.clientapp.layer import ilayer
from enki.apps.clientapp.layer.thlayer import (
    QueueCallbackItem,
    ThreadedGameLayer,
    ThreadedNetLayer,
)
from tests.itests.app_mocks.loginapp_mock import LoginappMock

logger = logging.getLogger(__name__)


class TestKBEngine:
    """Проверка работы модуля KBEngine."""

    @pytest.mark.timeout(5)
    def test_login(self, started_loginapp: LoginappMock):
        """Должен придти ответ об успешном подключении.

        Движение вызовов:
            Game -> Net -> Server -> Net -> Game

        Game и Net - в разных трэдах
        """
        client_app = ClientApp(
            loginapp_addr=started_loginapp.tcp_addr,
            server_tick_period=2,
            force_login=True,
        )
        queue: Queue[QueueCallbackItem] = Queue()

        loop = asyncio.get_event_loop()
        thread = Thread(target=loop.run_forever, daemon=True)
        thread.start()

        net_layer = ThreadedNetLayer({}, client_app, loop, queue)

        game_layer = ThreadedGameLayer({}, queue)
        # Мок, чтобы проверить, что ответ был в игровом треде
        game_layer.on_login = MagicMock(  # type: ignore
            side_effect=lambda *args: logger.debug("args = %s", args)
        )
        game_layer._on_call_entity_created = MagicMock(  # type: ignore
            side_effect=lambda *args: logger.debug("args = %s", args)
        )
        game_layer._on_update_entity_properties = MagicMock(  # type: ignore
            side_effect=lambda *args: logger.debug("args = %s", args)
        )
        ilayer.init(net_layer, game_layer)

        KBEngine.login("54", "21")

        end_time = time.time() + 2
        while time.time() < end_time:
            game_layer.sync_layers()

        # Результат может быть каким угодно (в том числе и ошибка, если
        # пользователь существует). Просто проверяем, что колбэк был.
        game_layer.on_login.assert_called_once()
        # Это удачный login
        assert game_layer.on_login.call_args[0][2] is True

        # Был вызов колбэка об обновлении свойств сущности
        game_layer._on_update_entity_properties.assert_called_once()

        # Был вызов колбэка о создании сущности
        game_layer._on_call_entity_created.assert_called_once()

    def test_createAccount(self, started_loginapp: LoginappMock):
        """Должен создастся новый аккаунт."""
        queue: Queue[QueueCallbackItem] = Queue()

        loop = asyncio.get_event_loop()
        thread = Thread(target=loop.run_forever, daemon=True)
        thread.start()

        game_layer = ThreadedGameLayer({}, queue)
        client_app = ClientApp(
            loginapp_addr=started_loginapp.tcp_addr,
            server_tick_period=2,
            force_login=True,
            game_layer=game_layer,
            entity_desc_by_uid={},
        )
        net_layer = ThreadedNetLayer({}, client_app, loop, queue)

        # Мок, чтобы проверить, что ответ был в игровом треде
        game_layer.on_create_account = MagicMock(  # type: ignore
            side_effect=lambda suc, ret_code, data, text: logger.debug(
                "success = %s, ret_code = %s, data = %s, text = %s",
                suc,
                ret_code,
                data,
                text,
            )
        )

        ilayer.init(net_layer, game_layer)

        KBEngine.createAccount("76", "1")

        end_time = time.time() + 2
        while time.time() < end_time:
            game_layer.sync_layers()

        # Результат может быть каким угодно (в том числе и ошибка, если
        # пользователь существует). Просто проверяем, что колбэк был.
        game_layer.on_create_account.assert_called_once()

    @pytest.mark.skip("Not implemented yet")
    def test_player(self):
        """Проверить, что возвращается плеер."""
        KBEngine.login("1", "1")
        game_layer: ThreadedGameLayer = ilayer.get_game_layer()  # type: ignore

        end_time = time.time() + 5
        while time.time() < end_time:
            game_layer.sync_layers()

        account = KBEngine.player()
        assert account is not None
        assert account.className == "Account"

        assert account is game_layer.get_game_state().get_player()

    @pytest.mark.skip("Not implemented yet")
    def test_findEntity(self):
        """Проверить поиск сущности."""
        KBEngine.login("1", "1")
        game_layer: ThreadedGameLayer = ilayer.get_game_layer()  # type: ignore

        end_time = time.time() + 5
        while time.time() < end_time:
            game_layer.sync_layers()

        account = KBEngine.player()
        assert account is not None
        assert KBEngine.entities[account.id] is account
        assert KBEngine.findEntity(account.id) is account
