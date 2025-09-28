"""Интеграционные тесты Clientapp."""

import asyncio
import random
import string

import pytest

from enki import msgspec
from enki.apps.clientapp.app import ClientApp
from enki.kbeenum import ClientType
from enki.kbetype.pytypes.basic_data_types import KBERowByteData
from enki.msg.message import Message
from enki.net.addr import Addr, Port
from enki.settings import SECOND


# TODO: [2025-09-06 12:09 burov_alexey@mail.ru]:
# Это всё настройка приложения. Может быть вынести в отдельный класс и функционал.
_LOGINAPP_PORT = 20013
_LOGINAPP_ADDR = Addr.create_default_gw_addr(Port(_LOGINAPP_PORT))
_LOGIN_NAME = "".join(random.choice(string.ascii_letters) for _ in range(10))
_PASSWORD = "".join(random.choice(string.ascii_letters) for _ in range(10))
_CLIENT_DATA = b"client_data"
_ENTITYDEFS_HASH = "06E15F102B481ACF8CA19E2F410D1B64"
_CLIENT_TYPE = ClientType.LINUX
_KBE_VERSION = "2.5.10"
_SCRIPT_VERSION = "0.1.0"
_ENCRYPTED_KEY = b""
_SERVER_TICK_PERIOD = 30 * SECOND
_FORCE_LOGIN = True


class TestClientApp:
    """Интеграционные тесты Clientapp."""

    async def test_start(self):
        """Clientapp запускается."""
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
        res = await clientapp.start()
        assert res.success is True, res.text

    async def test_stop(self):
        """Clientapp останавливается."""
        clientapp = ClientApp(
            loginapp_addr=Addr("0.0.0.0", Port(20013)),
            login_name="1",
            password="1",
            client_data=b"client_data",
            entitydefs_hash="06E15F102B481ACF8CA19E2F410D1B64",
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
@pytest.fixture
async def clientapp():
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

    async def test_onUpdatePropertys(self, clientapp: ClientApp):
        """Clientapp обрабатывает Client::onUpdatePropertys.

        Понастоящему логинимся и затем имитируем получения сообщения.
        """
        values = (
            KBERowByteData(
                b"\xd5\x07\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00"
            ),
        )
        msg = Message.create(msgspec.client.onUpdatePropertys, values)
        clientapp._handle_msg(msg)

        # await asyncio.sleep(600)
