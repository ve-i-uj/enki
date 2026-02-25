"""Тесты клиента для серверного компонента KBEngine 'Loginapp'."""

import asyncio

import pytest

from enki.apps.clientapp.clients.loginapp_client import (
    LoginappClient,
    LoginappIsNotStartedError,
    LoginappNoResponseError,
)
from enki.kbeenum import ComponentType
from tests.itests.app_mocks.loginapp_mock import LoginappMock


class TestLoginappClientHello:

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


"""Тесты для метода login клиента LoginappClient."""


import pytest

from enki.kbeenum import ClientType, ServerError
from tests.itests.app_mocks.loginapp_mock import LoginappMock


class TestLoginappClientLogin:

    @pytest.mark.timeout(7)
    async def test_login_success(self, loginapp_fixture: LoginappMock):
        """Тест успешного выполнения login с корректными учетными данными."""
        # Arrange
        client = LoginappClient(
            loginapp_addr=loginapp_fixture.tcp_addr,
            client_type=ComponentType.CLIENT,
            wait_response_seconds=5.0,
        )

        # Запускаем клиент
        start_result = await client.start()
        assert start_result.success

        account_name = loginapp_fixture.account_name
        password = loginapp_fixture.password
        entitydefs_hash = loginapp_fixture.entity_def_md5
        force_login = False

        result = await client.login(
            client_type=ClientType.MOBILE,
            client_data=b"test_client_data",
            account_name=account_name,
            password=password,
            entitydefs_hash=entitydefs_hash,
            force_login=force_login,
        )

        # Assert
        assert result.success is True
        assert result.result.ret_code == ServerError.SUCCESS
        assert result.result.baseapp_tcp_addr is not None
        assert result.result.baseapp_udp_addr is not None

    @pytest.mark.timeout(7)
    async def test_login_failed(self, loginapp_fixture: LoginappMock):
        """Тест неуспешного выполнения login с неверными учетными данными."""
        # Arrange
        client = LoginappClient(
            loginapp_addr=loginapp_fixture.tcp_addr,
            client_type=ComponentType.CLIENT,
            wait_response_seconds=5.0,
        )

        start_result = await client.start()
        assert start_result.success

        # Act - отправляем login с неверными данными
        # loginapp_fixture должен быть настроен на возврат ошибки для этих данных
        account_name = "wronguser"
        password = "wrongpass"
        entitydefs_hash = "wrong_hash"
        force_login = False

        assert account_name != loginapp_fixture.account_name
        assert password != loginapp_fixture.password

        result = await client.login(
            client_type=ClientType.MOBILE,
            client_data=b"test_client_data",
            account_name=account_name,
            password=password,
            entitydefs_hash=entitydefs_hash,
            force_login=force_login,
        )

        # Assert
        assert result.success is False
        assert result.result.ret_code != ServerError.SUCCESS
        assert isinstance(result.result.ret_code, ServerError)
        assert result.result.baseapp_tcp_addr is None
        assert result.result.baseapp_udp_addr is None
        assert "Login Falied" in result.text
        assert result.result.ret_code.name in result.text

    @pytest.mark.timeout(7)
    async def test_login_with_empty_client_data(
        self, loginapp_fixture: LoginappMock
    ):
        """Тест login с пустыми client_data."""
        # Arrange
        client = LoginappClient(
            loginapp_addr=loginapp_fixture.tcp_addr,
            client_type=ComponentType.CLIENT,
            wait_response_seconds=5.0,
        )

        start_result = await client.start()
        assert start_result.success

        # Act
        result = await client.login(
            client_type=ClientType.MOBILE,
            client_data=b"",  # пустые данные клиента
            account_name=loginapp_fixture.account_name,
            password=loginapp_fixture.password,
            entitydefs_hash=loginapp_fixture.entity_def_md5,
            force_login=False,
        )

        # Assert
        assert result.success is True
        assert result.result.ret_code == ServerError.SUCCESS

    @pytest.mark.timeout(7)
    async def test_login_client_not_started(
        self, loginapp_fixture: LoginappMock
    ):
        """Тест вызова login без запуска клиента."""
        # Arrange
        client = LoginappClient(
            loginapp_addr=loginapp_fixture.tcp_addr,
            client_type=ComponentType.CLIENT,
            wait_response_seconds=5.0,
        )

        # Не запускаем клиент!

        # Act & Assert
        with pytest.raises(LoginappIsNotStartedError) as exc_info:
            await client.login(
                client_type=ClientType.MOBILE,
                client_data=b"test_client_data",
                account_name="testuser",
                password="testpass",
                entitydefs_hash="test_hash",
                force_login=False,
            )

        assert "There is no connectio to Loginapp" in str(exc_info.value)

    @pytest.mark.timeout(7)
    async def test_login_timeout(self, loginapp_fixture: LoginappMock):
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
            await client.login(
                client_type=ClientType.MOBILE,
                client_data=b"test_client_data",
                account_name="testuser",
                password="testpass",
                entitydefs_hash="test_hash",
                force_login=False,
                wait_seconds=0.001,  # очень маленький таймаут
            )

        assert "There is no response" in str(exc_info.value)
        assert "Waiting stopped by timeout" in str(exc_info.value)

    @pytest.mark.timeout(7)
    async def test_login_with_different_entitydefs_hash(
        self, loginapp_fixture: LoginappMock
    ):
        """Тест login с неверным значением entitydefs_hash."""
        # Arrange
        client = LoginappClient(
            loginapp_addr=loginapp_fixture.tcp_addr,
            client_type=ComponentType.CLIENT,
            wait_response_seconds=5.0,
        )

        start_result = await client.start()
        assert start_result.success

        entitydefs_hash = "!@#$%^&*()"

        assert entitydefs_hash != loginapp_fixture.entity_def_md5
        # Act
        result = await client.login(
            client_type=ClientType.MOBILE,
            client_data=b"test_client_data",
            account_name=loginapp_fixture.account_name,
            password=loginapp_fixture.password,
            entitydefs_hash=entitydefs_hash,
            force_login=False,
        )

        # Assert
        assert result.success is False
        assert result.result is not None
        assert result.result.ret_code == ServerError.ENTITYDEFS_NOT_MATCH

    @pytest.mark.timeout(7)
    async def test_consecutive_login_calls(
        self, loginapp_fixture: LoginappMock
    ):
        """Тест нескольких последовательных вызовов login."""
        # Arrange
        client = LoginappClient(
            loginapp_addr=loginapp_fixture.tcp_addr,
            client_type=ComponentType.CLIENT,
            wait_response_seconds=5.0,
        )

        start_result = await client.start()
        assert start_result.success

        result = await client.login(
            client_type=ClientType.MOBILE,
            client_data=b"test_client_data",
            account_name=loginapp_fixture.account_name,
            password=loginapp_fixture.password,
            entitydefs_hash=loginapp_fixture.entity_def_md5,
            force_login=False,
        )

        assert result.success

        # Act - несколько последовательных входов
        for _i in range(3):
            result = await client.login(
                client_type=ClientType.MOBILE,
                client_data=b"test_client_data",
                account_name=loginapp_fixture.account_name,
                password=loginapp_fixture.password,
                entitydefs_hash=loginapp_fixture.entity_def_md5,
                force_login=False,
            )

            # Assert
            assert result.success is False

    @pytest.mark.timeout(7)
    async def test_login_after_client_stop(
        self, loginapp_fixture: LoginappMock
    ):
        """Тест вызова login после остановки клиента."""
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
            await client.login(
                client_type=ClientType.MOBILE,
                client_data=b"test_client_data",
                account_name="testuser",
                password="testpass",
                entitydefs_hash="test_hash",
                force_login=False,
            )

        assert "There is no connectio to Loginapp" in str(exc_info.value)
