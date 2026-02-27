"""Тесты на парсинг сообщений от компонента Interfaces."""

import pytest

from enki import msgspec
from enki.msg.msg_serializer import MessageSerializer
from enki.msg_parser.interfaces_msg_parser import (
    ChargeMsgParser,
    EraseClientReqMsgParser,
    LookAppMsgParser,
    OnAccountLoginMsgParser,
    OnAppActiveTickMsgParser,
    OnExecuteRawDatabaseCommandCBMsgParser,
    OnLookAppMsgParser,
    OnRegisterNewAppMsgParser,
    QueryWatcherMsgParser,
    ReqCreateAccountMsgParser,
    ReqKillServerMsgParser,
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
        msg, data_tail = serializer.deserialize_only_data(self.data, self.msg_spec.id)
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


class TestInterfaces_reqCreateAccount:
    """Тесты сообщения Interfaces::reqCreateAccount."""

    msg_spec = msgspec.interfaces.reqCreateAccount
    data = b"\t\x00#\x00)#\x00\x00\x00\x00\x00\x00NBkMtOWSbD\x00rfrbeb843O\x00\x01\x00\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(InterfacesMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = ReqCreateAccountMsgParser().parse(msg)

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

        pd = result.result
        assert pd.component_id == 9001
        assert pd.registerName == "NBkMtOWSbD"
        assert pd.password == "rfrbeb843O"
        assert pd.accountType == 1
        assert pd.datas == b""


class TestInterfaces_charge:
    """Тесты сообщения Interfaces::charge."""

    msg_spec = msgspec.interfaces.charge
    data = b"\x0b\x00$\x00order123\x00\xe8\x03\x00\x00testuser\x00\xe8\x03\x00\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(InterfacesMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = ChargeMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        # Проверка нейминга
        assert result.msg_id == self.msg_spec.id
        assert (
            result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            result.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )

        pd = result.result
        assert pd.orderID == "order123"
        assert pd.dbid == 1000
        assert pd.accountName == "testuser"
        assert pd.gold == 1000


class TestInterfaces_eraseClientReq:
    """Тесты сообщения Interfaces::eraseClientReq."""

    msg_spec = msgspec.interfaces.eraseClientReq
    data = b"\x0e\x00\x14\x00\xe8\x03\x00\x00testuser\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(InterfacesMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = EraseClientReqMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        # Проверка нейминга
        assert result.msg_id == self.msg_spec.id
        assert (
            result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            result.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )

        pd = result.result
        assert pd.dbid == 1000
        assert pd.accountName == "testuser"


class TestInterfaces_reqKillServer:
    """Тесты сообщения Interfaces::reqKillServer."""

    msg_spec = msgspec.interfaces.reqKillServer
    data = b"\x10\x00\x18\x00Baseapp\x00\xe8\x03\x00\x00\x00\x00\x00\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(InterfacesMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = ReqKillServerMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        # Проверка нейминга
        assert result.msg_id == self.msg_spec.id
        assert (
            result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            result.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )

        pd = result.result
        assert pd.componentType == "Baseapp"
        assert pd.componentID == 1000


class TestInterfaces_onExecuteRawDatabaseCommandCB:
    """Тесты сообщения Interfaces::onExecuteRawDatabaseCommandCB."""

    msg_spec = msgspec.interfaces.onExecuteRawDatabaseCommandCB
    data = b"\x11\x00\x0e\x00\x01\x00\x00\x00test result\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(InterfacesMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = OnExecuteRawDatabaseCommandCBMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        # Проверка нейминга
        assert result.msg_id == self.msg_spec.id
        assert (
            result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            result.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )

        pd = result.result
        assert pd.id == 1
        assert pd.result == b"test result"


class TestInterfaces_queryWatcher:
    """Тесты сообщения Interfaces::queryWatcher."""

    msg_spec = msgspec.interfaces.queryWatcher
    data = b"\xff\xa0\x0c\x00stats/cpuUsage\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(InterfacesMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = QueryWatcherMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        # Проверка нейминга
        assert result.msg_id == self.msg_spec.id
        assert (
            result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            result.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )

        pd = result.result
        assert pd.path == "stats/cpuUsage"
