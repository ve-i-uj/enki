"""Тесты клиента для серверного компонента KBEngine 'Loginapp'."""

import asyncio

import pytest
from enki.apps.clientapp.clients.loginapp_client import (
    LoginappClient,
    LoginappIsNotStartedError,
    LoginappNoResponseError,
)
from enki.kbeenum import ComponentType
from enki.misc.result import Result
from enki import msgspec
from tests.itests.app_mocks.loginapp_mock import LoginappMock


class TestLoginappClient:

    @pytest.mark.timeout(7)
    async def test_hello_success(self, loginapp_fixture: LoginappMock):
        """Тест успешного выполнения hello с корректными версиями."""
        # Arrange
        client = LoginappClient(
            loginapp_addr=loginapp_fixture.tcp_addr,
            client_type=ComponentType.CLIENT,
            wait_response_seconds=5.0,
        )

        # Запускаем клиент
        start_result = await client.start()
        assert start_result.success

        # Act - отправляем hello с версиями, которые ожидает loginapp_fixture
        # Предполагаем, что loginapp_fixture ожидает версию из baseapp_fixture.kbe_version
        result = await client.hello(
            kbe_version=loginapp_fixture.kbe_version,  # версия из фикстуры
            assets_version=loginapp_fixture.assets_version,  # можно взять из фикстуры если есть
            encrypted_key=b"test_encrypted_key",
        )

        # Assert
        assert result.success is True
        assert result.result.flag.value == "OK"
        assert result.result.kbe_version == loginapp_fixture.kbe_version
        assert result.result.encrypted_key == b"test_encrypted_key"
        assert result.result.component_type == ComponentType.LOGINAPP

    @pytest.mark.timeout(7)
    async def test_hello_kbe_version_mismatch(
        self, loginapp_fixture: LoginappMock
    ):
        """Тест несоответствия версии KBEngine."""
        # Arrange
        client = LoginappClient(
            loginapp_addr=loginapp_fixture.tcp_addr,
            client_type=ComponentType.CLIENT,
            wait_response_seconds=5.0,
        )

        start_result = await client.start()
        assert start_result.success

        # Act - отправляем неверную версию KBEngine
        wrong_kbe_version = "0.0.1"  # версия, которая не совпадает с ожидаемой
        assert wrong_kbe_version != loginapp_fixture.kbe_version
        result = await client.hello(
            kbe_version=wrong_kbe_version,
            assets_version="1.0.0",
            encrypted_key=b"test_encrypted_key",
        )

        # Assert
        assert result.success is False
        assert result.result.flag.value == "KBE_VERSION_MISMATCH"
        assert (
            result.result.kbe_version is not None
        )  # сервер вернет свою версию
        assert result.result.kbe_version != wrong_kbe_version
        assert result.result.encrypted_key == b"test_encrypted_key"
        assert "Plugin designed for KBEngine version" in result.text
        assert wrong_kbe_version in result.text

    @pytest.mark.timeout(7)
    async def test_hello_assets_version_mismatch(
        self, loginapp_fixture: LoginappMock
    ):
        """Тест несоответствия версии ассетов."""
        # Arrange
        client = LoginappClient(
            loginapp_addr=loginapp_fixture.tcp_addr,
            client_type=ComponentType.CLIENT,
            wait_response_seconds=5.0,
        )

        start_result = await client.start()
        assert start_result.success

        # Act - отправляем неверную версию ассетов
        # Предполагаем, что loginapp_fixture ожидает какую-то конкретную версию ассетов
        wrong_assets_version = "0.0.1"
        assert wrong_assets_version != loginapp_fixture.assets_version
        result = await client.hello(
            kbe_version=loginapp_fixture.kbe_version,  # верная версия KBE
            assets_version=wrong_assets_version,
            encrypted_key=b"test_encrypted_key",
        )

        # Assert
        assert result.success is False
        assert result.result.flag.value == "ASSETS_VERSION_MISMATCH"
        assert (
            result.result.assets_version is not None
        )  # сервер вернет свою версию
        assert result.result.assets_version != wrong_assets_version
        assert result.result.encrypted_key == b"test_encrypted_key"
        assert "Plugin designed for assets version" in result.text
        assert wrong_assets_version in result.text

    @pytest.mark.timeout(7)
    async def test_hello_client_not_started(
        self, loginapp_fixture: LoginappMock
    ):
        """Тест вызова hello без запуска клиента."""
        # Arrange
        client = LoginappClient(
            loginapp_addr=loginapp_fixture.tcp_addr,
            client_type=ComponentType.CLIENT,
            wait_response_seconds=5.0,
        )

        # Не запускаем клиент!

        # Act & Assert
        with pytest.raises(LoginappIsNotStartedError) as exc_info:
            await client.hello(
                kbe_version=loginapp_fixture.kbe_version,
                assets_version="1.0.0",
                encrypted_key=b"test_encrypted_key",
            )

        assert "There is no connectio to Loginapp" in str(exc_info.value)

    @pytest.mark.timeout(7)
    async def test_hello_timeout(self, loginapp_fixture: LoginappMock):
        """Тест таймаута при ожидании ответа от сервера."""
        # Arrange
        client = LoginappClient(
            loginapp_addr=loginapp_fixture.tcp_addr,
            client_type=ComponentType.CLIENT,
            wait_response_seconds=5.0,
        )

        start_result = await client.start()
        assert start_result.success

        # Act & Assert
        # Устанавливаем очень маленький таймаут, чтобы точно произошел таймаут
        with pytest.raises(LoginappNoResponseError) as exc_info:
            await client.hello(
                kbe_version=loginapp_fixture.kbe_version,
                assets_version="1.0.0",
                encrypted_key=b"test_encrypted_key",
                wait_seconds=0.001,  # очень маленький таймаут
            )

        assert "There is no response" in str(exc_info.value)
        assert "Waiting stopped by timeout" in str(exc_info.value)

    @pytest.mark.timeout(7)
    async def test_hello_with_different_client_types(
        self, loginapp_fixture: LoginappMock
    ):
        """Тест hello с разными типами клиентов."""
        client_types = [
            ComponentType.CLIENT,
            ComponentType.BOTS,
            ComponentType.TOOL,
        ]

        for client_type in client_types:
            # Arrange
            client = LoginappClient(
                loginapp_addr=loginapp_fixture.tcp_addr,
                client_type=client_type,
                wait_response_seconds=5.0,
            )

            start_result = await client.start()
            assert start_result.success

            # Act
            result = await client.hello(
                kbe_version=loginapp_fixture.kbe_version,
                assets_version=loginapp_fixture.assets_version,
                encrypted_key=b"test_encrypted_key",
            )

            # Assert
            assert result.success is True
            assert result.result.flag.value == "OK"

            # Останавливаем клиент для следующей итерации
            client.stop()

    @pytest.mark.timeout(7)
    async def test_hello_with_empty_encrypted_key(
        self, loginapp_fixture: LoginappMock
    ):
        """Тест hello с пустым encrypted_key."""
        # Arrange
        client = LoginappClient(
            loginapp_addr=loginapp_fixture.tcp_addr,
            client_type=ComponentType.CLIENT,
            wait_response_seconds=5.0,
        )

        start_result = await client.start()
        assert start_result.success

        # Act
        result = await client.hello(
            kbe_version=loginapp_fixture.kbe_version,
            assets_version=loginapp_fixture.assets_version,
            encrypted_key=b"",  # пустой ключ
        )

        # Assert
        assert result.success is True
        assert result.result.flag.value == "OK"
        assert result.result.encrypted_key == b""

    @pytest.mark.timeout(7)
    async def test_consecutive_hello_calls(
        self, loginapp_fixture: LoginappMock
    ):
        """Тест нескольких последовательных вызовов hello."""
        # Arrange
        client = LoginappClient(
            loginapp_addr=loginapp_fixture.tcp_addr,
            client_type=ComponentType.CLIENT,
            wait_response_seconds=5.0,
        )

        start_result = await client.start()
        assert start_result.success

        # Act - первый вызов
        result1 = await client.hello(
            kbe_version=loginapp_fixture.kbe_version,
            assets_version=loginapp_fixture.assets_version,
            encrypted_key=b"key1",
        )

        # Assert первого вызова
        assert result1.success is True
        assert result1.result.encrypted_key == b"key1"

        # Act - второй вызов с другими данными
        result2 = await client.hello(
            kbe_version=loginapp_fixture.kbe_version,
            assets_version=loginapp_fixture.assets_version,
            encrypted_key=b"key2",
        )

        # Assert второго вызова
        assert result2.success is True
        assert result2.result.encrypted_key == b"key2"

        # Проверяем, что оба вызова успешны и независимы
        assert result1.result.kbe_version == result2.result.kbe_version
        assert result1.result.encrypted_key != result2.result.encrypted_key

    @pytest.mark.timeout(7)
    async def test_hello_after_client_stop(
        self, loginapp_fixture: LoginappMock
    ):
        """Тест вызова hello после остановки клиента."""
        # Arrange
        client = LoginappClient(
            loginapp_addr=loginapp_fixture.tcp_addr,
            client_type=ComponentType.CLIENT,
            wait_response_seconds=5.0,
        )

        start_result = await client.start()
        assert start_result.success

        # Останавливаем клиент
        client.stop()

        # Даем время на остановку
        await asyncio.sleep(0.1)

        # Act & Assert
        with pytest.raises(LoginappIsNotStartedError) as exc_info:
            await client.hello(
                kbe_version=loginapp_fixture.kbe_version,
                assets_version=loginapp_fixture.assets_version,
                encrypted_key=b"test_encrypted_key",
            )

        assert "There is no connectio to Loginapp" in str(exc_info.value)
