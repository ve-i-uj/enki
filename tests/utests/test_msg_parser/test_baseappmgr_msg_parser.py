"""Тесты на парсинг сообщений от компонента BaseappMgr."""

from enki import msgspec
from enki.kbeenum import ClientType
from enki.msg.msg_serializer import MessageSerializer
from enki.msg_parser.baseappmgr_msg_parser import (
    OnAppActiveTickMsgParser,
    OnPendingAccountGetBaseappAddrMsgParser,
    OnRegisterNewAppMsgParser,
    RegisterPendingAccountToBaseappMsgParser,
)
from enki.msgspec import BaseappMgrMsgSpecByID
from enki.net.addr import Addr, Port


def normalize_wireshark_data(str_data: str) -> bytes:
    """Конвертирует скопированные из WireShark данные, как "as Hex String"."""
    return bytes.fromhex(str_data)


class TestBaseappMgr_onAppActiveTick:
    """Тесты сообщения BaseappMgr::onAppActiveTick."""

    msg_spec = msgspec.baseappmgr.onAppActiveTick
    data = b"A\xd7\n\x00\x00\x00\xd1\x07\x00\x00\x00\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, _data_tail = serializer.deserialize_only_data(
            memoryview(self.data), self.msg_spec.id
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


class TestBaseappMgr_onRegisterNewApp:
    """Тесты сообщения BaseappMgr::onRegisterNewApp."""

    msg_spec = msgspec.baseappmgr.onRegisterNewApp
    data = b"\x08\x00*\x00\xe8\x03\x00\x00root\x00\x04\x00\x00\x00q\x17\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xac\x12\x00\x08\xb6\x17\x00\x00\x00\x00\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
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


class Test_onGetEntityAppFromDbmgr:
    msg_spec = msgspec.baseappmgr.onPendingAccountGetBaseappAddr
    data = b'\x12\x00"\x00mbLYLNYIDF\x00mbLYLNYIDF\x000.0.0.0\x00N/N%'

    def test_onPendingAccountGetBaseappAddr(self):
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

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

        assert res.msg_id == msgspec.baseappmgr.onPendingAccountGetBaseappAddr.id

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
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

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

        assert res.msg_id == msgspec.baseappmgr.registerPendingAccountToBaseapp.id

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
