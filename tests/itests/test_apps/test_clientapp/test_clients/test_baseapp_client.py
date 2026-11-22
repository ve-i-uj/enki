"""Тесты клиента для серверного компонента KBEngine 'Baseapp'."""

import asyncio
from datetime import datetime

import pytest

from enki.apps.clientapp.clients.baseapp_client import (
    BaseappClient,
    BaseappIsNotStartedError,
)
from enki.settings import SECOND
from tests.itests.app_mocks.baseapp_mock import BaseappMock


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
