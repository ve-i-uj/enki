"""Интеграционные тесты на запущенный Loginapp (сообщения со стороны Client)."""

import random
import string

from enki.command.loginapp import LoginappHelloCommand, LoginappLoginCommand
from enki.kbeenum import ClientType, ComponentType, ServerError
from enki.kbetype.pytypes.basic_data_types import KBEString
from enki.msg.msg_client import TcpMsgClient
from enki.net.addr import Addr, Port
from tests.itests.app_mocks.loginapp_mock import LoginappMock

_LOGINAPP_ADDR = Addr.create_default_gw_addr(Port(20013))
_KBE_VERSION = "2.5.10"
_SCRIPT_VERSION = "0.1.0"


class TestHelloCommand:
    """Тесты команды hello."""

    async def test_loginapp_hello_success(self, started_loginapp: LoginappMock):
        """Сказать hello получить ответ."""
        client = TcpMsgClient(started_loginapp.tcp_addr, ComponentType.CLIENT)
        res = await client.start()
        assert res.success is True, "Loginapp is not reachable"

        cmd = LoginappHelloCommand(
            kbe_version=_KBE_VERSION,
            script_version=_SCRIPT_VERSION,
            encrypted_key=b"",
            started_client=client,
        )
        cmd_res = await cmd.execute()
        assert cmd_res.success is True, cmd_res.text

        assert cmd_res.result is not None
        assert cmd_res.result.kbe_version == _KBE_VERSION
        assert cmd_res.result.assets_version == _SCRIPT_VERSION
        assert cmd_res.result.protocol_md5 == "6615F2367124A5E4B390207ACC4906B6"
        assert (
            cmd_res.result.entity_def_md5 == "06E15F102B481ACF8CA19E2F410D1B64"
        )

    async def test_loginapp_hello_invalid_kbe_version(
        self, started_loginapp: LoginappMock
    ):
        """Ответ есть, но версия kBE указана неправильно."""
        client = TcpMsgClient(started_loginapp.tcp_addr, ComponentType.CLIENT)
        res = await client.start()
        assert res.success is True, "Loginapp is not reachable"

        # Отправляем с клиента неправильную версию движка
        test_kbe_version = KBEString("1.2.3")
        assert test_kbe_version != started_loginapp.kbe_version

        cmd = LoginappHelloCommand(
            kbe_version=test_kbe_version,
            script_version=_SCRIPT_VERSION,
            encrypted_key=b"",
            started_client=client,
        )
        cmd_res = await cmd.execute()
        assert cmd_res.success is False, cmd_res.text

    async def test_loginapp_hello_invalid_scripts_version(
        self, started_loginapp: LoginappMock
    ):
        """Не совпадает версия скриптов (assets'ов)."""
        client = TcpMsgClient(started_loginapp.tcp_addr, ComponentType.CLIENT)
        res = await client.start()
        assert res.success is True, "Loginapp is not reachable"

        script_version = "0.0.0"
        assert started_loginapp.assets_version != script_version

        cmd = LoginappHelloCommand(
            kbe_version=_KBE_VERSION,
            script_version="sdafassg",
            encrypted_key=b"",
            started_client=client,
        )
        cmd_res = await cmd.execute()
        assert cmd_res.success is False, cmd_res.text


class TestLoginCommand:
    """Тесты команды login."""

    async def test_loginapp_login(self, started_loginapp: LoginappMock):
        """Сказать login получить ответ (адрес Baseapp)."""
        client = TcpMsgClient(started_loginapp.tcp_addr, ComponentType.CLIENT)
        res = await client.start()
        assert res.success is True, "Loginapp is not reachable"

        account_name = "".join(
            random.choice(string.ascii_letters) for _ in range(10)
        )
        password = "".join(
            random.choice(string.ascii_letters) for _ in range(10)
        )

        cmd = LoginappLoginCommand(
            ClientType.LINUX,
            client_data=b"",
            login_name=account_name,
            password=password,
            digest="06E15F102B481ACF8CA19E2F410D1B64",
            force_login=False,
            started_client=client,
        )
        cmd_res = await cmd.execute()
        assert cmd_res.success is True, cmd_res.text
        assert cmd_res.result is not None

        assert cmd_res.result.ret_code == ServerError.SUCCESS

    async def test_loginapp_login_failed(self, started_loginapp: LoginappMock):
        """Получить ошибку от команды, если пришла неудача."""
        client = TcpMsgClient(started_loginapp.tcp_addr, ComponentType.CLIENT)
        res = await client.start()
        assert res.success is True, "Loginapp is not reachable"

        password = "".join(
            random.choice(string.ascii_letters) for _ in range(10)
        )

        cmd = LoginappLoginCommand(
            ClientType.LINUX,
            client_data=b"",
            # Имя аккаунта не может быть пустой строкой
            login_name="",
            password=password,
            digest="sadfasf",
            force_login=False,
            started_client=client,
        )
        cmd_res = await cmd.execute()
        assert cmd_res.success is False, cmd_res.text
        assert cmd_res.result is not None

        assert cmd_res.result.ret_code == ServerError.NAME
