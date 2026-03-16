"""Тесты клиента для серверного компонента KBEngine 'Loginapp'."""

import asyncio
import random
import string
from datetime import datetime

import pytest

from enki import settings
from enki.apps.clientapp.clients.loginapp_client import (
    LoginappClient,
    LoginappIsNotStartedError,
    LoginappNoResponseError,
)
from enki.kbeenum import ClientType, ComponentType, ServerError
from enki.settings import SECOND
from tests.itests.app_mocks.loginapp_mock import LoginappMock
from tests.itests.conftest import is_real_kbengine_loginapp


class TestLoginappClient:

    @pytest.mark.skipif(is_real_kbengine_loginapp(), reason="Only for Loginapp Mock")
    @pytest.mark.timeout(7)
    async def test_lost_connection(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ):
        """Тест работы клиента при разрыве соединения."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        loginapp_fixture.stop()
        await loginapp_fixture.wait_until_stop()

        # Смотрим, как ведёт себя клиент
        await client.wait_until_stop()


class TestLoginappClientHello:

    @pytest.mark.timeout(7)
    async def test_hello_success(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ):
        """Тест успешного выполнения hello с корректными версиями."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        result = await client.hello(
            kbe_version=loginapp_fixture.kbe_version,
            assets_version=loginapp_fixture.assets_version,
            encrypted_key=b"test_encrypted_key",
        )

        assert result.success is True
        assert result.result.flag.value == "OK"
        assert result.result.kbe_version == loginapp_fixture.kbe_version
        assert result.result.encrypted_key == b"test_encrypted_key"
        assert result.result.component_type == ComponentType.LOGINAPP

    @pytest.mark.timeout(7)
    async def test_hello_kbe_version_mismatch(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ):
        """Тест несоответствия версии KBEngine."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        wrong_kbe_version = "0.0.1"
        assert wrong_kbe_version != loginapp_fixture.kbe_version
        result = await client.hello(
            kbe_version=wrong_kbe_version,
            assets_version="0.1.0",
            encrypted_key=b"test_encrypted_key",
        )

        assert result.success is False
        assert result.result.flag.value == "KBE_VERSION_MISMATCH"
        assert result.result.kbe_version is not None
        assert result.result.kbe_version != wrong_kbe_version
        assert result.result.encrypted_key == b"test_encrypted_key"
        assert "Plugin designed for KBEngine version" in result.text
        assert wrong_kbe_version in result.text

    @pytest.mark.timeout(7)
    async def test_hello_assets_version_mismatch(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ):
        """Тест несоответствия версии ассетов."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        wrong_assets_version = "0.0.1"
        assert wrong_assets_version != loginapp_fixture.assets_version
        result = await client.hello(
            kbe_version=loginapp_fixture.kbe_version,
            assets_version=wrong_assets_version,
            encrypted_key=b"test_encrypted_key",
        )

        assert result.success is False
        assert result.result.flag.value == "ASSETS_VERSION_MISMATCH"
        assert result.result.assets_version is not None
        assert result.result.assets_version != wrong_assets_version
        assert result.result.encrypted_key == b"test_encrypted_key"
        assert "Plugin designed for assets version" in result.text
        assert wrong_assets_version in result.text

    @pytest.mark.timeout(7)
    async def test_hello_client_not_started(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ):
        """Тест вызова hello без запуска клиента."""
        client = loginapp_client_fixture
        # Не запускаем клиент

        with pytest.raises(LoginappIsNotStartedError):
            await client.hello(
                kbe_version=loginapp_fixture.kbe_version,
                assets_version="0.1.0",
                encrypted_key=b"test_encrypted_key",
            )

    @pytest.mark.timeout(7)
    async def test_hello_timeout(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ):
        """Тест таймаута при ожидании ответа от сервера."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        with pytest.raises(LoginappNoResponseError) as exc_info:
            await client.hello(
                kbe_version=loginapp_fixture.kbe_version,
                assets_version="0.1.0",
                encrypted_key=b"test_encrypted_key",
                wait_seconds=0,
            )

        assert "There is no response" in str(exc_info.value)
        assert "Waiting stopped by timeout" in str(exc_info.value)

    @pytest.mark.timeout(7)
    async def test_hello_with_different_client_types(
        self, loginapp_fixture: LoginappMock, loginapp_client_fixture
    ):
        """Тест hello с разными типами клиентов."""
        # В фикстуре клиент создается с ComponentType.CLIENT, поэтому для других типов
        # создаем клиентов напрямую
        client_types = [
            ComponentType.CLIENT,
            ComponentType.BOTS,
            ComponentType.TOOL,
        ]

        for client_type in client_types:
            if client_type == ComponentType.CLIENT:
                client = loginapp_client_fixture
            else:
                # Для других типов создаем отдельного клиента
                from enki.apps.clientapp.clients.loginapp_client import (
                    LoginappClient,
                )

                client = LoginappClient(
                    loginapp_addr=loginapp_fixture.tcp_addr,
                    client_type=client_type,
                    wait_response_seconds=5,
                    server_tick_period=settings.SERVER_TICK_PERIOD,
                )

            start_result = await client.start()
            assert start_result.success

            result = await client.hello(
                kbe_version=loginapp_fixture.kbe_version,
                assets_version=loginapp_fixture.assets_version,
                encrypted_key=b"test_encrypted_key",
            )

            assert result.success is True
            assert result.result.flag.value == "OK"

            if client_type != ComponentType.CLIENT:
                client.stop()

    @pytest.mark.timeout(7)
    async def test_hello_with_empty_encrypted_key(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ):
        """Тест hello с пустым encrypted_key."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        result = await client.hello(
            kbe_version=loginapp_fixture.kbe_version,
            assets_version=loginapp_fixture.assets_version,
            encrypted_key=b"",
        )

        assert result.success is True
        assert result.result.flag.value == "OK"
        assert result.result.encrypted_key == b""

    @pytest.mark.timeout(7)
    async def test_consecutive_hello_calls(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ):
        """Тест нескольких последовательных вызовов hello."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        result1 = await client.hello(
            kbe_version=loginapp_fixture.kbe_version,
            assets_version=loginapp_fixture.assets_version,
            encrypted_key=b"key1",
        )

        assert result1.success is True
        assert result1.result.encrypted_key == b"key1"

        result2 = await client.hello(
            kbe_version=loginapp_fixture.kbe_version,
            assets_version=loginapp_fixture.assets_version,
            encrypted_key=b"key2",
        )

        assert result2.success is True
        assert result2.result.encrypted_key == b"key2"

        assert result1.result.kbe_version == result2.result.kbe_version
        assert result1.result.encrypted_key != result2.result.encrypted_key

    @pytest.mark.timeout(7)
    async def test_hello_after_client_stop(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ):
        """Тест вызова hello после остановки клиента."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        client.stop()

        await asyncio.sleep(0.1)

        with pytest.raises(LoginappIsNotStartedError) as exc_info:
            await client.hello(
                kbe_version=loginapp_fixture.kbe_version,
                assets_version=loginapp_fixture.assets_version,
                encrypted_key=b"test_encrypted_key",
            )

        assert "There is no connection to Loginapp" in str(exc_info.value)


class TestLoginappClientLogin:

    @pytest.mark.timeout(7)
    async def test_login_success(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ):
        """Тест успешного выполнения login с корректными учетными данными."""
        client = loginapp_client_fixture

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

        assert result.success is True
        assert result.result.ret_code == ServerError.SUCCESS
        assert result.result.baseapp_tcp_addr is not None
        assert result.result.baseapp_udp_addr is not None

    @pytest.mark.timeout(7)
    async def test_login_failed(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ):
        """Тест неуспешного выполнения login с неверными учетными данными."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

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

        assert result.success is False
        assert result.result.ret_code != ServerError.SUCCESS
        assert isinstance(result.result.ret_code, ServerError)
        assert result.result.baseapp_tcp_addr is None
        assert result.result.baseapp_udp_addr is None
        assert "Login Falied" in result.text
        assert result.result.ret_code.name in result.text

    @pytest.mark.timeout(7)
    async def test_login_with_empty_client_data(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ):
        """Тест login с пустыми client_data."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        result = await client.login(
            client_type=ClientType.MOBILE,
            client_data=b"",
            account_name=loginapp_fixture.account_name,
            password=loginapp_fixture.password,
            entitydefs_hash=loginapp_fixture.entity_def_md5,
            force_login=False,
        )

        assert result.success is True
        assert result.result.ret_code == ServerError.SUCCESS

    @pytest.mark.timeout(7)
    async def test_login_client_not_started(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ):
        """Тест вызова login без запуска клиента."""
        client = loginapp_client_fixture
        # Не запускаем клиент

        with pytest.raises(LoginappIsNotStartedError):
            await client.login(
                client_type=ClientType.MOBILE,
                client_data=b"test_client_data",
                account_name="testuser",
                password="testpass",
                entitydefs_hash="test_hash",
                force_login=False,
            )

    @pytest.mark.timeout(7)
    async def test_login_timeout(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ):
        """Тест таймаута при ожидании ответа от сервера."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        with pytest.raises(LoginappNoResponseError) as exc_info:
            await client.login(
                client_type=ClientType.MOBILE,
                client_data=b"test_client_data",
                account_name=loginapp_fixture.account_name,
                password=loginapp_fixture.password,
                entitydefs_hash=loginapp_fixture.entity_def_md5,
                force_login=False,
                wait_seconds=0,
            )

        assert "There is no response" in str(exc_info.value)
        assert "Waiting stopped by timeout" in str(exc_info.value)


class TestLoginappClientReqCreateAccount:

    @pytest.mark.timeout(7)
    async def test_req_create_account_success(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ) -> None:
        """Успешное создание аккаунта с корректными данными."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        username = "".join(random.choices(string.ascii_letters + string.digits, k=10))
        password = "".join(random.choices(string.ascii_letters + string.digits, k=10))
        create_account_data = b"test_create_account_data"

        result = await client.reqCreateAccount(
            username=username,
            password=password,
            create_account_data=create_account_data,
        )

        assert result.success is True
        assert result.result is not None
        assert result.result.ret_code == ServerError.SUCCESS
        # Из серверных скриптов подменяются данные
        assert result.result.data == b""

    @pytest.mark.timeout(7)
    async def test_req_create_account_empty_username(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ) -> None:
        """Создание аккаунта с пустым именем пользователя."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        result = await client.reqCreateAccount(
            username="",
            password=loginapp_fixture.password,
            create_account_data=b"test_data",
        )

        assert result.success is False
        assert result.result is not None
        assert result.result.ret_code == ServerError.NAME

    @pytest.mark.timeout(7)
    async def test_req_create_account_empty_password(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ) -> None:
        """Создание аккаунта с пустым паролем."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        result = await client.reqCreateAccount(
            username="user",
            password="",
            create_account_data=b"test_data",
        )

        assert result.success is False
        assert result.result is not None
        assert result.result.ret_code == ServerError.ACCOUNT_CREATE_FAILED

    @pytest.mark.timeout(7)
    async def test_req_create_account_client_not_started(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ) -> None:
        """Вызов reqCreateAccount без запуска клиента."""
        client = loginapp_client_fixture
        # Не запускаем клиент

        with pytest.raises(LoginappIsNotStartedError):
            await client.reqCreateAccount(
                username="user",
                password="password",
                create_account_data=b"test_data",
            )


class TestLoginappClientReqCreateMailAccount:

    @pytest.mark.timeout(7)
    async def test_req_create_mail_account_success(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ) -> None:
        """Успешное создание почтового аккаунта с корректными данными."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        username = "".join(random.choices(string.ascii_letters + string.digits, k=10))
        email = f"{username}@example.com"
        password = loginapp_fixture.password
        create_account_data = b"test_mail_create_account_data"

        result = await client.reqCreateMailAccount(
            email=email,
            password=password,
            create_account_data=create_account_data,
        )

        assert result.success is True
        assert result.result is not None
        assert result.result.ret_code == ServerError.SUCCESS
        assert result.result.data == create_account_data

    @pytest.mark.timeout(7)
    async def test_req_create_not_mail_account_success(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ) -> None:
        """Имя аккаунта не email."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        email = "not_email"
        password = loginapp_fixture.password
        create_account_data = b"test_mail_create_account_data"

        result = await client.reqCreateMailAccount(
            email=email,
            password=password,
            create_account_data=create_account_data,
        )

        assert result.success is False
        assert result.result is not None
        assert result.result.ret_code == ServerError.NAME_MAIL
        assert result.result.data == create_account_data

    @pytest.mark.timeout(7)
    async def test_req_create_mail_account_empty_email(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ) -> None:
        """Создание почтового аккаунта с пустым email."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        result = await client.reqCreateMailAccount(
            email="",
            password="password",
            create_account_data=b"test_data",
        )

        assert result.success is False
        assert result.result is not None
        assert result.result.ret_code == ServerError.NAME

    @pytest.mark.timeout(7)
    async def test_req_create_mail_account_empty_password(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ) -> None:
        """Создание почтового аккаунта с пустым паролем."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        result = await client.reqCreateMailAccount(
            email="user@example.com",
            password="",
            create_account_data=b"test_data",
        )

        assert result.success is False
        assert result.result is not None
        assert result.result.ret_code == ServerError.ACCOUNT_CREATE_FAILED

    @pytest.mark.timeout(7)
    async def test_req_create_mail_account_client_not_started(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ) -> None:
        """Вызов reqCreateMailAccount без запуска клиента."""
        client = loginapp_client_fixture
        # Не запускаем клиент

        with pytest.raises(LoginappIsNotStartedError):
            await client.reqCreateMailAccount(
                email="user@example.com",
                password="password",
                create_account_data=b"test_data",
            )

    @pytest.mark.timeout(7)
    async def test_req_create_mail_after_client_stop(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ):
        """Тест вызова login после остановки клиента."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        client.stop()

        await asyncio.sleep(0.1)

        email = loginapp_fixture.account_name
        password = loginapp_fixture.password
        create_account_data = b"test_mail_create_account_data"

        with pytest.raises(LoginappIsNotStartedError):
            await client.reqCreateMailAccount(
                email=email,
                password=password,
                create_account_data=create_account_data,
            )


class TestLoginappClientReqAccountResetPassword:

    @pytest.mark.timeout(7)
    async def test_req_account_reset_password_success(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ) -> None:
        """Успешный запрос на сброс пароля для существующего аккаунта."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        # Сначала создаем аккаунт, чтобы он существовал
        username = "".join(random.choices(string.ascii_letters + string.digits, k=10))
        password = "".join(random.choices(string.ascii_letters + string.digits, k=10))
        create_result = await client.reqCreateAccount(
            username=username,
            password=password,
            create_account_data=b"test_data",
        )
        assert create_result.success is True

        # Запрашиваем сброс пароля для созданного аккаунта
        result = await client.reqAccountResetPassword(
            account_name=username,
        )

        assert result.success is True
        assert result.result.ret_code == ServerError.SUCCESS
        assert "Account password reset request accepted" in result.text

    @pytest.mark.timeout(7)
    async def test_req_account_reset_password_nonexistent_account(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ) -> None:
        """Запрос на сброс пароля для несуществующего аккаунта."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        # Используем имя аккаунта, которое точно не существует
        nonexistent_account = "nonexistent_account_12345"

        result = await client.reqAccountResetPassword(
            account_name=nonexistent_account,
        )

        # Согласно обновленному моку, ответ всегда SUCCESS
        # В реальном сервере была бы ошибка, но в моке мы упростили
        assert result.success is True
        assert result.result.ret_code == ServerError.SUCCESS

    @pytest.mark.timeout(7)
    async def test_req_account_reset_password_empty_account_name(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ) -> None:
        """Запрос на сброс пароля с пустым именем аккаунта."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        result = await client.reqAccountResetPassword(
            account_name="",
        )

        # Мок тримит пустую строку, оставляя пустоту, и отвечает SUCCESS
        assert result.success is True
        assert result.result.ret_code == ServerError.SUCCESS

    @pytest.mark.timeout(7)
    async def test_req_account_reset_password_account_name_with_spaces(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ) -> None:
        """Запрос на сброс пароля с именем аккаунта, содержащим пробелы."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        # Создаем аккаунт без пробелов
        username = "".join(random.choices(string.ascii_letters + string.digits, k=10))
        password = "".join(random.choices(string.ascii_letters + string.digits, k=10))
        create_result = await client.reqCreateAccount(
            username=username,
            password=password,
            create_account_data=b"test_data",
        )
        assert create_result.success is True

        # Запрашиваем с пробелами вокруг имени - мок должен сделать strip
        account_name_with_spaces = f"  {username}  "
        result = await client.reqAccountResetPassword(
            account_name=account_name_with_spaces,
        )

        # После strip имя должно совпасть с созданным аккаунтом
        assert result.success is True
        assert result.result.ret_code == ServerError.SUCCESS

    @pytest.mark.timeout(7)
    async def test_req_account_reset_password_client_not_started(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ) -> None:
        """Вызов reqAccountResetPassword без запуска клиента."""
        client = loginapp_client_fixture
        # Не запускаем клиент

        with pytest.raises(LoginappIsNotStartedError):
            await client.reqAccountResetPassword(
                account_name="testuser",
            )

    @pytest.mark.timeout(7)
    async def test_req_account_reset_password_timeout(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ) -> None:
        """Тест таймаута при ожидании ответа от сервера."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        with pytest.raises(LoginappNoResponseError) as exc_info:
            await client.reqAccountResetPassword(
                account_name="testuser",
                wait_seconds=0,
            )

        assert "There is no response" in str(exc_info.value)
        assert "Waiting stopped by timeout" in str(exc_info.value)

    @pytest.mark.timeout(7)
    async def test_req_account_reset_password_after_client_stop(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ) -> None:
        """Вызов reqAccountResetPassword после остановки клиента."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        client.stop()

        await asyncio.sleep(0.1)

        with pytest.raises(LoginappIsNotStartedError):
            await client.reqAccountResetPassword(
                account_name="testuser",
            )

    @pytest.mark.timeout(7)
    async def test_req_account_reset_password_consecutive_calls(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ) -> None:
        """Несколько последовательных вызовов reqAccountResetPassword."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        # Создаем несколько аккаунтов
        accounts = []
        for _ in range(3):
            username = "".join(
                random.choices(string.ascii_letters + string.digits, k=10)
            )
            password = "".join(
                random.choices(string.ascii_letters + string.digits, k=10)
            )
            create_result = await client.reqCreateAccount(
                username=username,
                password=password,
                create_account_data=b"test_data",
            )
            assert create_result.success is True
            accounts.append(username)

        # Последовательно запрашиваем сброс пароля для каждого
        for account in accounts:
            result = await client.reqAccountResetPassword(
                account_name=account,
            )
            assert result.success is True
            assert result.result.ret_code == ServerError.SUCCESS

    @pytest.mark.timeout(7)
    async def test_req_account_reset_password_same_account_multiple_times(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ) -> None:
        """Многократный запрос сброса пароля для одного аккаунта."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        # Создаем аккаунт
        username = "".join(random.choices(string.ascii_letters + string.digits, k=10))
        password = "".join(random.choices(string.ascii_letters + string.digits, k=10))
        create_result = await client.reqCreateAccount(
            username=username,
            password=password,
            create_account_data=b"test_data",
        )
        assert create_result.success is True

        # Несколько раз запрашиваем сброс пароля
        for _ in range(3):
            result = await client.reqAccountResetPassword(
                account_name=username,
            )
            assert result.success is True
            assert result.result.ret_code == ServerError.SUCCESS

    @pytest.mark.timeout(7)
    async def test_req_account_reset_password_with_different_client_types(
        self, loginapp_fixture: LoginappMock
    ) -> None:
        """Тест reqAccountResetPassword с разными типами клиентов."""
        from enki.apps.clientapp.clients.loginapp_client import LoginappClient

        client_types = [
            ComponentType.CLIENT,
            ComponentType.BOTS,
            ComponentType.TOOL,
        ]

        for client_type in client_types:
            # Создаем отдельного клиента для каждого типа
            client = LoginappClient(
                loginapp_addr=loginapp_fixture.tcp_addr,
                client_type=client_type,
                wait_response_seconds=5.0,
                server_tick_period=settings.SERVER_TICK_PERIOD,
            )

            start_result = await client.start()
            assert start_result.success

            # Создаем аккаунт
            username = "".join(
                random.choices(string.ascii_letters + string.digits, k=10)
            )
            password = "".join(
                random.choices(string.ascii_letters + string.digits, k=10)
            )
            create_result = await client.reqCreateAccount(
                username=username,
                password=password,
                create_account_data=b"test_data",
            )
            assert create_result.success is True

            # Запрашиваем сброс пароля
            result = await client.reqAccountResetPassword(
                account_name=username,
            )

            assert result.success is True
            assert result.result.ret_code == ServerError.SUCCESS

            client.stop()
            await asyncio.sleep(0.1)


class TestLoginappClientOnClientActiveTick:

    @pytest.mark.timeout(7)
    async def test_onClientActiveTick_success(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ):
        """Тест успешного выполнения onClientActiveTick."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        result = await client.onClientActiveTick(wait_seconds=5 * SECOND)

        assert result.success is True
        assert result.result is not None
        assert isinstance(result.result.resp_dt, datetime)

    @pytest.mark.timeout(7)
    async def test_onClientActiveTick_client_not_started(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ):
        """Тест вызова onClientActiveTick без запуска клиента."""
        client = loginapp_client_fixture
        # Не запускаем клиент

        with pytest.raises(LoginappIsNotStartedError):
            await client.onClientActiveTick(wait_seconds=5 * SECOND)

    @pytest.mark.timeout(7)
    async def test_hello_timeout(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ):
        """Тест таймаута при ожидании ответа от сервера."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        with pytest.raises(LoginappNoResponseError):
            await client.onClientActiveTick(
                wait_seconds=0,
            )

    @pytest.mark.timeout(7)
    async def test_onClientActiveTick_after_client_stop(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ):
        """Тест вызова hello после остановки клиента."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        client.stop()

        await asyncio.sleep(0.1)

        with pytest.raises(LoginappIsNotStartedError):
            await client.onClientActiveTick(wait_seconds=5 * SECOND)


class TestLoginappClientImportClientMessages:

    @pytest.mark.timeout(7)
    async def test_import_client_messages_success(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ) -> None:
        """Успешный импорт описаний сообщений."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        result = await client.importClientMessages()

        assert result.success is True
        assert result.result is not None
        assert len(result.result.client_msgs_descr) > 0
        assert len(result.result.loginapp_msgs_descr) > 0

        # Проверяем, что все сообщения имеют правильные типы компонентов
        for msg_descr in result.result.client_msgs_descr:
            assert msg_descr.component_type == ComponentType.CLIENT
        for msg_descr in result.result.loginapp_msgs_descr:
            assert msg_descr.component_type == ComponentType.LOGINAPP

    @pytest.mark.timeout(7)
    async def test_import_client_messages_with_custom_timeout(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ) -> None:
        """Импорт описаний сообщений с кастомным таймаутом."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        result = await client.importClientMessages(wait_seconds=10)

        assert result.success is True
        assert result.result is not None
        assert len(result.result.client_msgs_descr) > 0
        assert len(result.result.loginapp_msgs_descr) > 0

    @pytest.mark.timeout(7)
    async def test_import_client_messages_client_not_started(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ) -> None:
        """Вызов importClientMessages без запуска клиента."""
        client = loginapp_client_fixture
        # Не запускаем клиент

        with pytest.raises(LoginappIsNotStartedError):
            await client.importClientMessages()

    @pytest.mark.timeout(7)
    async def test_import_client_messages_connection_error(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ) -> None:
        """Ошибка соединения при импорте сообщений."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        # Останавливаем сервер для имитации ошибки соединения
        loginapp_fixture.stop()
        await loginapp_fixture.wait_until_stop()

        result = await client.importClientMessages()

        assert result.success is False
        assert result.result is None

    @pytest.mark.timeout(7)
    async def test_import_client_messages_timeout(
        self, loginapp_client_fixture: LoginappClient, loginapp_fixture: LoginappMock
    ) -> None:
        """Таймаут при ожидании ответа от сервера."""
        client = loginapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        result = await client.importClientMessages(wait_seconds=0.0)

        assert result.success is False
        assert result.result is None
        assert "timeout" in result.text.lower() or "Timeout" in result.text
