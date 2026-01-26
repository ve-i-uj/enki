"""Тесты на парсинг сообщений от компонента BaseappMgr."""

from enki import msgspec
from enki.kbeenum import ClientType
from enki.msg.msg_serializer import MessageSerializer
from enki.msg_parser.baseappmgr_msg_parser import (
    ForwardMessageMsgParser,
    LookAppMsgParser,
    OnAppActiveTickMsgParser,
    OnBaseappInitProgressMsgParser,
    OnLookAppMsgParser,
    OnPendingAccountGetBaseappAddrMsgParser,
    OnRegisterNewAppMsgParser,
    OnReqAccountBindEmailCBFromLoginappMsgParser,
    QueryAppsLoadsMsgParser,
    QueryLoadMsgParser,
    QueryWatcherMsgParser,
    RegisterPendingAccountToBaseappAddrMsgParser,
    RegisterPendingAccountToBaseappMsgParser,
    ReqAccountBindEmailAllocCallbackLoginappMsgParser,
    ReqCloseServerMsgParser,
    ReqCreateEntityAnywhereFromDBIDMsgParser,
    ReqCreateEntityAnywhereFromDBIDQueryBestBaseappIDMsgParser,
    ReqCreateEntityAnywhereMsgParser,
    ReqCreateEntityRemotelyFromDBIDMsgParser,
    ReqCreateEntityRemotelyMsgParser,
    ReqKillServerMsgParser,
    StartProfileMsgParser,
    UpdateBaseappMsgParser,
)
from enki.msgspec import BaseappMgrMsgSpecByID
from enki.net.addr import Addr, Port


class TestBaseappMgr_onAppActiveTick:
    """Тесты сообщения BaseappMgr::onAppActiveTick."""

    msg_spec = msgspec.baseappmgr.onAppActiveTick
    data = b"A\xd7\n\x00\x00\x00\xd1\x07\x00\x00\x00\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize_only_data(
            memoryview(self.data), self.msg_spec.id
        )
        assert msg is not None
        assert not data_tail

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


class TestBaseappMgr_onRegisterNewApp:
    """Тесты сообщения BaseappMgr::onRegisterNewApp."""

    msg_spec = msgspec.baseappmgr.onRegisterNewApp
    data = b"\x08\x00*\x00\xe8\x03\x00\x00root\x00\x04\x00\x00\x00q\x17\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xac\x12\x00\x08\xb6\x17\x00\x00\x00\x00\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

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


class Test_onGetEntityAppFromDbmgr:
    msg_spec = msgspec.baseappmgr.onPendingAccountGetBaseappAddr
    data = b'\x12\x00"\x00mbLYLNYIDF\x00mbLYLNYIDF\x000.0.0.0\x00N/N%'

    def test_onPendingAccountGetBaseappAddr(self):
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnPendingAccountGetBaseappAddrMsgParser().parse(msg)

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

        assert (
            res.msg_id == msgspec.baseappmgr.onPendingAccountGetBaseappAddr.id
        )

        pd = res.result

        assert pd.loginName == "mbLYLNYIDF"
        assert pd.accountName == "mbLYLNYIDF"
        assert pd.external_baseapp_tcp_address == Addr(
            ip_addr="0.0.0.0", port=Port(20015)
        )
        assert pd.external_baseapp_udp_address == Addr(
            ip_addr="0.0.0.0", port=Port(20005)
        )


class Test_registerPendingAccountToBaseapp:
    msg_spec = msgspec.baseappmgr.registerPendingAccountToBaseapp
    data = b"\x11\x00?\x00mbLYLNYIDF\x00mbLYLNYIDF\x00hKjiTCXJSp\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00"

    def test_registerPendingAccountToBaseapp(self):
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = RegisterPendingAccountToBaseappMsgParser().parse(msg)

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

        assert (
            res.msg_id == msgspec.baseappmgr.registerPendingAccountToBaseapp.id
        )

        pd = res.result

        assert pd.login == "mbLYLNYIDF"
        assert pd.account_name == "mbLYLNYIDF"
        assert pd.password == "hKjiTCXJSp"
        assert pd.needCheckPassword == 1
        assert pd.dbid == 1
        assert pd.flags == 0
        assert pd.deadline == 0
        assert pd.client_type == ClientType.LINUX
        assert pd.forceInternalLogin == 0
        assert pd.datas == ""


# ==============================================================================
# НОВЫЕ ТЕСТЫ
# ==============================================================================


class TestBaseappMgr_lookApp:
    """Тесты сообщения BaseappMgr::lookApp."""

    msg_spec = msgspec.baseappmgr.lookApp
    data = b"\x09\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = LookAppMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestBaseappMgr_onLookApp:
    """Тесты сообщения BaseappMgr::onLookApp."""

    msg_spec = msgspec.baseappmgr.onLookApp
    data = b"\x0b\x00\x0c\x00\x04\x00\x00\x00\xd1\x07\x00\x00\x01\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = OnLookAppMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestBaseappMgr_updateBaseapp:
    """Тесты сообщения BaseappMgr::updateBaseapp."""

    msg_spec = msgspec.baseappmgr.updateBaseapp
    data = b"\x15\x00\x18\x00\xd1\x07\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = UpdateBaseappMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestBaseappMgr_onBaseappInitProgress:
    """Тесты сообщения BaseappMgr::onBaseappInitProgress."""

    msg_spec = msgspec.baseappmgr.onBaseappInitProgress
    data = b"\x16\x00\x0c\x00\xd1\x07\x00\x00\x00\x00\x80?\x00\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = OnBaseappInitProgressMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestBaseappMgr_reqCreateEntityAnywhere:
    """Тесты сообщения BaseappMgr::reqCreateEntityAnywhere."""

    msg_spec = msgspec.baseappmgr.reqCreateEntityAnywhere
    data = b"\x0b\x00\x10\x00\x08\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = ReqCreateEntityAnywhereMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestBaseappMgr_reqCloseServer:
    """Тесты сообщения BaseappMgr::reqCloseServer."""

    msg_spec = msgspec.baseappmgr.reqCloseServer
    data = b"\x14\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = ReqCloseServerMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestBaseappMgr_queryLoad:
    """Тесты сообщения BaseappMgr::queryLoad."""

    msg_spec = msgspec.baseappmgr.queryLoad
    data = b"\x0a\x00\x04\x00\xd1\x07\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = QueryLoadMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestBaseappMgr_reqCreateEntityRemotely:
    """Тесты сообщения BaseappMgr::reqCreateEntityRemotely."""

    msg_spec = msgspec.baseappmgr.reqCreateEntityRemotely
    data = b"\x0c\x00\x10\x00\x08\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = ReqCreateEntityRemotelyMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestBaseappMgr_reqCreateEntityAnywhereFromDBIDQueryBestBaseappID:
    """Тесты сообщения BaseappMgr::reqCreateEntityAnywhereFromDBIDQueryBestBaseappID."""

    msg_spec = (
        msgspec.baseappmgr.reqCreateEntityAnywhereFromDBIDQueryBestBaseappID
    )
    data = b"\x0d\x00\x10\x00\x08\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = (
            ReqCreateEntityAnywhereFromDBIDQueryBestBaseappIDMsgParser().parse(
                msg
            )
        )

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestBaseappMgr_reqCreateEntityAnywhereFromDBID:
    """Тесты сообщения BaseappMgr::reqCreateEntityAnywhereFromDBID."""

    msg_spec = msgspec.baseappmgr.reqCreateEntityAnywhereFromDBID
    data = b"\x0e\x00\x10\x00\x08\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = ReqCreateEntityAnywhereFromDBIDMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestBaseappMgr_reqCreateEntityRemotelyFromDBID:
    """Тесты сообщения BaseappMgr::reqCreateEntityRemotelyFromDBID."""

    msg_spec = msgspec.baseappmgr.reqCreateEntityRemotelyFromDBID
    data = b"\x0f\x00\x10\x00\x08\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = ReqCreateEntityRemotelyFromDBIDMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestBaseappMgr_reqKillServer:
    """Тесты сообщения BaseappMgr::reqKillServer."""

    msg_spec = msgspec.baseappmgr.reqKillServer
    data = b"\x18\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = ReqKillServerMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestBaseappMgr_startProfile:
    """Тесты сообщения BaseappMgr::startProfile."""

    msg_spec = msgspec.baseappmgr.startProfile
    data = b"\x17\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = StartProfileMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestBaseappMgr_queryWatcher:
    """Тесты сообщения BaseappMgr::queryWatcher."""

    msg_spec = msgspec.baseappmgr.queryWatcher
    data = b"\x04\xa0\x10\x00\x08\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = QueryWatcherMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestBaseappMgr_queryAppsLoads:
    """Тесты сообщения BaseappMgr::queryAppsLoads."""

    msg_spec = msgspec.baseappmgr.queryAppsLoads
    data = b"\x01\xc3\x0f\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = QueryAppsLoadsMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestBaseappMgr_reqAccountBindEmailAllocCallbackLoginapp:
    """Тесты сообщения BaseappMgr::reqAccountBindEmailAllocCallbackLoginapp."""

    msg_spec = msgspec.baseappmgr.reqAccountBindEmailAllocCallbackLoginapp
    data = b"\x19\x00\x10\x00\x08\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = ReqAccountBindEmailAllocCallbackLoginappMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestBaseappMgr_forwardMessage:
    """Тесты сообщения BaseappMgr::forwardMessage."""

    msg_spec = msgspec.baseappmgr.forwardMessage
    data = b"\x10\x00\x10\x00\x08\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = ForwardMessageMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestBaseappMgr_registerPendingAccountToBaseappAddr:
    """Тесты сообщения BaseappMgr::registerPendingAccountToBaseappAddr."""

    msg_spec = msgspec.baseappmgr.registerPendingAccountToBaseappAddr
    data = b"\x13\x00\x10\x00\x08\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = RegisterPendingAccountToBaseappAddrMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestBaseappMgr_onReqAccountBindEmailCBFromLoginapp:
    """Тесты сообщения BaseappMgr::onReqAccountBindEmailCBFromLoginapp."""

    msg_spec = msgspec.baseappmgr.onReqAccountBindEmailCBFromLoginapp
    data = b"\x1a\x00\x10\x00\x08\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = OnReqAccountBindEmailCBFromLoginappMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id
