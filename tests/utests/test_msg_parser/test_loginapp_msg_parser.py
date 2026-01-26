"""Тесты для парсеров собщений компонента Loginapp."""

from enki import msgspec
from enki.kbeenum import ClientType, ComponentState, ComponentType, ServerError
from enki.msg.msg_serializer import MessageSerializer
from enki.msg_parser.loginapp_msg_parser import (
    HelloMsgParser,
    LoginMsgParser,
    OnAppActiveTickMsgParser,
    OnBaseappInitProgressMsgParser,
    OnDbmgrInitCompletedMsgParser,
    OnLoginAccountQueryBaseappAddrFromBaseappmgrMsgParser,
    OnLoginAccountQueryResultFromDbmgrMsgParser,
    OnLookAppMsgParser,
)
from enki.msgspec import LoginappMsgSpecByID
from enki.net.addr import Addr, Port


class TestOnDbmgrInitCompletedTestCase:
    data = b"\x0e\x00)\x00\x05\x00\x00\x00\x01\x00\x00\x0006E15F102B481ACF8CA19E2F410D1B64\x00"
    msg_spec = msgspec.loginapp.onDbmgrInitCompleted

    def test_onDbmgrInitCompleted(self):
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

        res = OnDbmgrInitCompletedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга, чтобы не было опечаток и т.п.
        assert res.msg_id == self.msg_spec.id
        assert (
            res.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            res.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )
        assert res.msg_id == self.msg_spec.id

        pd = res.result

        assert pd.startID == 1
        assert pd.endID == 826619440
        assert pd.startGlobalOrder == 808535605
        assert pd.startGroupOrder == 942948914
        assert pd.digest == "1ACF8CA19E2F410D1B64"


class TestOnBaseappInitProgressTestCase:
    data = b"\x18\x00\x00\x00\xc8B"
    msg_spec = msgspec.loginapp.onBaseappInitProgress

    def test_OnBaseappInitProgressHandler(self):
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

        res = OnBaseappInitProgressMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга, чтобы не было опечаток и т.п.
        assert res.msg_id == self.msg_spec.id
        assert (
            res.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            res.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )
        assert res.msg_id == self.msg_spec.id

        pd = res.result

        assert pd.progress == 100.0


class TestOnAppActiveTick:
    data = b"B\xd7\n\x00\x00\x00\xd1\x07\x00\x00\x00\x00\x00\x00"
    msg_spec = msgspec.loginapp.onAppActiveTick

    def test_OnAppActiveTickHandler(self):
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

        res = OnAppActiveTickMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга, чтобы не было опечаток и т.п.
        assert res.msg_id == self.msg_spec.id
        assert (
            res.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            res.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )
        assert res.msg_id == self.msg_spec.id

        pd = res.result

        assert pd.componentType == 10
        assert pd.componentID == 2001


class TestLoginappHello:
    """Тест парсинга сообщения Loginapp::hello."""

    data = b"\x04\x00\x11\x002.5.10\x000.1.0\x00\x00\x00\x00\x00"
    msg_spec = msgspec.loginapp.hello

    def test_hello(self):
        """Тест парсинга сообщения Loginapp::hello."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

        res = HelloMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга, чтобы не было опечаток и т.п.
        assert res.msg_id == self.msg_spec.id
        assert (
            res.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            res.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )
        assert res.msg_id == self.msg_spec.id

        pd = res.result

        assert pd.kbe_version == "2.5.10"
        assert pd.script_version == "0.1.0"
        assert pd.encrypted_key == b""


class TestLoginappLogin:
    """Тест парсинга сообщения Loginapp::login."""

    data = b"\x03\x00!\x00\x00\x00\x00\x00\x00ACCOUNT_NAME\x00PASSWORD\x00False\x00"
    msg_spec = msgspec.loginapp.login

    def test_login(self):
        """Тест парсинга сообщения Loginapp::login."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

        res = LoginMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга, чтобы не было опечаток и т.п.
        assert res.msg_id == self.msg_spec.id
        assert (
            res.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            res.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )
        assert res.msg_id == self.msg_spec.id

        pd = res.result

        assert pd.client_type == ClientType.UNKNOWN
        assert pd.clientData == b""
        assert pd.accountName == "ACCOUNT_NAME"
        assert pd.password == "PASSWORD"
        assert pd.force_login is False


class Test_OnLoginAccountQueryResultFromDbmgr:
    """Тест парсинга сообщения Loginapp::onLoginAccountQueryResultFromDbmgr."""

    data = b"\x0f\x00H\x00\x00\x00mbLYLNYIDF\x00mbLYLNYIDF\x00hKjiTCXJSp\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    msg_spec = msgspec.loginapp.onLoginAccountQueryResultFromDbmgr

    def test_login(self):
        """Тест парсинга сообщения Loginapp::login."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

        res = OnLoginAccountQueryResultFromDbmgrMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга, чтобы не было опечаток и т.п.
        assert res.msg_id == self.msg_spec.id
        assert (
            res.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            res.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )
        assert res.msg_id == self.msg_spec.id

        pd = res.result

        assert pd.ret_code == ServerError.SUCCESS
        assert pd.login == "mbLYLNYIDF"
        assert pd.account_name == "mbLYLNYIDF"
        assert pd.password == "hKjiTCXJSp"
        assert pd.needCheckPassword == 1
        assert pd.componentID == 0
        assert pd.entitiy_id == 0
        assert pd.db_id == 1
        assert pd.flags == 0
        assert pd.deadline == 0
        assert pd.data == ""


class TestLoginappOnLoginAccountQueryBaseappAddrFromBaseappmgr:
    msg_spec = msgspec.loginapp.onLoginAccountQueryBaseappAddrFromBaseappmgr
    data = b'\x10\x00"\x00mbLYLNYIDF\x00mbLYLNYIDF\x000.0.0.0\x00N/N%'

    def test_onLoginAccountQueryBaseappAddrFromBaseappmgr(self):
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnLoginAccountQueryBaseappAddrFromBaseappmgrMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга, чтобы не было опечаток и т.п.
        assert res.msg_id == self.msg_spec.id
        assert (
            res.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            res.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )
        assert res.msg_id == self.msg_spec.id

        assert res.msg_id == self.msg_spec.id

        pd = res.result

        assert pd.loginName == "mbLYLNYIDF"
        assert pd.accountName == "mbLYLNYIDF"
        assert pd.external_baseapp_tcp_address == Addr(
            ip_addr="0.0.0.0", port=Port(20015)
        )
        assert pd.external_baseapp_udp_address == Addr(
            ip_addr="0.0.0.0", port=Port(20005)
        )


class TestOnLookApp:
    msg_spec = msgspec.loginapp.onLookApp
    data = b"\x02\x00\x00\x00)#\x00\x00\x00\x00\x00\x00\x01"

    def test_onLookApp(self):
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize_only_data(
            memoryview(self.data), msg_id=msgspec.loginapp.onLookApp.id
        )
        assert msg is not None

        res = OnLookAppMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга, чтобы не было опечаток и т.п.
        assert res.msg_id == self.msg_spec.id
        assert (
            res.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            res.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )
        assert res.msg_id == self.msg_spec.id

        assert res.msg_id == self.msg_spec.id

        pd = res.result

        assert pd.componentId == 9001
        assert pd.component_type == ComponentType.LOGINAPP
        assert pd.component_state == ComponentState.RUN
