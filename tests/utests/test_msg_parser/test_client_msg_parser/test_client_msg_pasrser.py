"""Тесты парсинга сообщений Client::*."""

from enki import msgspec
from enki.kbeenum import ComponentType, ServerError
from enki.msg.msg_serializer import MessageSerializer
from enki.msg_parser.client_msg_parser.client_msg_pasrser import (
    OnHelloCBMsgParser,
    OnImportClientMessagesMsgParser,
    OnLoginFailedMsgParser,
    OnLoginSuccessfullyMsgParser,
    OnScriptVersionNotMatchMsgParser,
    OnVersionNotMatchMsgParser,
)
from enki.net.addr import Addr, Port


class TestOnHelloCB:
    """Test Client::onHelloCB."""

    data = b"\t\x02S\x002.5.10\x000.1.0\x001102EA4445FA7BC78DFA939A2161D781\x00ADB0AF58A3C2E7C576C9B3D1820FB606\x00\x02\x00\x00\x00"
    msg_spec = msgspec.client.onHelloCB

    async def test_on_created_proxy_no_components(self):
        serializer = MessageSerializer(msgspec.ClientappMsgSpecByID)
        msg, _ = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = OnHelloCBMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга, чтобы не было опечаток и т.п.
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
        assert pd.assets_version == "0.1.0"
        assert pd.protocol_md5 == "1102EA4445FA7BC78DFA939A2161D781"
        assert pd.entity_def_md5 == "ADB0AF58A3C2E7C576C9B3D1820FB606"
        assert pd.component_type == ComponentType.LOGINAPP


class TestOnLoginSuccessfully:
    """Test Client::onLoginSuccessfully."""

    data = b"\xf6\x01\x1e\x00iwHHfZGDKk\x000.0.0.0\x00/N%N\x03\x00\x00\x00123"
    msg_spec = msgspec.client.onLoginSuccessfully

    async def test_on_created_proxy_no_components(self):
        serializer = MessageSerializer(msgspec.ClientappMsgSpecByID)
        msg, _ = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = OnLoginSuccessfullyMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга, чтобы не было опечаток и т.п.
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

        assert pd.account_name == "iwHHfZGDKk"
        assert pd.host == "0.0.0.0"
        assert pd.baseapp_tcp_address == Addr(ip_addr="0.0.0.0", port=Port(20015))
        assert pd.baseapp_udp_address == Addr(ip_addr="0.0.0.0", port=Port(20005))
        assert pd.data == b"123"


class TestOnLoginFailed:
    """Test Client::OnLoginFailed."""

    data = b"\xf7\x01\x06\x00\x0c\x00\x00\x00\x00\x00"
    msg_spec = msgspec.client.onLoginFailed

    async def test_onLoginFailed(self):
        """Test Client::OnLoginFailed."""
        serializer = MessageSerializer(msgspec.ClientappMsgSpecByID)
        msg, _ = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = OnLoginFailedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга, чтобы не было опечаток и т.п.
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

        assert pd.ret_code == ServerError.ENTITYDEFS_NOT_MATCH


class TestOnVersionNotMatch:
    """Test Client::onVersionNotMatch."""

    data = b"\x0b\x02\x07\x002.5.10\x00"
    msg_spec = msgspec.client.onVersionNotMatch

    async def test_on_created_proxy_no_components(self):
        serializer = MessageSerializer(msgspec.ClientappMsgSpecByID)
        msg, _ = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = OnVersionNotMatchMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга, чтобы не было опечаток и т.п.
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


class TestOnScriptVersionNotMatch:
    """Test Client::onScriptVersionNotMatch."""

    data = b"\n\x02\x06\x000.1.0\x00"
    msg_spec = msgspec.client.onScriptVersionNotMatch

    async def test_on_created_proxy_no_components(self):
        serializer = MessageSerializer(msgspec.ClientappMsgSpecByID)
        msg, _ = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = OnScriptVersionNotMatchMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга, чтобы не было опечаток и т.п.
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

        assert pd.assets_version == "0.1.0"


class TestOnImportClientMessages:
    """Test Client::onImportClientMessages."""

    data = b"\x06\x02\xf0\x0c`\x00\x08\x00\x02\x00Client_onReloginBaseappFailed\x00\x00\x01\x03\t\x00\xff\xffClient_onEntityLeaveWorldOptimized\x00\xff\x00\n\x00\xff\xffClient_onRemoteMethodCallOptimized\x00\xff\x00\x0b\x00\xff\xffClient_onUpdatePropertysOptimized\x00\xff\x00\x0c\x00\xff\xffClient_onSetEntityPosAndDir\x00\xff\x00\r\x00\x0c\x00Client_onUpdateBasePos\x00\x00\x03\r\r\r\x0e\x00\xff\xffClient_onUpdateBaseDir\x00\xff\x00\x0f\x00\x08\x00Client_onUpdateBasePosXZ\x00\x00\x02\r\r\x10\x00\xff\xffClient_onUpdateData\x00\xff\x00\x11\x00\xff\xffClient_onUpdateData_ypr\x00\xff\x00\x12\x00\xff\xffClient_onUpdateData_yp\x00\xff\x00\x13\x00\xff\xffClient_onUpdateData_yr\x00\xff\x00\x14\x00\xff\xffClient_onUpdateData_pr\x00\xff\x00\x15\x00\xff\xffClient_onUpdateData_y\x00\xff\x00\x16\x00\xff\xffClient_onUpdateData_p\x00\xff\x00\x17\x00\xff\xffClient_onUpdateData_r\x00\xff\x00\x18\x00\xff\xffClient_onUpdateData_xz\x00\xff\x00\x19\x00\xff\xffClient_onUpdateData_xz_ypr\x00\xff\x00\x1a\x00\xff\xffClient_onUpdateData_xz_yp\x00\xff\x00\x1b\x00\xff\xffClient_onUpdateData_xz_yr\x00\xff\x00\x1c\x00\xff\xffClient_onUpdateData_xz_pr\x00\xff\x00\x1d\x00\xff\xffClient_onUpdateData_xz_y\x00\xff\x00\x1e\x00\xff\xffClient_onUpdateData_xz_p\x00\xff\x00\x1f\x00\xff\xffClient_onUpdateData_xz_r\x00\xff\x00 \x00\xff\xffClient_onUpdateData_xyz\x00\xff\x00!\x00\xff\xffClient_onUpdateData_xyz_ypr\x00\xff\x00\"\x00\xff\xffClient_onUpdateData_xyz_yp\x00\xff\x00#\x00\xff\xffClient_onUpdateData_xyz_yr\x00\xff\x00$\x00\xff\xffClient_onUpdateData_xyz_pr\x00\xff\x00%\x00\xff\xffClient_onUpdateData_xyz_y\x00\xff\x00&\x00\xff\xffClient_onUpdateData_xyz_p\x00\xff\x00'\x00\xff\xffClient_onUpdateData_xyz_r\x00\xff\x00(\x00\xff\xffClient_onUpdateData_ypr_optimized\x00\xff\x00)\x00\xff\xffClient_onUpdateData_yp_optimized\x00\xff\x00*\x00\xff\xffClient_onUpdateData_yr_optimized\x00\xff\x00+\x00\xff\xffClient_onUpdateData_pr_optimized\x00\xff\x00,\x00\xff\xffClient_onUpdateData_y_optimized\x00\xff\x00-\x00\xff\xffClient_onUpdateData_p_optimized\x00\xff\x00.\x00\xff\xffClient_onUpdateData_r_optimized\x00\xff\x00/\x00\xff\xffClient_onUpdateData_xz_optimized\x00\xff\x000\x00\xff\xffClient_onUpdateData_xz_ypr_optimized\x00\xff\x001\x00\xff\xffClient_onUpdateData_xz_yp_optimized\x00\xff\x002\x00\xff\xffClient_onUpdateData_xz_yr_optimized\x00\xff\x003\x00\xff\xffClient_onUpdateData_xz_pr_optimized\x00\xff\x004\x00\xff\xffClient_onUpdateData_xz_y_optimized\x00\xff\x005\x00\xff\xffClient_onUpdateData_xz_p_optimized\x00\xff\x006\x00\xff\xffClient_onUpdateData_xz_r_optimized\x00\xff\x007\x00\xff\xffClient_onUpdateData_xyz_optimized\x00\xff\x008\x00\xff\xffClient_onUpdateData_xyz_ypr_optimized\x00\xff\x009\x00\xff\xffClient_onUpdateData_xyz_yp_optimized\x00\xff\x00:\x00\xff\xffClient_onUpdateData_xyz_yr_optimized\x00\xff\x00;\x00\xff\xffClient_onUpdateData_xyz_pr_optimized\x00\xff\x00<\x00\xff\xffClient_onUpdateData_xyz_y_optimized\x00\xff\x00=\x00\xff\xffClient_onUpdateData_xyz_p_optimized\x00\xff\x00>\x00\xff\xffClient_onUpdateData_xyz_r_optimized\x00\xff\x00?\x00\xff\xffClient_onImportServerErrorsDescr\x00\xff\x00@\x00\xff\xffClient_onImportClientSDK\x00\xff\x00A\x00\xff\xffClient_initSpaceData\x00\xff\x00B\x00\xff\xffClient_setSpaceData\x00\x00\x03\x04\x01\x01C\x00\xff\xffClient_delSpaceData\x00\x00\x02\x04\x01D\x00\x02\x00Client_onReqAccountResetPasswordCB\x00\x00\x01\x03E\x00\x02\x00Client_onReqAccountBindEmailCB\x00\x00\x01\x03F\x00\x02\x00Client_onReqAccountNewPasswordCB\x00\x00\x01\x03G\x00\xff\xffClient_onReloginBaseappSuccessfully\x00\xff\x00H\x00\x00\x00Client_onAppActiveTickCB\x00\x00\x00\xf5\x01\xff\xffClient_onCreateAccountResult\x00\xff\x00\xf6\x01\xff\xffClient_onLoginSuccessfully\x00\xff\x00\xf7\x01\xff\xffClient_onLoginFailed\x00\xff\x00\xf8\x01\xff\xffClient_onCreatedProxies\x00\x00\x03\x05\x08\x01\xf9\x01\x02\x00Client_onLoginBaseappFailed\x00\x00\x01\x03\xfa\x01\xff\xffClient_onRemoteMethodCall\x00\xff\x00\xfb\x01\xff\xffClient_onEntityEnterWorld\x00\xff\x00\xfc\x01\x04\x00Client_onEntityLeaveWorld\x00\x00\x01\x08\xfd\x01\xff\xffClient_onEntityEnterSpace\x00\xff\x00\xfe\x01\x04\x00Client_onEntityLeaveSpace\x00\x00\x01\x08\xff\x01\xff\xffClient_onUpdatePropertys\x00\xff\x00\x00\x02\x04\x00Client_onEntityDestroyed\x00\x00\x01\x08\x02\x02\xff\xffClient_onStreamDataStarted\x00\x00\x03\x07\x04\x01\x03\x02\xff\xffClient_onStreamDataRecv\x00\xff\x00\x04\x02\x02\x00Client_onStreamDataCompleted\x00\x00\x01\x07\x05\x02\x02\x00Client_onKicked\x00\x00\x01\x03\x06\x02\xff\xffClient_onImportClientMessages\x00\xff\x00\x07\x02\xff\xffClient_onImportClientEntityDef\x00\xff\x00\t\x02\xff\xffClient_onHelloCB\x00\xff\x00\n\x02\xff\xffClient_onScriptVersionNotMatch\x00\xff\x00\x0b\x02\xff\xffClient_onVersionNotMatch\x00\xff\x00\x0c\x02\x05\x00Client_onControlEntity\x00\x00\x02\x08\x06\x02\x00\xff\xffLoginapp_reqCreateAccount\x00\x00\x00\x03\x00\xff\xffLoginapp_login\x00\x00\x00\x04\x00\xff\xffLoginapp_hello\x00\x00\x00\x05\x00\x00\x00Loginapp_importClientMessages\x00\x00\x00\x06\x00\xff\xffLoginapp_reqCreateMailAccount\x00\x00\x00\x07\x00\xff\xffLoginapp_importClientSDK\x00\x00\x00\x08\x00\x00\x00Loginapp_importServerErrorsDescr\x00\x00\x00\x0b\x00\x00\x00Loginapp_onClientActiveTick\x00\x00\x00\x0c\x00\xff\xffLoginapp_reqAccountResetPassword\x00\x00\x01\x01"
    msg_spec = msgspec.client.onImportClientMessages

    async def test_on_created_proxy_no_components(self):
        serializer = MessageSerializer(msgspec.ClientappMsgSpecByID)
        msg, _ = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = OnImportClientMessagesMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга, чтобы не было опечаток и т.п.
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

        assert len(pd.msg_specs) == 96
