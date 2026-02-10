import pytest

from enki.kbetype.pytypes.basic_data_types import KBEString
from enki.net.addr import Addr, Port
from enki.net.server import get_free_port
from tests.itests.app_mocks.loginapp_mock import LoginappMock


@pytest.fixture
async def started_loginapp(request):
    """Фикстура запущенного Loginapp."""
    kbe_version = getattr(request, "param", KBEString("2.5.10"))
    loginapp = LoginappMock(
        tcp_addr=Addr.create_default_gw_addr(Port(get_free_port())),
        kbe_version=kbe_version,
    )
    await loginapp.start()

    yield loginapp

    loginapp.stop()


def create_loginapp_fixture(kbe_version: KBEString):
    """Создает фикстуру с заданной версией."""

    @pytest.fixture
    async def loginapp_fixture():
        loginapp = LoginappMock(
            tcp_addr=Addr.create_default_gw_addr(Port(get_free_port())),
            kbe_version=kbe_version,
        )
        await loginapp.start()
        yield loginapp
        loginapp.stop()

    return loginapp_fixture


"""Фикстура запущенного Loginapp."""
started_loginapp = create_loginapp_fixture(kbe_version=KBEString("2.5.10"))
