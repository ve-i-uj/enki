"""Интеграционные тесты на запущенный Loginapp (сообщения со стороны Client)."""

import random
import string

from enki.command.loginapp import HelloCommand, LoginappLoginCommand
from enki.kbeenum import ClientType, ComponentType, ServerError
from enki.kbetype.decoders.custom_decoders import SERVER_ERROR
from enki.msg.msg_client import TcpMsgClient
from enki.net.addr import Addr, Port

_LOGINAPP_ADDR = Addr.create_default_gw_addr(Port(20013))
_KBE_VERSION = "2.5.10"
_SCRIPT_VERSION = "0.1.0"


class TestHelloCommand:
    """Тесты команды hello."""

    async def test_loginapp_hello_success(self):
        """Сказать hello получить ответ."""
        client = TcpMsgClient(_LOGINAPP_ADDR, ComponentType.CLIENT)
        res = await client.start()
        assert res.success is True, "Loginapp is not reachable"

        cmd = HelloCommand(
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
        assert cmd_res.result.protocol_md5 == "1102EA4445FA7BC78DFA939A2161D781"
        assert cmd_res.result.entity_def_md5 == "ADB0AF58A3C2E7C576C9B3D1820FB606"

    async def test_loginapp_hello_invalid_kbe_version(self):
        """Ответ есть, но версия kBE указана неправильно."""
        client = TcpMsgClient(_LOGINAPP_ADDR, ComponentType.CLIENT)
        res = await client.start()
        assert res.success is True, "Loginapp is not reachable"

        cmd = HelloCommand(
            kbe_version="asdfasf",
            script_version=_SCRIPT_VERSION,
            encrypted_key=b"",
            started_client=client,
        )
        cmd_res = await cmd.execute()
        assert cmd_res.success is False, cmd_res.text

    async def test_loginapp_hello_invalid_scripts_version(self):
        """Не совпадает версия скриптов (assets'ов)."""
        client = TcpMsgClient(_LOGINAPP_ADDR, ComponentType.CLIENT)
        res = await client.start()
        assert res.success is True, "Loginapp is not reachable"

        cmd = HelloCommand(
            kbe_version=_KBE_VERSION,
            script_version="sdafassg",
            encrypted_key=b"",
            started_client=client,
        )
        cmd_res = await cmd.execute()
        assert cmd_res.success is False, cmd_res.text


class TestLoginCommand:
    """Тесты команды login."""

    async def test_loginapp_login(self):
        """Сказать login получить ответ (адрес Baseapp)."""
        client = TcpMsgClient(_LOGINAPP_ADDR, ComponentType.CLIENT)
        res = await client.start()
        assert res.success is True, "Loginapp is not reachable"

        account_name = "".join(
            random.choice(string.ascii_letters) for _ in range(10)
        )
        password = "".join(random.choice(string.ascii_letters) for _ in range(10))

        cmd = LoginappLoginCommand(
            ClientType.LINUX,
            client_data=b"",
            account_name=account_name,
            password=password,
            digest="sadfasf",
            force_login=False,
            started_client=client,
        )
        cmd_res = await cmd.execute()
        assert cmd_res.success is True, cmd_res.text
        assert cmd_res.result is not None

        assert cmd_res.result.ret_code == ServerError.SUCCESS

    async def test_loginapp_login_failed(self):
        """Получить ошибку от команды, если пришла неудача."""
        client = TcpMsgClient(_LOGINAPP_ADDR, ComponentType.CLIENT)
        res = await client.start()
        assert res.success is True, "Loginapp is not reachable"

        password = "".join(random.choice(string.ascii_letters) for _ in range(10))

        cmd = LoginappLoginCommand(
            ClientType.LINUX,
            client_data=b"",
            # Имя аккаунта не может быть пустой строкой
            account_name="",
            password=password,
            digest="sadfasf",
            force_login=False,
            started_client=client,
        )
        cmd_res = await cmd.execute()
        assert cmd_res.success is False, cmd_res.text
        assert cmd_res.result is not None

        assert cmd_res.result.ret_code == ServerError.NAME
