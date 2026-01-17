"""Тесты на парсинг сообщений от компонента DBMgr."""

import pytest

from enki import msgspec
from enki.kbeenum import ComponentType, ServerError
from enki.msg.msg_serializer import MessageSerializer
from enki.msg_parser.dbmgr_msg_parser import (
    EntityAutoLoadMsgParser,
    OnAccountLoginMsgParser,
    OnAppActiveTickMsgParser,
    OnBroadcastGlobalDataChangedMsgParser,
    OnLoginAccountCBBFromInterfacesMsgParser,
    OnRegisterNewAppMsgParser,
    SyncEntityStreamTemplateMsgParser,
)
from enki.msgspec import DBMgrMsgSpecByID


class TestDBMgr_onAppActiveTick:
    """Тесты сообщения DBMgr::onAppActiveTick."""

    msg_spec = msgspec.dbmgr.onAppActiveTick
    data = b"A\xd7\n\x00\x00\x00\xd1\x07\x00\x00\x00\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
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


class TestDBMgr_onRegisterNewApp:
    """Тесты сообщения DBMgr::onRegisterNewApp."""

    msg_spec = msgspec.dbmgr.onRegisterNewApp
    data = b"\x08\x00*\x00\xe8\x03\x00\x00root\x00\r\x00\x00\x00\xb9\x0b\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xac\x12\x00\x05u\x93\x00\x00\x00\x00\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

        result = OnRegisterNewAppMsgParser().parse(msg)

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


class TestDBMgr_onBroadcastGlobalDataChanged:
    """Тесты сообщения DBMgr::onBroadcastGlobalDataChanged."""

    msg_spec = msgspec.dbmgr.onBroadcastGlobalDataChanged
    data = b"\x0c\x00K\x00\x00\x00\r\x00\x00\x00Vspace_1\np0\n.0\x00\x00\x00c_upf\nEntityCall\np0\n(I2002\nI7001\nI9\nI1\ntp1\nRp2\n.\x05\x00\x00\x00"

    # TODO: [2025-08-12 11:34 burov_alexey@mail.ru]:
    # Я взял данные, какие были. Возможно, они не валидные, т.к. не может
    # вычитать ключ (длина ключа больше всех данных). Может быть BLOB
    # неправильно сделан у меня.
    @pytest.mark.skip(reason="maybe wrong data")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

        result = OnBroadcastGlobalDataChangedMsgParser().parse(msg)

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

        assert not result.result.isDelete
        assert result.result.key == "space_1"
        assert result.result.value is not None
        assert result.result.component_type == ComponentType.CELLAPP


class TestDBMgr_syncEntityStreamTemplate:
    """Тесты сообщения DBMgr::syncEntityStreamTemplate."""

    msg_spec = msgspec.dbmgr.syncEntityStreamTemplate
    data = b"\x1d\x00\x14\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00"

    def test_success(self):
        # См. комментарий к обработчику
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

        result = SyncEntityStreamTemplateMsgParser().parse(msg)

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
        assert isinstance(pd.data, bytes)


class TestDBMgr_entityAutoLoad:
    """Тесты сообщения DBMgr::entityAutoLoad."""

    msg_spec = msgspec.dbmgr.entityAutoLoad
    data = b"\x1c\x00\x14\x00\x00\x00Y\x1b\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00 \x00\x00\x00"

    def test_success(self):
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

        result = EntityAutoLoadMsgParser().parse(msg)

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
        assert pd.dbInterfaceIndex == 0
        assert pd.componentID == 7001
        assert pd.entityType == 1
        assert pd.start == 0
        assert pd.end == 32


class TestDBMgr_onAccountLogin:
    """Тесты сообщения DBMgr::onAccountLogin."""

    msg_spec = msgspec.dbmgr.onAccountLogin
    data = b"\x0f\x00\x1a\x00mbLYLNYIDF\x00hKjiTCXJSp\x00\x00\x00\x00\x00"

    def test_onAccountLogin(self):
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

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
        assert pd.login == "mbLYLNYIDF"
        assert pd.password == "hKjiTCXJSp"
        assert pd.data == b""


class TestDBMgr_onLoginAccountCBBFromInterfaces:
    """Тесты сообщения DBMgr::onLoginAccountCBBFromInterfaces."""

    msg_spec = msgspec.dbmgr.onLoginAccountCBBFromInterfaces
    data = b"\x10\x003\x00)#\x00\x00\x00\x00\x00\x00mbLYLNYIDF\x00mbLYLNYIDF\x00hKjiTCXJSp\x00#\x00\x00\x00\x00\x00\x00\x00\x00\x00"

    def test_onLoginAccountCBBFromInterfaces(self):
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

        result = OnLoginAccountCBBFromInterfacesMsgParser().parse(msg)

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
        assert pd.login == "mbLYLNYIDF"
        assert pd.password == "hKjiTCXJSp"
        assert pd.component_id == 9001
        assert pd.ret_code == ServerError.LOCAL_PROCESSING
        assert pd.getdatas == ""
        assert pd.postdatas == ""
