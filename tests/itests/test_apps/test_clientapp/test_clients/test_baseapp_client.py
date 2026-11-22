"""Тесты клиента для серверного компонента KBEngine 'Baseapp'."""

import asyncio
from datetime import datetime

import pytest

from enki.apps.clientapp.clients.baseapp_client import (
    BaseappClient,
    BaseappIsNotStartedError,
)
from enki.apps.clientapp.clients.loginapp_client import LoginappClient
from enki.kbeenum import ClientType, ComponentType, ServerError
from enki.settings import SECOND
from tests.itests.app_mocks.baseapp_mock import BaseappMock
from tests.itests.app_mocks.loginapp_mock import LoginappMock
from tests.itests.conftest import is_real_kbengine_baseapp, is_real_kbengine_loginapp


class TestBaseappClientStartStop:

    @pytest.mark.timeout(7)
    async def test_start_success(
        self, baseapp_client_fixture: BaseappClient, baseapp_fixture: BaseappMock
    ) -> None:
        """Успешный запуск клиента."""
        client = baseapp_client_fixture

        assert client.is_started is False
        start_result = await client.start()

        assert start_result.success is True
        assert client.is_started is True

    @pytest.mark.timeout(7)
    async def test_start_unreachable(self) -> None:
        """Запуск клиента при недоступном сервере."""
        from enki.net.addr import Addr  # noqa: PLC0415

        # Несуществующий адрес
        client = BaseappClient(Addr("127.0.0.1", 1), ComponentType.CLIENT, 60, 60)
        start_result = await client.start()

        assert start_result.success is False
        assert "not reachable" in start_result.text

    @pytest.mark.timeout(7)
    async def test_stop(
        self, baseapp_client_fixture: BaseappClient, baseapp_fixture: BaseappMock
    ) -> None:
        """Остановка клиента."""
        client = baseapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        client.stop()
        await asyncio.sleep(0.1)

        assert client.is_started is False

    @pytest.mark.skipif(is_real_kbengine_loginapp(), reason="Only for Baseapp Mock")
    @pytest.mark.timeout(7)
    async def test_lost_connection(
        self, baseapp_client_fixture: BaseappClient, baseapp_fixture: BaseappMock
    ) -> None:
        """Клиент корректно реагирует на разрыв соединения сервером."""
        client = baseapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        baseapp_fixture.stop()
        await baseapp_fixture.wait_until_stop()

        await asyncio.sleep(0.1)
        # Клиент должен быть в состоянии "не запущен"
        assert client.is_started is False


class TestBaseappClientLoginBaseapp:

    @pytest.mark.timeout(7)
    async def test_loginbaseapp_success(
        self,
        loginapp_client_fixture: LoginappClient,
        loginapp_fixture: LoginappMock,
        baseapp_client_fixture: BaseappClient,
        baseapp_fixture: BaseappMock,
    ) -> None:
        """Успешный логин на Baseapp.

        Для успешного подключения нужно сперва залогиниться на Loginapp.
        """
        baseapp_client = baseapp_client_fixture
        loginapp_client = loginapp_client_fixture

        res = await loginapp_client.start()
        assert res.success
        account_name = loginapp_fixture.account_name
        password = loginapp_fixture.password
        entitydefs_hash = loginapp_fixture.entity_def_md5
        force_login = False

        result = await loginapp_client.login(
            client_type=ClientType.MOBILE,
            client_data=b"test_client_data",
            account_name=account_name,
            password=password,
            entitydefs_hash=entitydefs_hash,
            force_login=force_login,
        )

        assert result.success is True
        assert result.result.ret_code == ServerError.SUCCESS

        start_result = await baseapp_client.start()
        assert start_result.success

        result = await baseapp_client.loginBaseapp(
            account_name=baseapp_fixture.account_name,
            password=baseapp_fixture.password,
        )

        assert result.success is True

    @pytest.mark.skipif(
        not is_real_kbengine_loginapp() and not is_real_kbengine_baseapp(),
        reason="Only for real Baseapp and Loginapp",
    )
    @pytest.mark.timeout(7)
    async def test_loginbaseapp_not_success(
        self,
        baseapp_client_fixture: BaseappClient,
        baseapp_fixture: BaseappMock,
    ) -> None:
        """Не успешный логин на Baseapp (без предварительного логина от Loginapp)."""
        baseapp_client = baseapp_client_fixture
        start_result = await baseapp_client.start()
        assert start_result.success

        result = await baseapp_client.loginBaseapp(
            account_name=baseapp_fixture.account_name,
            password=baseapp_fixture.password,
        )

        assert result.success is False
        assert isinstance(result.result, ServerError)
        assert result.result == ServerError.ILLEGAL_LOGIN

    @pytest.mark.timeout(7)
    async def test_loginbaseapp_client_not_started(
        self, baseapp_client_fixture: BaseappClient, baseapp_fixture: BaseappMock
    ) -> None:
        """Логин без предварительного start()."""
        client = baseapp_client_fixture
        with pytest.raises(BaseappIsNotStartedError):
            _ = await client.loginBaseapp(
                account_name=baseapp_fixture.account_name,
                password=baseapp_fixture.password,
            )


class TestBaseappClientOnClientActiveTick:

    @pytest.mark.timeout(7)
    async def test_onClientActiveTick_success(
        self, baseapp_client_fixture: BaseappClient, baseapp_fixture: BaseappMock
    ):
        """Тест успешного выполнения onClientActiveTick (работает и без логина)."""
        client = baseapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        result = await client.onClientActiveTick(wait_seconds=5 * SECOND)

        assert result.success is True
        assert result.result is not None
        assert isinstance(result.result.resp_dt, datetime)

    @pytest.mark.timeout(7)
    async def test_onClientActiveTick_client_not_started(
        self, baseapp_client_fixture: BaseappClient, baseapp_fixture: BaseappMock
    ):
        """Тест вызова onClientActiveTick без запуска клиента."""
        client = baseapp_client_fixture
        # Не запускаем клиент

        with pytest.raises(BaseappIsNotStartedError):
            await client.onClientActiveTick(wait_seconds=5 * SECOND)

    @pytest.mark.timeout(7)
    async def test_onClientActiveTick_after_client_stop(
        self, baseapp_client_fixture: BaseappClient, baseapp_fixture: BaseappMock
    ):
        """Тест вызова hello после остановки клиента."""
        client = baseapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        client.stop()

        await asyncio.sleep(0.1)

        with pytest.raises(BaseappIsNotStartedError):
            await client.onClientActiveTick(wait_seconds=5 * SECOND)
