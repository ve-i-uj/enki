import pytest

from enki.kbetype.pytypes.basic_data_types import KBEString
from enki.net.addr import Addr, Port
from enki.net.server import get_free_port
from tests.itests.app_mocks.baseapp_mock import BaseappMock
from tests.itests.app_mocks.loginapp_mock import LoginappMock


def create_loginapp_fixture(kbe_version: KBEString):
    """Создает фикстуру с заданной версией."""

    @pytest.fixture
    async def loginapp_fixture(started_baseapp: BaseappMock):
        loginapp = LoginappMock(
            tcp_addr=Addr.create_default_gw_addr(Port(get_free_port())),
            baseapp_tcp_add=started_baseapp.tcp_addr,
            kbe_version=kbe_version,
        )
        await loginapp.start()
        yield loginapp
        loginapp.stop()

    return loginapp_fixture


def create_baseapp_fixture(kbe_version: KBEString):
    """Создает фикстуру с заданной версией."""

    @pytest.fixture
    async def baseapp_fixture():
        """Фикстура запущенного Baseapp."""
        baseapp = BaseappMock(
            tcp_addr=Addr.create_default_gw_addr(Port(get_free_port())),
            kbe_version=kbe_version,
        )
        await baseapp.start()

        yield baseapp

        baseapp.stop()

    return baseapp_fixture


"""Фикстура запущенного Baseapp."""
started_baseapp = create_baseapp_fixture(kbe_version=KBEString("2.5.10"))
"""Фикстура запущенного Loginapp."""
started_loginapp = create_loginapp_fixture(kbe_version=KBEString("2.5.10"))
