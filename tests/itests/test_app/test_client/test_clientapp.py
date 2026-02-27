"""Интеграционные тесты Clientapp."""

import asyncio
import random
import string
from queue import Queue
from threading import Thread

import pytest

from enki.apps.clientapp.app import ClientApp
from enki.apps.clientapp.layer.thlayer import (
    QueueCallbackItem,
    ThreadedGameLayer,
)
from enki.kbeenum import ClientType, ComponentType
from enki.msg.msg_serializer import MessageSerializer, MessageSerializer.get_serializer
from enki.net.addr import Addr, Port
from enki.settings import SECOND
from tests.itests.app_mocks.loginapp_mock import LoginappMock

# TODO: [2025-09-06 12:09 burov_alexey@mail.ru]:
# Это всё настройка приложения. Может быть вынести в отдельный класс и функционал.
_LOGINAPP_PORT = 20013
_LOGINAPP_ADDR = Addr.create_default_gw_addr(Port(_LOGINAPP_PORT))
_LOGIN_NAME = "".join(random.choice(string.ascii_letters) for _ in range(10))
_PASSWORD = "".join(random.choice(string.ascii_letters) for _ in range(10))
_CLIENT_DATA = b"client_data"
_ENTITYDEFS_HASH = "97FD10D9C332339BAE53A765BF8E35AA"
_CLIENT_TYPE = ClientType.LINUX
_KBE_VERSION = "2.5.10"
_SCRIPT_VERSION = "0.1.0"
_ENCRYPTED_KEY = b""
_SERVER_TICK_PERIOD = 30 * SECOND
_FORCE_LOGIN = True


USE_KBE_LOGINAPP = False


class TestOnCreatedProxies:
    """Test onCreatedProxies."""

    async def test_on_update_and_on_created_proxy(
        self, loginapp_fixture: LoginappMock
    ):
        """Ещё до создания сущности приходит сообщение об обновлении свойств.

        Это сообщение нужно сохранить.
        """
        queue: Queue[QueueCallbackItem] = Queue()

        loop = asyncio.get_event_loop()
        thread = Thread(target=loop.run_forever, daemon=True)
        thread.start()

        game_layer = ThreadedGameLayer({}, queue)
        client_app = ClientApp(
            loginapp_addr=loginapp_fixture.tcp_addr,
            server_tick_period=30 * SECOND,
            force_login=True,
            game_layer=game_layer,
        )

        res = await client_app.start()
        assert res.success

        # client.start(
        #     Addr("localhost", 20013),
        #     descr.description.DESC_BY_UID,
        #     descr.eserializer.SERIAZER_BY_ECLS_NAME,
        #     descr.kbenginexml.root(),
        #     entities.ENTITY_CLS_BY_NAME,
        # )
        # client_app = client._app
        # # Имитируем, что приложение подключено
        # client_app._state = __appl._AppStateEnum.CONNECTED
        # # Подменим слои на моки
        # ilayer.init(MagicMock(), MagicMock())

        serializer = MessageSerializer.MessageSerializer.get_serializer(ComponentType.CLIENT)

        data = b"\xff\x01\x0e\x00\xf3\x00\x00\x00\x00\x04\x02\x00\x00\x00\x00\x00\x00\x00\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00"
        # onUpdatePropertys
        onUpdatePropertys_msg, data_tail = serializer.deserialize(
            memoryview(data)
        )
        assert onUpdatePropertys_msg is not None, "Invalid initial data"

        onCreatedProxies_msg, data_tail = serializer.deserialize(data_tail)
        assert onCreatedProxies_msg is not None
        assert not data_tail

        # Сообщение об обновлении пришло до создания сущности. Оно должно
        # быть сохранено и переотправлено, когда сущность будет создана.

        # assert not client_app._pending_msgs_by_entity_id

        client_app.on_receive_msg(onUpdatePropertys_msg)

        # Уснём на секунду, чтобы поймать таск в следующем тике
        await asyncio.sleep(1)
        assert len(client_app._pending_msgs_by_entity_id) == 1
        # 243 - это id сущности
        assert (
            msgspec.client.onUpdatePropertys.id
            == client_app._pending_msgs_by_entity_id[243][0].id
        )
        # В игру уведомления не было
        assert ilayer.get_game_layer().call_entity_created.call_count == 0
        assert ilayer.get_game_layer().update_entity_properties.call_count == 0

        # Теперь пришлои onCreatedProxies. Сообщения 511 должны быть пересланы
        data = b"\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00"
        msg_504, _data_tail = serializer.deserialize(memoryview(data))
        assert msg_504 is not None, "Invalid initial data"
        client_app.on_receive_msg(msg_504)
        await asyncio.sleep(1)
        assert not client_app._pending_msgs_by_entity_id
        assert ilayer.get_game_layer().call_entity_created.call_count == 1
        assert ilayer.get_game_layer().update_entity_properties.call_count == 1


class TestClientApp:
    """Интеграционные тесты Clientapp."""

    @pytest.mark.timeout(5)
    async def test_start(self):
        """Clientapp запускается."""
        clientapp = ClientApp(
            loginapp_addr=started_loginapp.tcp_addr,
            login_name=_LOGIN_NAME,
            password=_PASSWORD,
            client_data=_CLIENT_DATA,
            entitydefs_hash=_ENTITYDEFS_HASH,
            client_type=_CLIENT_TYPE,
            kbe_version=_KBE_VERSION,
            script_version=_SCRIPT_VERSION,
            encrypted_key=_ENCRYPTED_KEY,
            server_tick_period=_SERVER_TICK_PERIOD,
            force_login=_FORCE_LOGIN,
        )
        res = await clientapp.start()
        assert res.success is True, res.text

    @pytest.mark.timeout(5)
    async def test_stop(self):
        """Clientapp останавливается."""
        clientapp = ClientApp(
            loginapp_addr=Addr("0.0.0.0", Port(20013)),
            login_name="1",
            password="1",
            client_data=b"client_data",
            entitydefs_hash="97FD10D9C332339BAE53A765BF8E35AA",
            client_type=ClientType.LINUX,
            kbe_version="2.5.10",
            script_version="0.1.0",
            encrypted_key=b"",
            server_tick_period=30 * SECOND,
            force_login=True,
        )
        res = await clientapp.start()
        assert res.success is True, res.text

        clientapp.stop()
        await asyncio.sleep(0.1)

        assert not clientapp.is_started


# TODO: [2025-09-06 11:53 burov_alexey@mail.ru]:
# В переменные окружения адресе, логин и всё остальное. Плюс нужен мок сервера.
# Имитация сообщений от сервера. Можно взять в тестах сервера / клиента сообщений.
# Сообщения снять с помощью ридера.
# [2026-01-31 13:04 burov_alexey@mail.ru]:
# Можно прямо тестовые Loginapp запускать ) Со всеми запущенными сервисами? ))
# Это тогда ограниченная функиональность в тестах. Ну логин и реконнект и
# почта - тоже не плохо.
@pytest.fixture
async def started_clientapp():
    """Фикстура запущенного Clientapp."""
    clientapp = ClientApp(
        loginapp_addr=_LOGINAPP_ADDR,
        login_name=_LOGIN_NAME,
        password=_PASSWORD,
        client_data=_CLIENT_DATA,
        entitydefs_hash=_ENTITYDEFS_HASH,
        client_type=_CLIENT_TYPE,
        kbe_version=_KBE_VERSION,
        script_version=_SCRIPT_VERSION,
        encrypted_key=_ENCRYPTED_KEY,
        server_tick_period=_SERVER_TICK_PERIOD,
        force_login=_FORCE_LOGIN,
    )
    await clientapp.start()

    yield clientapp

    clientapp.stop()


class TestOnUpdatePropertys:
    """Тесты Clientapp по обработке Client::onUpdatePropertys."""

    @pytest.mark.skip("Нужны настоящие данные")
    @pytest.mark.timeout(5)
    async def test_onUpdatePropertys(self, started_clientapp: ClientApp):
        """Clientapp обрабатывает Client::onUpdatePropertys.

        Понастоящему логинимся и затем имитируем получения сообщения.
        """
        # [2026-01-31 13:09 burov_alexey@mail.ru]:
        # Нужны настоящие данные
        data = b"\xd5\x07\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00"
        serializer = MessageSerializer.get_serializer(ComponentType.CLIENT)
        msg, data_tail = serializer.deserialize(memoryview(data))
        assert msg is not None
        assert not data_tail

        started_clientapp._handle_msg(msg)

        # await asyncio.sleep(600)
