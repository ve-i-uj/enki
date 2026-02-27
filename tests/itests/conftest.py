import os
import shutil
import tempfile

import pytest

from enki.apps.clientapp.clients.loginapp_client import LoginappClient
from enki.kbeenum import ComponentType
from enki.kbetype.decoders.custom_decoders import KBEComponentType
from enki.kbetype.pytypes.basic_data_types import KBEString
from enki.misc.result import Result
from enki.misc.startable import IStartable
from enki.msg.imsg import IMsgBackChannel, IServerMsgReceiver
from enki.msg.message import Message
from enki.net.addr import Addr, Port
from enki.net.server import get_free_port
from tests.itests.app_mocks.baseapp_mock import BaseappMock
from tests.itests.app_mocks.loginapp_mock import LoginappMock

TESTS_STARTED_BASEAPP_ADDR = os.environ.get("TESTS_STARTED_BASEAPP_ADDR")
TESTS_STARTED_LOGINAPP_ADDR = os.environ.get("TESTS_STARTED_LOGINAPP_ADDR")


class _BaseappDataForTesting(IStartable, IServerMsgReceiver):
    """Данные настоященго запущенного Baseapp.

    Данные нужны, чтобы сохранить совместимость интеграционных тестов, но
    проверять их на реальном запущнном кластере KBEngine.
    """

    def __init__(
        self,
        tcp_addr: Addr,
        kbe_version: str,
        account_name: str,
        assets_version: str,
        password: str,
        protocol_md5: str,
        entity_def_md5: str,
    ) -> None:
        self._tcp_addr = tcp_addr

        self._kbe_version = KBEString(kbe_version)
        self._assets_version = KBEString(assets_version)
        self._protocol_md5 = KBEString(protocol_md5)
        self._entity_def_md5 = KBEString(entity_def_md5)
        self._componentType = KBEComponentType(ComponentType.BASEAPP.value)

        self._account_name = account_name
        self._password = password

    @property
    def account_name(self) -> str:
        """Получить версию ассетов."""
        return self._account_name

    @property
    def password(self) -> str:
        """Получить версию ассетов."""
        return self._password

    @property
    def kbe_version(self) -> KBEString:
        """Получить версию ассетов."""
        return self._kbe_version

    @property
    def assets_version(self) -> KBEString:
        """Получить версию ассетов."""
        return self._assets_version

    @property
    def protocol_md5(self) -> KBEString:
        """Получить MD5 протокола."""
        return self._protocol_md5

    @protocol_md5.setter
    def protocol_md5(self, value: KBEString) -> None:
        """Установить MD5 протокола."""
        self._protocol_md5 = value

    @property
    def entity_def_md5(self) -> KBEString:
        """Получить MD5 определений сущностей."""
        return self._entity_def_md5

    @entity_def_md5.setter
    def entity_def_md5(self, value: KBEString) -> None:
        """Установить MD5 определений сущностей."""
        self._entity_def_md5 = value

    @property
    def componentType(self) -> KBEComponentType:
        """Получить тип компонента (только чтение)."""
        return self._componentType

    @property
    def tcp_addr(self) -> Addr:
        return self._tcp_addr

    async def start(self) -> Result:
        return Result(success=True, result=None)

    def stop(self) -> None:
        pass

    @property
    def is_started(self) -> bool:
        """Флаг запущен ли Baseapp.

        Returns:
            bool: Флаг запущен ли Baseapp

        """
        return True

    def on_receive_msg(self, msg: Message, back_channel: IMsgBackChannel) -> None:
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"


@pytest.fixture
async def baseapp_fixture():
    """Фикстура запущенного Baseapp."""
    tcp_addr = Addr.create_default_gw_addr(Port(get_free_port()))
    kls = BaseappMock

    if TESTS_STARTED_BASEAPP_ADDR is not None:
        res = TESTS_STARTED_BASEAPP_ADDR.split(":")
        assert len(res) == 2, f"Invalid Baseapp address {TESTS_STARTED_BASEAPP_ADDR}"
        host, port = res

        tcp_addr = Addr(host, Port(port))
        kls = _BaseappDataForTesting  # type: ignore

    baseapp = kls(
        tcp_addr=tcp_addr,
        kbe_version="2.5.10",
        assets_version="0.1.0",
        account_name="1",
        password="1",
        protocol_md5="6615F2367124A5E4B390207ACC4906B6",
        entity_def_md5="97FD10D9C332339BAE53A765BF8E35AA",
    )
    await baseapp.start()

    yield baseapp

    baseapp.stop()


class _LoginappDataForTesting(IStartable, IServerMsgReceiver):
    """Компонент частично повторяющий функционал KBEngine-компонента Loginapp."""

    def __init__(
        self,
        tcp_addr: Addr,
        baseapp_tcp_add: Addr,
        kbe_version: str,
        assets_version: str,
        account_name: str,
        password: str,
        protocol_md5: str,
        entity_def_md5: str,
    ) -> None:
        self._tcp_addr = tcp_addr
        self._baseapp_tcp_add = baseapp_tcp_add

        self._kbe_version = KBEString(kbe_version)
        self._assets_version = KBEString(assets_version)
        self._protocol_md5 = KBEString(protocol_md5)
        self._entity_def_md5 = KBEString(entity_def_md5)
        self._componentType = KBEComponentType(ComponentType.LOGINAPP.value)

        self._account_name = KBEString(account_name)
        self._password = KBEString(password)

    @property
    def account_name(self) -> str:
        """Получить версию ассетов."""
        return self._account_name

    @property
    def password(self) -> str:
        """Получить версию ассетов."""
        return self._password

    @property
    def baseapp_tcp_add(self) -> Addr:
        """Получить версию ассетов."""
        return self._baseapp_tcp_add

    @property
    def kbe_version(self) -> KBEString:
        """Получить версию ассетов."""
        return self._kbe_version

    @property
    def assets_version(self) -> KBEString:
        """Получить версию ассетов."""
        return self._assets_version

    @property
    def protocol_md5(self) -> KBEString:
        """Получить MD5 протокола."""
        return self._protocol_md5

    @protocol_md5.setter
    def protocol_md5(self, value: KBEString) -> None:
        """Установить MD5 протокола."""
        self._protocol_md5 = value

    @property
    def entity_def_md5(self) -> KBEString:
        """Получить MD5 определений сущностей."""
        return self._entity_def_md5

    @entity_def_md5.setter
    def entity_def_md5(self, value: KBEString) -> None:
        """Установить MD5 определений сущностей."""
        self._entity_def_md5 = value

    @property
    def componentType(self) -> KBEComponentType:
        """Получить тип компонента (только чтение)."""
        return self._componentType

    @property
    def tcp_addr(self) -> Addr:
        return self._tcp_addr

    async def start(self) -> Result:
        return Result(success=True, result=None)

    def stop(self) -> None:
        pass

    async def wait_until_stop(self):
        pass

    @property
    def is_started(self) -> bool:
        """Флаг запущен ли Супервизор.

        Returns:
            bool: Флаг запущен ли Супервизор

        """
        return True

    def on_receive_msg(self, msg: Message, back_channel: IMsgBackChannel) -> None:
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"


@pytest.fixture
async def loginapp_fixture(baseapp_fixture: BaseappMock):

    tcp_addr = Addr.create_default_gw_addr(Port(get_free_port()))
    kls = LoginappMock

    if TESTS_STARTED_LOGINAPP_ADDR is not None:
        res = TESTS_STARTED_LOGINAPP_ADDR.split(":")
        assert len(res) == 2, f"Invalid Loginapp address {TESTS_STARTED_LOGINAPP_ADDR}"
        host, port = res

        tcp_addr = Addr(host, Port(port))
        kls = _LoginappDataForTesting  # type: ignore

    loginapp = kls(
        tcp_addr=tcp_addr,
        baseapp_tcp_add=baseapp_fixture.tcp_addr,
        kbe_version=baseapp_fixture.kbe_version,
        assets_version=baseapp_fixture.assets_version,
        account_name=baseapp_fixture.account_name,
        password=baseapp_fixture.password,
        protocol_md5=baseapp_fixture.protocol_md5,
        entity_def_md5=baseapp_fixture.entity_def_md5,
    )
    await loginapp.start()
    yield loginapp

    loginapp.stop()
    await loginapp.wait_until_stop()


@pytest.fixture
async def loginapp_client_fixture(loginapp_fixture):
    client = LoginappClient(
        loginapp_addr=loginapp_fixture.tcp_addr,
        client_type=ComponentType.CLIENT,
        wait_response_seconds=5.0,
    )

    yield client

    client.stop()
    await client.wait_until_stop()


@pytest.fixture
def temp_dir_name():
    """Fixture that creates a temporary directory.

    Creates a temporary directory using Python's tempfile module.
    The directory is automatically removed after the test completes.

    Yields:
        str: Path to the temporary directory.

    """
    # Get a system temporary directory
    dir_name = tempfile.TemporaryDirectory()

    yield dir_name.name

    if os.path.exists(dir_name.name):
        shutil.rmtree(dir_name.name)
