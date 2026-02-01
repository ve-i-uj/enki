"""Тесты на парсинг сообщений от компонента Interfaces."""

from enki import msgspec
from enki.msg.msg_serializer import MessageSerializer
from enki.msg_parser.interfaces_msg_parser import (
    LookAppMsgParser,
    OnAccountLoginMsgParser,
    OnAppActiveTickMsgParser,
    OnLookAppMsgParser,
    OnRegisterNewAppMsgParser,
)
from enki.msgspec import InterfacesMsgSpecByID


class TestInterfaces_onRegisterNewApp:
    """Тесты сообщения Interfaces::onRegisterNewApp."""

    msg_spec = msgspec.interfaces.onRegisterNewApp
    data = b"\x08\x00*\x00\xe8\x03\x00\x00root\x00\x01\x00\x00\x00\xa1\x0f\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xac\x12\x00\x06\x89\xfd\x00\x00\x00\x00\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(InterfacesMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = OnRegisterNewAppMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        pd = result.result
        assert pd.uid == 1000
        assert pd.username == "root"
        assert pd.componentType == 1
        assert pd.componentID == 4001
        assert pd.globalorderID == -1
        assert pd.grouporderID == -1
        assert pd.intaddr == 100668076
        assert pd.intport == 64905
        assert pd.extaddr == 0
        assert pd.extport == 0
        assert pd.extaddrEx == ""


class TestInterfaces_onAppActiveTick:
    """Тесты сообщения Interfaces::onAppActiveTick."""

    msg_spec = msgspec.interfaces.onAppActiveTick
    data = b"\xbd\x02\x01\x00\x00\x00\xa1\x0f\x00\x00\x00\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(InterfacesMsgSpecByID)
        msg, _data_tail = serializer.deserialize_only_data(
            memoryview(self.data), msgspec.interfaces.onAppActiveTick.id
        )
        assert msg is not None

        result = OnAppActiveTickMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        # Проверка нейминга, чтобы не было опечаток и т.п.
        assert result.msg_id == self.msg_spec.id
        assert (
            result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            result.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )
        assert result.msg_id == self.msg_spec.id


class TestInterfaces_onAccountLogin:
    """Тесты сообщения Interfaces::onAccountLogin."""

    msg_spec = msgspec.interfaces.onAccountLogin
    data = b'\n\x00"\x00)#\x00\x00\x00\x00\x00\x00mbLYLNYIDF\x00hKjiTCXJSp\x00\x00\x00\x00\x00'

    def test_onAccountLogin(self):
        serializer = MessageSerializer(InterfacesMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = OnAccountLoginMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        # Проверка нейминга, чтобы не было опечаток и т.п.
        assert result.msg_id == self.msg_spec.id
        assert (
            result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            result.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )
        assert result.msg_id == self.msg_spec.id

        pd = result.result
        assert pd.component_id == 9001
        assert pd.login == "mbLYLNYIDF"
        assert pd.password == "hKjiTCXJSp"
        assert pd.data == b""


class TestInterfaces_onLookApp:
    """Тесты сообщения Interfaces::onLookApp."""

    msg_spec = msgspec.interfaces.onLookApp
    data = b"\r\x00\x00\x00\xb9\x0b\x00\x00\x00\x00\x00\x00\x01"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(InterfacesMsgSpecByID)
        msg, data_tail = serializer.deserialize_only_data(
            self.data, self.msg_spec.id
        )
        assert msg is not None
        assert not data_tail

        result = OnLookAppMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        pd = result.result
        assert pd.componentType == 13
        assert pd.componentId == 3001
        assert pd.shutdownState == 1


class TestInterfaces_lookApp:
    """Тесты сообщения Interfaces::lookApp."""

    msg_spec = msgspec.interfaces.lookApp
    data = b"\x0c\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(InterfacesMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = LookAppMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        # Сообщение пустое
