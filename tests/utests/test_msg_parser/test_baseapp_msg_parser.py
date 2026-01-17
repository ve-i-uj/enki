"""Тесты на парсинг сообщений от компонента Baseapp."""

from enki import msgspec
from enki.kbeenum import ClientType
from enki.msg.msg_serializer import MessageSerializer
from enki.msg_parser.baseapp_msg_parser import (
    OnAppActiveTickMsgParser,
    OnBroadcastGlobalDataChangedMsgParser,
    OnDbmgrInitCompletedMsgParser,
    OnEntityAutoLoadCBFromDBMgrMsgParser,
    OnEntityGetCellMsgParser,
    OnGetEntityAppFromDbmgrMsgParser,
    OnRegisterNewAppMsgParser,
    RegisterPendingLoginMsgParser,
)
from enki.msgspec import BaseappMsgSpecByID
from enki.net.addr import Addr, Port


class TestBaseapp_onRegisterNewApp:
    """Тесты сообщения Baseapp::onRegisterNewApp."""

    msg_spec = msgspec.baseapp.onRegisterNewApp
    data = b"\n\x00*\x00\xe8\x03\x00\x00root\x00\x05\x00\x00\x00Y\x1b\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\xac\x12\x00\n\xe5\x1d\x00\x00\x00\x00\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
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


class TestBaseapp_onAppActiveTick:
    """Тесты сообщения Baseapp::onAppActiveTick."""

    msg_spec = msgspec.baseapp.onAppActiveTick
    data = b"<\xd7\x01\x00\x00\x00\xa1\x0f\x00\x00\x00\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
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


class TestDBMgr_OnDbmgrInitCompleted:
    msg_spec = msgspec.baseapp.onDbmgrInitCompleted
    data = b"\r\x005\x00k\x11\x00\x00\xd1\x07\x00\x00\xa1\x0f\x00\x00\x04\x00\x00\x00\x01\x00\x00\x0006E15F102B481ACF8CA19E2F410D1B64\x00"

    def test_onDbmgrInitCompleted(self):
        serializer = MessageSerializer(BaseappMsgSpecByID)
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

        assert pd.startID == 2001
        assert pd.endID == 4001
        assert pd.startGlobalOrder == 4
        assert pd.startGroupOrder == 1
        assert pd.digest == "06E15F102B481ACF8CA19E2F410D1B64"


class TestDBMgr_OnEntityAutoLoadCBFromDBMgr:
    msg_spec = msgspec.baseapp.onEntityAutoLoadCBFromDBMgr
    data = b"\x17\x00\x08\x00\x00\x00\x00\x00\x00\x00\x01\x00"

    def test_onEntityAutoLoadCBFromDBMgr(self):
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

        res = OnEntityAutoLoadCBFromDBMgrMsgParser().parse(msg)

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

        assert pd.dbInterfaceIndex == 0
        assert pd.size == 0
        assert pd.entityType == 1
        assert pd.dbids == []


class TestDBMgr_OnBroadcastGlobalDataChanged:
    msg_spec = msgspec.baseapp.onBroadcastGlobalDataChanged
    data = b"\x0e\x00F\x00\x00\r\x00\x00\x00Vspace_1\np0\n.0\x00\x00\x00c_upf\nEntityCall\np0\n(I2002\nI7001\nI9\nI1\ntp1\nRp2\n."

    def test_onBroadcastGlobalDataChanged(self):
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

        res = OnBroadcastGlobalDataChangedMsgParser().parse(msg)

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
        assert not pd.isDelete
        assert pd.key == "space_1"
        assert pd.value is not None


class TestDBMgr_OnEntityGetCell:
    msg_spec = msgspec.baseapp.onEntityGetCell
    data = (
        b"\x14\x00\xd2\x07\x00\x00Y\x1b\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00"
    )

    def test_onRegisterNewApp(self):
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

        res = OnEntityGetCellMsgParser().parse(msg)

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
        assert pd.componentID == 7001
        assert pd.entity_id == 2002
        assert pd.spaceID == 1


class Test_onGetEntityAppFromDbmgr:
    msg_spec = msgspec.baseapp.onGetEntityAppFromDbmgr
    data = b"\x0b\x00*\x00\xe8\x03\x00\x00root\x00\x05\x00\x00\x00A\x1f\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x01\x00\x00\x00\xac\x17\x00\n\x9c\x17\x00\x00\x00\x00\x00\x00\x00"

    def test_onRegisterNewApp(self):
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

        res = OnGetEntityAppFromDbmgrMsgParser().parse(msg)

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

        assert res.msg_id == msgspec.baseapp.onGetEntityAppFromDbmgr.id
        pd = res.result
        assert pd.componentID == 8001
        assert pd.internal_address == Addr(
            ip_addr="172.23.0.10", port=Port(39959)
        )
        assert pd.intport == 6044


class Test_registerPendingLogin:
    msg_spec = msgspec.baseapp.registerPendingLogin
    data = b"\x16\x00C\x00mbLYLNYIDF\x00mbLYLNYIDF\x00hKjiTCXJSp\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00"

    def test_onRegisterNewApp(self):
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

        res = RegisterPendingLoginMsgParser().parse(msg)

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
        assert res.msg_id == msgspec.baseapp.registerPendingLogin.id

        pd = res.result

        assert pd.login == "mbLYLNYIDF"
        assert pd.account_name == "mbLYLNYIDF"
        assert pd.password == "hKjiTCXJSp"
        assert pd.needCheckPassword == 1
        assert pd.eid == 0
        assert pd.entityDBID == 1
        assert pd.flags == 0
        assert pd.deadline == 0
        assert pd.client_type == ClientType.LINUX
        assert pd.forceInternalLogin == 0
        assert pd.datas == ""
