"""Тесты клиента для серверного компонента KBEngine 'Baseapp'."""

import asyncio
import random
import string
from datetime import datetime

import pytest

from enki.apps.clientapp.clients.baseapp_client import (
    BaseappClient,
    BaseappIsNotStartedError,
    BaseappNoConnectionError,
    BaseappNoResponseError,
    BaseappNotLoggedInError,
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


class TestBaseappClientHello:
    @pytest.mark.timeout(7)
    async def test_hello_success(
        self, baseapp_client_fixture: BaseappClient, baseapp_fixture: BaseappMock
    ) -> None:
        """Успешная проверка версий."""
        client = baseapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        result = await client.hello(
            kbe_version=baseapp_fixture.kbe_version,
            assets_version=baseapp_fixture.assets_version,
            encrypted_key=b"test_encrypted_key",
        )

        assert result.success is True
        assert result.result.flag.value == "OK"
        assert result.result.kbe_version == baseapp_fixture.kbe_version
        assert result.result.encrypted_key == b"test_encrypted_key"

    @pytest.mark.timeout(7)
    async def test_hello_kbe_mismatch(
        self, baseapp_client_fixture: BaseappClient, baseapp_fixture: BaseappMock
    ) -> None:
        """Несовпадение версии KBEngine."""
        client = baseapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        wrong_version = "0.0.1"
        assert wrong_version != baseapp_fixture.kbe_version
        result = await client.hello(
            kbe_version=wrong_version,
            assets_version=baseapp_fixture.assets_version,
            encrypted_key=b"",
        )

        assert result.success is False
        assert result.result.flag.value == "KBE_VERSION_MISMATCH"
        assert result.result.kbe_version is not None
        assert wrong_version in result.text

    @pytest.mark.timeout(7)
    async def test_hello_assets_mismatch(
        self, baseapp_client_fixture: BaseappClient, baseapp_fixture: BaseappMock
    ) -> None:
        """Несовпадение версии ассетов."""
        client = baseapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        wrong_version = "0.0.1"
        assert wrong_version != baseapp_fixture.assets_version
        result = await client.hello(
            kbe_version=baseapp_fixture.kbe_version,
            assets_version=wrong_version,
            encrypted_key=b"",
        )

        assert result.success is False
        assert result.result.flag.value == "ASSETS_VERSION_MISMATCH"
        assert wrong_version in result.text

    @pytest.mark.timeout(7)
    async def test_hello_client_not_started(
        self, baseapp_client_fixture: BaseappClient, baseapp_fixture: BaseappMock
    ) -> None:
        """check_version без start() кидает BaseappConnectionError."""
        client = baseapp_client_fixture

        with pytest.raises(BaseappIsNotStartedError):
            _ = await client.hello(
                kbe_version=baseapp_fixture.kbe_version,
                assets_version=baseapp_fixture.assets_version,
                encrypted_key=b"",
            )

    @pytest.mark.timeout(7)
    async def test_hello_timeout(
        self, baseapp_client_fixture: BaseappClient, baseapp_fixture: BaseappMock
    ) -> None:
        """Таймаут при ожидании ответа check_version."""
        client = baseapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        with pytest.raises(BaseappNoResponseError) as exc_info:
            await client.hello(
                kbe_version=baseapp_fixture.kbe_version,
                assets_version=baseapp_fixture.assets_version,
                encrypted_key=b"",
                wait_seconds=0,
            )

        assert "no response" in str(exc_info.value).lower()


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


class TestBaseappClientReqAccountBindEmail:
    """Тесты BaseappClient.reqAccountBindEmail."""

    @pytest.mark.timeout(7)
    async def test_bind_main_without_login(
        self, baseapp_client_fixture: BaseappClient, baseapp_fixture: BaseappMock
    ) -> None:
        """Не успешный запрос привязки к email, т.к. не было логина."""
        client = baseapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        with pytest.raises(BaseappNotLoggedInError):
            # На сервере в логах будет
            # Baseapp::reqAccountBindEmail: can't found entity:0.
            _result = await client.reqAccountBindEmail(
                entity_id=0,
                password=baseapp_fixture.password,
                email="user@example.com",
                wait_seconds=2 * SECOND,
            )

    @pytest.mark.timeout(7)
    async def test_bind_main_client_success(
        self,
        loginapp_client_fixture: LoginappClient,
        loginapp_fixture: LoginappMock,
        baseapp_client_fixture: BaseappClient,
        baseapp_fixture: BaseappMock,
    ) -> None:
        """Успешный запрос привязки email."""
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

        assert baseapp_client.account_entity_id == baseapp_client.NO_ENTITY_ID

        result = await baseapp_client.loginBaseapp(
            account_name=baseapp_fixture.account_name,
            password=baseapp_fixture.password,
        )
        assert result.success is True
        assert baseapp_client.account_entity_id != baseapp_client.NO_ENTITY_ID

        result = await baseapp_client.reqAccountBindEmail(
            entity_id=baseapp_client.account_entity_id,
            password=baseapp_fixture.password,
            email="user@example.com",
        )

        assert result.success is True
        assert result.result is not None
        assert result.result.ret_code == ServerError.SUCCESS


class TestBaseappClientReqAccountNewPassword:
    """Тесты BaseappClient.reqAccountNewPassword."""

    @pytest.mark.timeout(7)
    async def test_req_account_new_password_without_login(
        self, baseapp_client_fixture: BaseappClient, baseapp_fixture: BaseappMock
    ) -> None:
        """Неуспешный запрос смены пароля, т.к. не было логина.

        На сервере в логах будет:
        Baseapp::reqAccountNewPassword: can't found entity:0.

        """
        client = baseapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        with pytest.raises(BaseappNotLoggedInError):
            _result = await client.reqAccountNewPassword(
                entity_id=0,
                old_password=baseapp_fixture.password,
                new_password="new_password",  # noqa: S106
                wait_seconds=2 * SECOND,
            )

    @pytest.mark.timeout(7)
    async def test_req_account_new_password_client_success(
        self,
        loginapp_client_fixture: LoginappClient,
        loginapp_fixture: LoginappMock,
        baseapp_client_fixture: BaseappClient,
        baseapp_fixture: BaseappMock,
    ) -> None:
        """Успешный запрос смены пароля."""
        baseapp_client = baseapp_client_fixture
        loginapp_client = loginapp_client_fixture

        res = await loginapp_client.start()
        assert res.success

        account_name = "".join(
            random.choices(string.ascii_letters + string.digits, k=10)
        )
        password = "".join(random.choices(string.ascii_letters + string.digits, k=10))
        entitydefs_hash = loginapp_fixture.entity_def_md5
        force_login = True

        loginapp_fixture.account_name = account_name
        loginapp_fixture.password = password

        login_res = await loginapp_client.login(
            client_type=ClientType.MOBILE,
            client_data=b"test_client_data",
            account_name=account_name,
            password=password,
            entitydefs_hash=entitydefs_hash,
            force_login=force_login,
        )
        assert login_res.success is True
        assert login_res.result.ret_code == ServerError.SUCCESS

        start_result = await baseapp_client.start()
        assert start_result.success

        assert baseapp_client.account_entity_id == baseapp_client.NO_ENTITY_ID

        loginbaseapp_res = await baseapp_client.loginBaseapp(
            account_name=account_name,
            password=password,
        )
        assert loginbaseapp_res.success is True
        assert baseapp_client.account_entity_id != baseapp_client.NO_ENTITY_ID

        result = await baseapp_client.reqAccountNewPassword(
            entity_id=baseapp_client.account_entity_id,
            old_password=password,
            new_password="new_password_123",
        )

        assert result.success is True
        assert result.result is not None
        assert result.result.ret_code == ServerError.SUCCESS

    @pytest.mark.timeout(7)
    async def test_req_account_new_password_client_not_started(
        self, baseapp_client_fixture: BaseappClient, baseapp_fixture: BaseappMock
    ) -> None:
        """Запрос смены пароля без предварительного start()."""
        client = baseapp_client_fixture

        with pytest.raises(BaseappNoConnectionError):
            _ = await client.reqAccountNewPassword(
                entity_id=0,
                old_password=baseapp_fixture.password,
                new_password="new_password_123",
            )

    @pytest.mark.timeout(7)
    async def test_req_account_new_password_after_client_stop(
        self, baseapp_client_fixture: BaseappClient, baseapp_fixture: BaseappMock
    ) -> None:
        """Запрос смены пароля после stop() кидает BaseappIsNotStartedError."""
        client = baseapp_client_fixture

        start_result = await client.start()
        assert start_result.success

        client.stop()
        await asyncio.sleep(0.1)

        with pytest.raises(BaseappNoConnectionError):
            _ = await client.reqAccountNewPassword(
                entity_id=0,
                old_password=baseapp_fixture.password,
                new_password="new_password_123",
            )


class TestBaseappClientLogoutBaseapp:
    """Тесты BaseappClient.logoutBaseapp."""

    @pytest.mark.timeout(7)
    async def test_logout_success(
        self,
        loginapp_client_fixture: LoginappClient,
        loginapp_fixture: LoginappMock,
        baseapp_client_fixture: BaseappClient,
    ) -> None:
        """Успешный logout — сообщение отправлено, ответа не ждём."""
        baseapp_client = baseapp_client_fixture
        loginapp_client = loginapp_client_fixture

        res = await loginapp_client.start()
        assert res.success

        account_name = "".join(
            random.choices(string.ascii_letters + string.digits, k=10)
        )
        password = "".join(random.choices(string.ascii_letters + string.digits, k=10))
        entitydefs_hash = loginapp_fixture.entity_def_md5
        force_login = False

        loginapp_fixture.account_name = account_name
        loginapp_fixture.password = password

        login_res = await loginapp_client.login(
            client_type=ClientType.MOBILE,
            client_data=b"test_client_data",
            account_name=account_name,
            password=password,
            entitydefs_hash=entitydefs_hash,
            force_login=force_login,
        )
        assert login_res.success is True

        start_result = await baseapp_client.start()
        assert start_result.success

        assert baseapp_client.account_entity_id == baseapp_client.NO_ENTITY_ID
        loginbaseapp_res = await baseapp_client.loginBaseapp(
            account_name=account_name,
            password=password,
        )
        assert loginbaseapp_res.success is True
        assert baseapp_client.account_entity_id != baseapp_client.NO_ENTITY_ID

        result = await baseapp_client.logoutBaseapp(
            baseapp_client.rnd_uuid,
            baseapp_client.account_entity_id,
        )

        assert result.success is True
        assert result.result is not None
        assert result.result.sent is True

        # Соединение закрывается живым сервером
        await asyncio.sleep(2)
        await baseapp_client.wait_until_stop()
        assert not baseapp_client.is_started

    @pytest.mark.timeout(7)
    async def test_logout_no_login(
        self,
        loginapp_client_fixture: LoginappClient,
        loginapp_fixture: LoginappMock,
        baseapp_client_fixture: BaseappClient,
        baseapp_fixture: BaseappMock,
    ) -> None:
        """Logout без предварительного логина."""
        baseapp_client = baseapp_client_fixture
        loginapp_client = loginapp_client_fixture

        res = await loginapp_client.start()
        assert res.success

        account_name = "".join(
            random.choices(string.ascii_letters + string.digits, k=10)
        )
        password = "".join(random.choices(string.ascii_letters + string.digits, k=10))

        loginapp_fixture.account_name = account_name
        loginapp_fixture.password = password

        start_result = await baseapp_client.start()
        assert start_result.success

        assert baseapp_client.rnd_uuid == baseapp_client.NO_RND_UUID
        assert baseapp_client.account_entity_id == baseapp_client.NO_ENTITY_ID
        result = await baseapp_client.logoutBaseapp(
            baseapp_client.rnd_uuid,
            baseapp_client.account_entity_id,
        )

        assert result.success is True
        assert result.result is not None
        assert result.result.sent is True

        # Это несуществующие id и uuid, поэтому сервер ничего не делает
        # на сообщение и не закрывает соединение.
        await asyncio.sleep(3)
        assert baseapp_client.is_started

    @pytest.mark.timeout(7)
    async def test_logout_client_not_started(
        self,
        baseapp_client_fixture: BaseappClient,
    ) -> None:
        """Logout без start() кидает BaseappIsNotStartedError."""
        baseapp_client = baseapp_client_fixture

        with pytest.raises(BaseappIsNotStartedError):
            _result = await baseapp_client.logoutBaseapp(
                baseapp_client.rnd_uuid,
                baseapp_client.account_entity_id,
            )

    @pytest.mark.timeout(7)
    async def test_logout_after_client_stop(
        self, baseapp_client_fixture: BaseappClient, baseapp_fixture: BaseappMock
    ) -> None:
        """Logout после stop() кидает BaseappIsNotStartedError."""
        baseapp_client = baseapp_client_fixture

        start_result = await baseapp_client.start()
        assert start_result.success

        baseapp_client.stop()
        await asyncio.sleep(0.1)

        with pytest.raises(BaseappIsNotStartedError):
            _result = await baseapp_client.logoutBaseapp(
                baseapp_client.rnd_uuid,
                baseapp_client.account_entity_id,
            )
