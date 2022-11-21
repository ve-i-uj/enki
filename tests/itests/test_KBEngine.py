"""Интеграционны тесты на публичный интерфейс модуля KBEngine.

Тесты осуществляются при подключении к kbe_demo_assets . Тесты находятся
в игровом трэде. Сетевой трэд инициализируется вместе с Энки.
"""

import time
import logging
import unittest
from unittest.mock import MagicMock

import enki
from enki import KBEngine
from enki import devonly
from enki.enkitype import AppAddr
from enki import layer
from enki.app.thlayer import ThreadedGameLayer, ThreadedNetLayer

from tests.data import demo_descr, entities

LOGIN_APP_ADDR = AppAddr('localhost', 20013)

logger = logging.getLogger(__name__)


class KBEngineTestCase(unittest.TestCase):

    def setUp(self):
        super().setUp()
        enki.spawn(
            AppAddr('localhost', 20013),
            demo_descr.description.DESC_BY_UID,
            demo_descr.eserializer.SERIAZER_BY_ECLS_NAME,
            demo_descr.kbenginexml.root(),
            entities.ENTITY_CLS_BY_NAME
        )

    def tearDown(self) -> None:
        super().tearDown()
        enki.stop()


class KBEngineLoginTestCase(KBEngineTestCase):
    """Проверка работы KBEngine.login ."""

    def test_login(self):
        """Должен придти ответ об успешном подключении.

        Движение вызовов:
            Game -> Net -> Server -> Net -> Game

        Game и Net - в разных трэдах
        """
        game_layer: ThreadedGameLayer = layer.get_game_layer()  # type: ignore

        assert game_layer.get_game_state().get_account_name() == ''
        assert game_layer.get_game_state().get_password() == ''

        KBEngine.login('54', '21')

        end_time = time.time() + 5
        while time.time() < end_time:
            game_layer.update_from_net(block=True)

        assert game_layer.get_game_state().get_account_name() == '54'
        assert game_layer.get_game_state().get_password() == '21'

    def test_createAccount(self):
        """Должен создастся новый аккаунт."""
        game_layer: ThreadedGameLayer = layer.get_game_layer()  # type: ignore
        game_layer.on_create_account = MagicMock(
            side_effect=lambda suc, text: logger.debug('success = %s, text = %s', suc, text)
        )
        KBEngine.createAccount('76', '1')

        end_time = time.time() + 5
        while time.time() < end_time:
            game_layer.update_from_net(block=True)

        # Результат может быть каким угодно (в том числе и ошибка, если
        # пользователь существует). Просто проверяем, что колбэк был.
        game_layer.on_create_account.assert_called_once()

    def test_player(self):
        """Проверить, что возвращается плеер."""
        KBEngine.login('1', '1')
        game_layer: ThreadedGameLayer = layer.get_game_layer()  # type: ignore

        end_time = time.time() + 5
        while time.time() < end_time:
            game_layer.update_from_net(block=True)

        account = KBEngine.player()
        assert account is not None
        assert account.className == 'Account'

        assert account is game_layer.get_game_state().get_player()

    def test_findEntity(self):
        """Проверить поиск сущности."""
        KBEngine.login('1', '1')
        game_layer: ThreadedGameLayer = layer.get_game_layer()  # type: ignore

        end_time = time.time() + 5
        while time.time() < end_time:
            game_layer.update_from_net(block=True)

        account = KBEngine.player()
        assert account is not None
        assert KBEngine.entities[account.id] is account
        assert KBEngine.findEntity(account.id) is account
