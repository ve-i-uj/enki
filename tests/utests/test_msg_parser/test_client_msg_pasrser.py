"""Тесты парсинга сообщений Client::*."""

import struct

import pytest

from enki import msgspec
from enki.kbeenum import ServerError
from enki.msg.msg_serializer import MessageSerializer
from enki.msg_parser.client_msg_parser import (
    DelSpaceDataMsgParser,
    InitSpaceDataMsgParser,
    OnAppActiveTickCBMsgParser,
    OnControlEntityMsgParser,
    OnCreateAccountResultMsgParser,
    OnCreatedProxiesMsgParser,
    OnEntityDestroyedMsgParser,
    OnEntityEnterSpaceMsgParser,
    OnEntityEnterWorldMsgParser,
    OnEntityLeaveSpaceMsgParser,
    OnEntityLeaveWorldMsgParser,
    OnEntityLeaveWorldOptimizedMsgParser,
    OnHelloCBMsgParser,
    OnImportClientEntityDefMsgParser,
    OnImportClientMessagesMsgParser,
    OnImportClientSDKMsgParser,
    OnImportServerErrorsDescrMsgParser,
    OnKickedMsgParser,
    OnLoginBaseappFailedMsgParser,
    OnLoginFailedMsgParser,
    OnLoginSuccessfullyMsgParser,
    OnReloginBaseappFailedMsgParser,
    OnReloginBaseappSuccessfullyMsgParser,
    OnRemoteMethodCallMsgParser,
    OnRemoteMethodCallOptimizedMsgParser,
    OnReqAccountBindEmailCBMsgParser,
    OnReqAccountNewPasswordCBMsgParser,
    OnReqAccountResetPasswordCBMsgParser,
    OnScriptVersionNotMatchMsgParser,
    OnSetEntityPosAndDirMsgParser,
    OnStreamDataCompletedMsgParser,
    OnStreamDataRecvMsgParser,
    OnStreamDataStartedMsgParser,
    OnUpdateBaseDirMsgParser,
    OnUpdateBasePosMsgParser,
    OnUpdateBasePosXZMsgParser,
    OnUpdateDataMsgParser,
    OnUpdateDataPMsgParser,
    OnUpdateDataPOptimizedMsgParser,
    OnUpdateDataPrMsgParser,
    OnUpdateDataPrOptimizedMsgParser,
    OnUpdateDataRMsgParser,
    OnUpdateDataROptimizedMsgParser,
    OnUpdateDataXyzMsgParser,
    OnUpdateDataXyzOptimizedMsgParser,
    OnUpdateDataXyzPMsgParser,
    OnUpdateDataXyzPOptimizedMsgParser,
    OnUpdateDataXyzPrMsgParser,
    OnUpdateDataXyzPrOptimizedMsgParser,
    OnUpdateDataXyzRMsgParser,
    OnUpdateDataXyzROptimizedMsgParser,
    OnUpdateDataXyzYMsgParser,
    OnUpdateDataXyzYOptimizedMsgParser,
    OnUpdateDataXyzYpMsgParser,
    OnUpdateDataXyzYpOptimizedMsgParser,
    OnUpdateDataXyzYprMsgParser,
    OnUpdateDataXyzYprOptimizedMsgParser,
    OnUpdateDataXyzYrMsgParser,
    OnUpdateDataXyzYrOptimizedMsgParser,
    OnUpdateDataXzMsgParser,
    OnUpdateDataXzOptimizedMsgParser,
    OnUpdateDataXzPMsgParser,
    OnUpdateDataXzPOptimizedMsgParser,
    OnUpdateDataXzPrMsgParser,
    OnUpdateDataXzPrOptimizedMsgParser,
    OnUpdateDataXzRMsgParser,
    OnUpdateDataXzROptimizedMsgParser,
    OnUpdateDataXzYMsgParser,
    OnUpdateDataXzYOptimizedMsgParser,
    OnUpdateDataXzYpMsgParser,
    OnUpdateDataXzYpOptimizedMsgParser,
    OnUpdateDataXzYprMsgParser,
    OnUpdateDataXzYprOptimizedMsgParser,
    OnUpdateDataXzYrMsgParser,
    OnUpdateDataXzYrOptimizedMsgParser,
    OnUpdateDataYMsgParser,
    OnUpdateDataYOptimizedMsgParser,
    OnUpdateDataYpMsgParser,
    OnUpdateDataYpOptimizedMsgParser,
    OnUpdateDataYprMsgParser,
    OnUpdateDataYprOptimizedMsgParser,
    OnUpdateDataYrMsgParser,
    OnUpdateDataYrOptimizedMsgParser,
    OnUpdatePropertysMsgParser,
    OnUpdatePropertysOptimizedMsgParser,
    OnVersionNotMatchMsgParser,
    SetSpaceDataMsgParser,
)


class TestClient_onHelloCB:
    """Тесты сообщения Client::onHelloCB."""

    msg_spec = msgspec.client.onHelloCB
    data = b"\t\x02S\x002.5.10\x000.1.0\x006615F2367124A5E4B390207ACC4906B6\x0006E15F102B481ACF8CA19E2F410D1B64\x00\x06\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = OnHelloCBMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        pd = result.result
        assert pd.kbe_version == "2.5.10"
        assert pd.assets_version == "0.1.0"
        assert pd.protocol_md5 == "6615F2367124A5E4B390207ACC4906B6"
        assert pd.entity_def_md5 == "06E15F102B481ACF8CA19E2F410D1B64"
        assert pd.componentType == 6


class TestClient_onLoginSuccessfully:
    """Тесты сообщения Client::onLoginSuccessfully."""

    msg_spec = msgspec.client.onLoginSuccessfully
    data = b"\xf6\x01\x1d\x001\x000.0.0.0\x00/N%N\x0b\x00\x00\x00client_data"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = OnLoginSuccessfullyMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        pd = result.result
        assert pd.account_name == "1"
        assert pd.host == "0.0.0.0"
        assert pd.tcpPort == 20015
        assert pd.udpPort == 20005
        assert pd.data == b"client_data"


class TestOnLoginFailed:
    """Test Client::OnLoginFailed."""

    data = b"\xf7\x01\x06\x00\x0c\x00\x00\x00\x00\x00"
    msg_spec = msgspec.client.onLoginFailed

    async def test_onLoginFailed(self):
        """Test Client::OnLoginFailed."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
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
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
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
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
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

    async def test_success(self):
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
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


class TestClient_onCreatedProxies:
    """Тесты сообщения Client::onCreatedProxies."""

    msg_spec = msgspec.client.onCreatedProxies
    data = b"\xf8\x01\x14\x00\x00\x00mxk\xfaui\x01\x00\x00\x00Account\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = OnCreatedProxiesMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        pd = result.result
        assert pd.rnd_uuid == 7599255285746434048
        assert pd.entity_id == 1
        assert pd.entity_type == "Account"


class TestClient_onUpdatePropertys:
    """Тесты сообщения Client::onUpdatePropertys."""

    msg_spec = msgspec.client.onUpdatePropertys
    data = b"\xff\x01\x0e\x00\x01\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = OnUpdatePropertysMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        pd = result.result
        assert pd.entity_id == 1
        assert pd.entity_data == b"\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00"


class TestClient_onAppActiveTickCB:
    """Тесты сообщения Client::onAppActiveTickCB."""

    msg_spec = msgspec.client.onAppActiveTickCB
    # Сообщение без данных (lenght=0)
    data = b"H\x00"

    def test_success(self):
        """Удачный парсинг сообщения без данных."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = OnAppActiveTickCBMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        # Проверка нейминга
        assert result.msg_id == self.msg_spec.id
        assert result.__class__.__name__ == "OnAppActiveTickCBMsgParserResult"
        assert result.result.__class__.__name__ == "OnAppActiveTickCBParsedMsgData"
        assert result.msg_id == self.msg_spec.id
        assert result.text == ""


class TestOnReloginBaseappFailed:
    """Test Client::onReloginBaseappFailed."""

    msg_spec = msgspec.client.onReloginBaseappFailed
    # UINT16: 0x0C00 (12) - ServerError.LOGIN_APP_STOPPED
    data = b"\x08\x00\x0c\x00"

    @pytest.mark.skip("Случайные данные")
    def test_on_relogin_baseapp_failed(self):
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnReloginBaseappFailedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга
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
        assert pd.ret_code == ServerError.LOGIN_APP_STOPPED


class TestOnEntityLeaveWorldOptimized:
    """Test Client::onEntityLeaveWorldOptimized."""

    msg_spec = msgspec.client.onEntityLeaveWorldOptimized
    # Произвольные бинарные данные
    data = b"\x09\x00\x05\x00\x01\x02\x03\x04\x05"

    def test_on_entity_leave_world_optimized(self):
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnEntityLeaveWorldOptimizedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга
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
        assert pd.entity_data == b"\x01\x02\x03\x04\x05"


class TestOnRemoteMethodCallOptimized:
    """Test Client::onRemoteMethodCallOptimized."""

    msg_spec = msgspec.client.onRemoteMethodCallOptimized
    # Произвольные бинарные данные
    data = b"\x0a\x00\x06\x00\xaa\xbb\xcc\xdd\xee\xff"

    def test_on_remote_method_call_optimized(self):
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnRemoteMethodCallOptimizedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга
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
        assert pd.method_data == b"\xaa\xbb\xcc\xdd\xee\xff"


class TestOnUpdatePropertysOptimized:
    """Test Client::onUpdatePropertysOptimized."""

    msg_spec = msgspec.client.onUpdatePropertysOptimized
    # Произвольные бинарные данные
    data = b"\x0b\x00\x08\x00\x11\x22\x33\x44\x55\x66\x77\x88"

    def test_on_update_propertys_optimized(self):
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdatePropertysOptimizedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга
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
        assert pd.property_data == b"\x11\x22\x33\x44\x55\x66\x77\x88"


class TestOnSetEntityPosAndDir:
    """Test Client::onSetEntityPosAndDir."""

    msg_spec = msgspec.client.onSetEntityPosAndDir
    # Произвольные бинарные данные
    data = b"\x0c\x00\x07\x00\x99\x88\x77\x66\x55\x44\x33"

    def test_on_set_entity_pos_and_dir(self):
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnSetEntityPosAndDirMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга
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
        assert pd.position_data == b"\x99\x88\x77\x66\x55\x44\x33"


class TestOnUpdateBasePos:
    """Test Client::onUpdateBasePos."""

    msg_spec = msgspec.client.onUpdateBasePos
    # 3 float значения: 1.5, 2.5, 3.5
    data = b"\r\x00\x0c\x00" + struct.pack("fff", 1.5, 2.5, 3.5)

    @pytest.mark.skip("Случайные данные")
    def test_on_update_base_pos(self):
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateBasePosMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга
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
        assert pd.x == 1.5
        assert pd.y == 2.5
        assert pd.z == 3.5


class TestOnUpdateBaseDir:
    """Test Client::onUpdateBaseDir."""

    msg_spec = msgspec.client.onUpdateBaseDir
    # Произвольные бинарные данные
    data = b"\x0e\x00\x05\x00\xaa\xcc\xee\x11\x22"

    @pytest.mark.skip("Случайные данные")
    def test_on_update_base_dir(self):
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateBaseDirMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга
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
        assert pd.direction_data == b"\xaa\xcc\xee\x11\x22"


class TestOnUpdateBasePosXZ:
    """Test Client::onUpdateBasePosXZ."""

    msg_spec = msgspec.client.onUpdateBasePosXZ
    # 2 float значения: 10.5, 20.5
    data = b"\x0f\x00\x08\x00" + struct.pack("ff", 10.5, 20.5)

    @pytest.mark.skip("Случайные данные")
    def test_on_update_base_pos_xz(self):
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateBasePosXZMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга
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
        assert pd.x == 10.5
        assert pd.z == 20.5


class TestOnUpdateData:
    """Test Client::onUpdateData."""

    msg_spec = msgspec.client.onUpdateData
    # Произвольные бинарные данные
    data = b"\x10\x00\x06\x00\xde\xad\xbe\xef\x12\x34"

    def test_on_update_data(self):
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга
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
        assert pd.update_data == b"\xde\xad\xbe\xef\x12\x34"


class TestOnEntityLeaveWorld:
    """Test Client::onEntityLeaveWorld."""

    msg_spec = msgspec.client.onEntityLeaveWorld
    # INT32: 1001
    data = b"\xfc\x01\x04\x00\xe9\x03\x00\x00"

    @pytest.mark.skip("Случайные данные")
    def test_on_entity_leave_world(self):
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnEntityLeaveWorldMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга
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
        assert pd.entity_id == 1001


class TestOnEntityDestroyed:
    """Test Client::onEntityDestroyed."""

    msg_spec = msgspec.client.onEntityDestroyed
    # INT32: 2001
    data = b"\x00\x02\x04\x00\xd1\x07\x00\x00"

    @pytest.mark.skip("Случайные данные")
    def test_on_entity_destroyed(self):
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnEntityDestroyedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга
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
        assert pd.entity_id == 2001


class TestOnStreamDataCompleted:
    """Test Client::onStreamDataCompleted."""

    msg_spec = msgspec.client.onStreamDataCompleted
    # INT16: 42
    data = b"\x04\x02\x02\x00\x2a\x00"

    @pytest.mark.skip("Случайные данные")
    def test_on_stream_data_completed(self):
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnStreamDataCompletedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга
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
        assert pd.stream_id == 42


class TestOnLoginBaseappFailed:
    """Test Client::onLoginBaseappFailed."""

    msg_spec = msgspec.client.onLoginBaseappFailed
    # UINT16: 0x0F00 (15) - ServerError.LOGIN_INVALID_PASSWORD
    data = b"\xf9\x01\x02\x00\x0f\x00"

    @pytest.mark.skip("Случайные данные")
    def test_on_login_baseapp_failed(self):
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnLoginBaseappFailedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга
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
        assert pd.ret_code == ServerError.LOGIN_INVALID_PASSWORD


class TestOnControlEntity:
    """Test Client::onControlEntity."""

    msg_spec = msgspec.client.onControlEntity
    # INT32: 3001, INT8: 1
    data = b"\x0c\x02\x05\x00\xb9\x0b\x00\x00\x01"

    @pytest.mark.skip("Случайные данные")
    def test_on_control_entity(self):
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnControlEntityMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга
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
        assert pd.entity_id == 3001
        assert pd.control_type == 1


class TestSetSpaceData:
    """Test Client::setSpaceData."""

    msg_spec = msgspec.client.setSpaceData
    # UINT32: 1, STRING: "key1", STRING: "value1"
    data = b"B\x00\x0f\x00\x01\x00\x00\x00key1\x00value1\x00"

    @pytest.mark.skip("Случайные данные")
    def test_set_space_data(self):
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = SetSpaceDataMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга
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
        assert pd.space_id == 1
        assert pd.key == "key1"
        assert pd.value == "value1"


class TestDelSpaceData:
    """Test Client::delSpaceData."""

    msg_spec = msgspec.client.delSpaceData
    # UINT32: 2, STRING: "key2"
    data = b"C\x00\x0b\x00\x02\x00\x00\x00key2\x00"

    @pytest.mark.skip("Случайные данные")
    def test_del_space_data(self):
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = DelSpaceDataMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга
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
        assert pd.space_id == 2
        assert pd.key == "key2"


class TestOnReqAccountResetPasswordCB:
    """Test Client::onReqAccountResetPasswordCB."""

    msg_spec = msgspec.client.onReqAccountResetPasswordCB
    # UINT16: 0x0100 (1) - ServerError.SUCCESS
    data = b"D\x00\x02\x00\x01\x00"

    @pytest.mark.skip("Случайные данные")
    def test_on_req_account_reset_password_cb(self):
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnReqAccountResetPasswordCBMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга
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


class TestOnReqAccountBindEmailCB:
    """Test Client::onReqAccountBindEmailCB."""

    msg_spec = msgspec.client.onReqAccountBindEmailCB
    # UINT16: 0x0200 (2) - ServerError.INTERNAL_ERROR
    data = b"E\x00\x02\x00\x02\x00"

    @pytest.mark.skip("Случайные данные")
    def test_on_req_account_bind_email_cb(self):
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnReqAccountBindEmailCBMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга
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
        assert pd.ret_code == ServerError.INTERNAL_ERROR


class TestOnReqAccountNewPasswordCB:
    """Test Client::onReqAccountNewPasswordCB."""

    msg_spec = msgspec.client.onReqAccountNewPasswordCB
    # UINT16: 0x0300 (3) - ServerError.NO_SUCH_SERVICE
    data = b"F\x00\x02\x00\x03\x00"

    @pytest.mark.skip("Случайные данные")
    def test_on_req_account_new_password_cb(self):
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnReqAccountNewPasswordCBMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга
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
        assert pd.ret_code == ServerError.NO_SUCH_SERVICE


class TestOnRemoteMethodCall:
    """Test Client::onRemoteMethodCall."""

    msg_spec = msgspec.client.onRemoteMethodCall
    # Произвольные бинарные данные
    data = b"\xfa\x01\x08\x00\x55\x66\x77\x88\x99\xaa\xbb\xcc"

    def test_on_remote_method_call(self):
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnRemoteMethodCallMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        # Проверка нейминга
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
        assert pd.method_data == b"\x55\x66\x77\x88\x99\xaa\xbb\xcc"


class TestOnUpdateDataYpr:
    """Test Client::onUpdateData_ypr."""

    msg_spec = msgspec.client.onUpdateData_ypr
    # Произвольные бинарные данные
    data = b"\x11\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_ypr(self):
        """Тест для Client::onUpdateData_ypr."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataYprMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataYp:
    """Test Client::onUpdateData_yp."""

    msg_spec = msgspec.client.onUpdateData_yp
    # Произвольные бинарные данные
    data = b"\x12\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_yp(self):
        """Тест для Client::onUpdateData_yp."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataYpMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataYr:
    """Test Client::onUpdateData_yr."""

    msg_spec = msgspec.client.onUpdateData_yr
    # Произвольные бинарные данные
    data = b"\x13\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_yr(self):
        """Тест для Client::onUpdateData_yr."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataYrMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataPr:
    """Test Client::onUpdateData_pr."""

    msg_spec = msgspec.client.onUpdateData_pr
    # Произвольные бинарные данные
    data = b"\x14\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_pr(self):
        """Тест для Client::onUpdateData_pr."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataPrMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataY:
    """Test Client::onUpdateData_y."""

    msg_spec = msgspec.client.onUpdateData_y
    # Произвольные бинарные данные
    data = b"\x15\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_y(self):
        """Тест для Client::onUpdateData_y."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataYMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataP:
    """Test Client::onUpdateData_p."""

    msg_spec = msgspec.client.onUpdateData_p
    # Произвольные бинарные данные
    data = b"\x16\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_p(self):
        """Тест для Client::onUpdateData_p."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataPMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataR:
    """Test Client::onUpdateData_r."""

    msg_spec = msgspec.client.onUpdateData_r
    # Произвольные бинарные данные
    data = b"\x17\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_r(self):
        """Тест для Client::onUpdateData_r."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataRMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXz:
    """Test Client::onUpdateData_xz."""

    msg_spec = msgspec.client.onUpdateData_xz
    # Произвольные бинарные данные
    data = b"\x18\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xz(self):
        """Тест для Client::onUpdateData_xz."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXzMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXzYpr:
    """Test Client::onUpdateData_xz_ypr."""

    msg_spec = msgspec.client.onUpdateData_xz_ypr
    # Произвольные бинарные данные
    data = b"\x19\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xz_ypr(self):
        """Тест для Client::onUpdateData_xz_ypr."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXzYprMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXzYp:
    """Test Client::onUpdateData_xz_yp."""

    msg_spec = msgspec.client.onUpdateData_xz_yp
    # Произвольные бинарные данные
    data = b"\x1a\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xz_yp(self):
        """Тест для Client::onUpdateData_xz_yp."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXzYpMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXzYr:
    """Test Client::onUpdateData_xz_yr."""

    msg_spec = msgspec.client.onUpdateData_xz_yr
    # Произвольные бинарные данные
    data = b"\x1b\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xz_yr(self):
        """Тест для Client::onUpdateData_xz_yr."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXzYrMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXzPr:
    """Test Client::onUpdateData_xz_pr."""

    msg_spec = msgspec.client.onUpdateData_xz_pr
    # Произвольные бинарные данные
    data = b"\x1c\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xz_pr(self):
        """Тест для Client::onUpdateData_xz_pr."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXzPrMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXzY:
    """Test Client::onUpdateData_xz_y."""

    msg_spec = msgspec.client.onUpdateData_xz_y
    # Произвольные бинарные данные
    data = b"\x1d\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xz_y(self):
        """Тест для Client::onUpdateData_xz_y."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXzYMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXzP:
    """Test Client::onUpdateData_xz_p."""

    msg_spec = msgspec.client.onUpdateData_xz_p
    # Произвольные бинарные данные
    data = b"\x1e\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xz_p(self):
        """Тест для Client::onUpdateData_xz_p."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXzPMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXzR:
    """Test Client::onUpdateData_xz_r."""

    msg_spec = msgspec.client.onUpdateData_xz_r
    # Произвольные бинарные данные
    data = b"\x1f\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xz_r(self):
        """Тест для Client::onUpdateData_xz_r."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXzRMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXyz:
    """Test Client::onUpdateData_xyz."""

    msg_spec = msgspec.client.onUpdateData_xyz
    # Произвольные бинарные данные
    data = b"\x20\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xyz(self):
        """Тест для Client::onUpdateData_xyz."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXyzMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXyzYpr:
    """Test Client::onUpdateData_xyz_ypr."""

    msg_spec = msgspec.client.onUpdateData_xyz_ypr
    # Произвольные бинарные данные
    data = b"\x21\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xyz_ypr(self):
        """Тест для Client::onUpdateData_xyz_ypr."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXyzYprMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXyzYp:
    """Test Client::onUpdateData_xyz_yp."""

    msg_spec = msgspec.client.onUpdateData_xyz_yp
    # Произвольные бинарные данные
    data = b"\x22\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xyz_yp(self):
        """Тест для Client::onUpdateData_xyz_yp."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXyzYpMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXyzYr:
    """Test Client::onUpdateData_xyz_yr."""

    msg_spec = msgspec.client.onUpdateData_xyz_yr
    # Произвольные бинарные данные
    data = b"\x23\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xyz_yr(self):
        """Тест для Client::onUpdateData_xyz_yr."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXyzYrMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXyzPr:
    """Test Client::onUpdateData_xyz_pr."""

    msg_spec = msgspec.client.onUpdateData_xyz_pr
    # Произвольные бинарные данные
    data = b"\x24\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xyz_pr(self):
        """Тест для Client::onUpdateData_xyz_pr."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXyzPrMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXyzY:
    """Test Client::onUpdateData_xyz_y."""

    msg_spec = msgspec.client.onUpdateData_xyz_y
    # Произвольные бинарные данные
    data = b"\x25\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xyz_y(self):
        """Тест для Client::onUpdateData_xyz_y."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXyzYMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXyzP:
    """Test Client::onUpdateData_xyz_p."""

    msg_spec = msgspec.client.onUpdateData_xyz_p
    # Произвольные бинарные данные
    data = b"\x26\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xyz_p(self):
        """Тест для Client::onUpdateData_xyz_p."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXyzPMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXyzR:
    """Test Client::onUpdateData_xyz_r."""

    msg_spec = msgspec.client.onUpdateData_xyz_r
    # Произвольные бинарные данные
    data = b"\x27\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xyz_r(self):
        """Тест для Client::onUpdateData_xyz_r."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXyzRMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataYprOptimized:
    """Test Client::onUpdateData_ypr_optimized."""

    msg_spec = msgspec.client.onUpdateData_ypr_optimized
    # Произвольные бинарные данные
    data = b"(\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_ypr_optimized(self):
        """Тест для Client::onUpdateData_ypr_optimized."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataYprOptimizedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataYpOptimized:
    """Test Client::onUpdateData_yp_optimized."""

    msg_spec = msgspec.client.onUpdateData_yp_optimized
    # Произвольные бинарные данные
    data = b")\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_yp_optimized(self):
        """Тест для Client::onUpdateData_yp_optimized."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataYpOptimizedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataYrOptimized:
    """Test Client::onUpdateData_yr_optimized."""

    msg_spec = msgspec.client.onUpdateData_yr_optimized
    # Произвольные бинарные данные
    data = b"*\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_yr_optimized(self):
        """Тест для Client::onUpdateData_yr_optimized."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataYrOptimizedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataPrOptimized:
    """Test Client::onUpdateData_pr_optimized."""

    msg_spec = msgspec.client.onUpdateData_pr_optimized
    # Произвольные бинарные данные
    data = b"+\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_pr_optimized(self):
        """Тест для Client::onUpdateData_pr_optimized."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataPrOptimizedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataYOptimized:
    """Test Client::onUpdateData_y_optimized."""

    msg_spec = msgspec.client.onUpdateData_y_optimized
    # Произвольные бинарные данные
    data = b",\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_y_optimized(self):
        """Тест для Client::onUpdateData_y_optimized."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataYOptimizedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataPOptimized:
    """Test Client::onUpdateData_p_optimized."""

    msg_spec = msgspec.client.onUpdateData_p_optimized
    # Произвольные бинарные данные
    data = b"-\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_p_optimized(self):
        """Тест для Client::onUpdateData_p_optimized."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataPOptimizedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataROptimized:
    """Test Client::onUpdateData_r_optimized."""

    msg_spec = msgspec.client.onUpdateData_r_optimized
    # Произвольные бинарные данные
    data = b".\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_r_optimized(self):
        """Тест для Client::onUpdateData_r_optimized."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataROptimizedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXzOptimized:
    """Test Client::onUpdateData_xz_optimized."""

    msg_spec = msgspec.client.onUpdateData_xz_optimized
    # Произвольные бинарные данные
    data = b"/\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xz_optimized(self):
        """Тест для Client::onUpdateData_xz_optimized."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXzOptimizedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXzYprOptimized:
    """Test Client::onUpdateData_xz_ypr_optimized."""

    msg_spec = msgspec.client.onUpdateData_xz_ypr_optimized
    # Произвольные бинарные данные
    data = b"0\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xz_ypr_optimized(self):
        """Тест для Client::onUpdateData_xz_ypr_optimized."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXzYprOptimizedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXzYpOptimized:
    """Test Client::onUpdateData_xz_yp_optimized."""

    msg_spec = msgspec.client.onUpdateData_xz_yp_optimized
    # Произвольные бинарные данные
    data = b"1\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xz_yp_optimized(self):
        """Тест для Client::onUpdateData_xz_yp_optimized."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXzYpOptimizedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXzYrOptimized:
    """Test Client::onUpdateData_xz_yr_optimized."""

    msg_spec = msgspec.client.onUpdateData_xz_yr_optimized
    # Произвольные бинарные данные
    data = b"2\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xz_yr_optimized(self):
        """Тест для Client::onUpdateData_xz_yr_optimized."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXzYrOptimizedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXzPrOptimized:
    """Test Client::onUpdateData_xz_pr_optimized."""

    msg_spec = msgspec.client.onUpdateData_xz_pr_optimized
    # Произвольные бинарные данные
    data = b"3\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xz_pr_optimized(self):
        """Тест для Client::onUpdateData_xz_pr_optimized."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXzPrOptimizedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXzYOptimized:
    """Test Client::onUpdateData_xz_y_optimized."""

    msg_spec = msgspec.client.onUpdateData_xz_y_optimized
    # Произвольные бинарные данные
    data = b"4\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xz_y_optimized(self):
        """Тест для Client::onUpdateData_xz_y_optimized."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXzYOptimizedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXzPOptimized:
    """Test Client::onUpdateData_xz_p_optimized."""

    msg_spec = msgspec.client.onUpdateData_xz_p_optimized
    # Произвольные бинарные данные
    data = b"5\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xz_p_optimized(self):
        """Тест для Client::onUpdateData_xz_p_optimized."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXzPOptimizedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXzROptimized:
    """Test Client::onUpdateData_xz_r_optimized."""

    msg_spec = msgspec.client.onUpdateData_xz_r_optimized
    # Произвольные бинарные данные
    data = b"6\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xz_r_optimized(self):
        """Тест для Client::onUpdateData_xz_r_optimized."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXzROptimizedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXyzOptimized:
    """Test Client::onUpdateData_xyz_optimized."""

    msg_spec = msgspec.client.onUpdateData_xyz_optimized
    # Произвольные бинарные данные
    data = b"7\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xyz_optimized(self):
        """Тест для Client::onUpdateData_xyz_optimized."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXyzOptimizedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXyzYprOptimized:
    """Test Client::onUpdateData_xyz_ypr_optimized."""

    msg_spec = msgspec.client.onUpdateData_xyz_ypr_optimized
    # Произвольные бинарные данные
    data = b"8\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xyz_ypr_optimized(self):
        """Тест для Client::onUpdateData_xyz_ypr_optimized."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXyzYprOptimizedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXyzYpOptimized:
    """Test Client::onUpdateData_xyz_yp_optimized."""

    msg_spec = msgspec.client.onUpdateData_xyz_yp_optimized
    # Произвольные бинарные данные
    data = b"9\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xyz_yp_optimized(self):
        """Тест для Client::onUpdateData_xyz_yp_optimized."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXyzYpOptimizedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXyzYrOptimized:
    """Test Client::onUpdateData_xyz_yr_optimized."""

    msg_spec = msgspec.client.onUpdateData_xyz_yr_optimized
    # Произвольные бинарные данные
    data = b":\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xyz_yr_optimized(self):
        """Тест для Client::onUpdateData_xyz_yr_optimized."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXyzYrOptimizedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXyzPrOptimized:
    """Test Client::onUpdateData_xyz_pr_optimized."""

    msg_spec = msgspec.client.onUpdateData_xyz_pr_optimized
    # Произвольные бинарные данные
    data = b";\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xyz_pr_optimized(self):
        """Тест для Client::onUpdateData_xyz_pr_optimized."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXyzPrOptimizedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXyzYOptimized:
    """Test Client::onUpdateData_xyz_y_optimized."""

    msg_spec = msgspec.client.onUpdateData_xyz_y_optimized
    # Произвольные бинарные данные
    data = b"<\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xyz_y_optimized(self):
        """Тест для Client::onUpdateData_xyz_y_optimized."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXyzYOptimizedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXyzPOptimized:
    """Test Client::onUpdateData_xyz_p_optimized."""

    msg_spec = msgspec.client.onUpdateData_xyz_p_optimized
    # Произвольные бинарные данные
    data = b"=\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xyz_p_optimized(self):
        """Тест для Client::onUpdateData_xyz_p_optimized."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXyzPOptimizedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnUpdateDataXyzROptimized:
    """Test Client::onUpdateData_xyz_r_optimized."""

    msg_spec = msgspec.client.onUpdateData_xyz_r_optimized
    # Произвольные бинарные данные
    data = b">\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_update_data_xyz_r_optimized(self):
        """Тест для Client::onUpdateData_xyz_r_optimized."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnUpdateDataXyzROptimizedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnImportServerErrorsDescr:
    """Test Client::onImportServerErrorsDescr."""

    msg_spec = msgspec.client.onImportServerErrorsDescr
    # Произвольные бинарные данные
    data = b"?\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_import_server_errors_descr(self):
        """Тест для Client::onImportServerErrorsDescr."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnImportServerErrorsDescrMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnImportClientSDK:
    """Test Client::onImportClientSDK."""

    msg_spec = msgspec.client.onImportClientSDK
    # Произвольные бинарные данные
    data = b"@\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_import_client_sdk(self):
        """Тест для Client::onImportClientSDK."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnImportClientSDKMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestInitSpaceData:
    """Test Client::initSpaceData."""

    msg_spec = msgspec.client.initSpaceData
    # Произвольные бинарные данные
    data = b"A\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_init_space_data(self):
        """Тест для Client::initSpaceData."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = InitSpaceDataMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnReloginBaseappSuccessfully:
    """Test Client::onReloginBaseappSuccessfully."""

    msg_spec = msgspec.client.onReloginBaseappSuccessfully
    # Произвольные бинарные данные
    data = b"G\x00\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_relogin_baseapp_successfully(self):
        """Тест для Client::onReloginBaseappSuccessfully."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnReloginBaseappSuccessfullyMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnCreateAccountResult:
    """Test Client::onCreateAccountResult."""

    msg_spec = msgspec.client.onCreateAccountResult
    # Произвольные бинарные данные
    data = b"\xf5\x01\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_create_account_result(self):
        """Тест для Client::onCreateAccountResult."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnCreateAccountResultMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnEntityEnterWorld:
    """Test Client::onEntityEnterWorld."""

    msg_spec = msgspec.client.onEntityEnterWorld
    # Произвольные бинарные данные
    data = b"\xfb\x01\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_entity_enter_world(self):
        """Тест для Client::onEntityEnterWorld."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnEntityEnterWorldMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnEntityEnterSpace:
    """Test Client::onEntityEnterSpace."""

    msg_spec = msgspec.client.onEntityEnterSpace
    # Произвольные бинарные данные
    data = b"\xfd\x01\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_entity_enter_space(self):
        """Тест для Client::onEntityEnterSpace."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnEntityEnterSpaceMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnStreamDataStarted:
    """Test Client::onStreamDataStarted."""

    msg_spec = msgspec.client.onStreamDataStarted
    # INT16: 1, UINT32: 1024, STRING: "test.txt", INT8: 0
    data = b"\x02\x02\x10\x00\x01\x00\x00\x04\x00\x00test.txt\x00\x00"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_stream_data_started(self):
        """Тест для Client::onStreamDataStarted."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnStreamDataStartedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnStreamDataRecv:
    """Test Client::onStreamDataRecv."""

    msg_spec = msgspec.client.onStreamDataRecv
    # Произвольные бинарные данные
    data = b"\x03\x02\x05\x00\x01\x02\x03\x04\x05"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_stream_data_recv(self):
        """Тест для Client::onStreamDataRecv."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnStreamDataRecvMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnImportClientEntityDef:
    """Test Client::onImportClientEntityDef."""

    msg_spec = msgspec.client.onImportClientEntityDef
    data = b"\x07\x02\xae\x0b#\x00\x01\x00UINT8\x00ENTITY_SUBSTATE\x00\x02\x00UINT16\x00UINT16\x00\x03\x00UINT64\x00UID\x00\x04\x00UINT32\x00ENTITY_UTYPE\x00\x05\x00INT8\x00ENTITY_STATE\x00\x06\x00INT16\x00INT16\x00\x07\x00INT32\x00ENTITY_FORBIDS\x00\x08\x00INT64\x00INT64\x00\t\x00STRING\x00STRING\x00\n\x00UNICODE\x00UNICODE\x00\x0b\x00FLOAT\x00FLOAT\x00\x0c\x00DOUBLE\x00DOUBLE\x00\r\x00PYTHON\x00UID1\x00\x0e\x00PY_DICT\x00PY_DICT\x00\x0f\x00PY_TUPLE\x00PY_TUPLE\x00\x10\x00PY_LIST\x00PY_LIST\x00\x11\x00ENTITYCALL\x00ENTITYCALL\x00\x12\x00BLOB\x00BLOB\x00\x13\x00VECTOR2\x00VECTOR2\x00\x14\x00VECTOR3\x00DIRECTION3D\x00\x15\x00VECTOR4\x00VECTOR4\x00\x16\x00ARRAY\x00ENTITY_FORBID_COUNTER\x00\x05\x00\x17\x00ARRAY\x00ENTITYID_LIST\x00\x07\x00\x18\x00FIXED_DICT\x00AVATAR_DATA\x00\x02AVATAR_DATA.AVATAR_DATA_PICKLER\x00param1\x00\x05\x00param2\x00\x12\x00\x19\x00FIXED_DICT\x00AVATAR_INFOS\x00\x05AVATAR_INFOS.avatar_info_inst\x00dbid\x00\x03\x00name\x00\n\x00roleType\x00\x01\x00level\x00\x02\x00data\x00\x18\x00\x1a\x00FIXED_DICT\x00AVATAR_INFOS_LIST\x00\x01AVATAR_INFOS.AVATAR_INFOS_LIST_PICKLER\x00values\x00\x1b\x00\x1b\x00ARRAY\x00_AVATAR_INFOS_LIST_values_ArrayType\x00\x19\x00\x1c\x00FIXED_DICT\x00BAG\x00\x01\x00values22\x00\x1d\x00\x1d\x00ARRAY\x00_BAG_values22_ArrayType\x00\x1e\x00\x1e\x00ARRAY\x00__BAG_values22_ArrayType_ArrayType\x00\x08\x00\x1f\x00FIXED_DICT\x00EXAMPLES\x00\x02\x00k1\x00\x08\x00k2\x00\x08\x00 \x00ARRAY\x00\x00\x07\x00!\x00ENTITY_COMPONENT\x00\x00\"\x00ENTITY_COMPONENT\x00\x00#\x00ENTITY_COMPONENT\x00\x00Account\x00\x01\x00\x04\x00\x03\x00\x05\x00\x00\x00@\x9c\x04\x00\x00\x00\xff\xffposition\x00\x00\x14\x00A\x9c\x04\x00\x00\x00\xff\xffdirection\x00\x00\x14\x00B\x9c\x02\x00\x00\x00\xff\xffspaceID\x00\x00\x04\x00\x02\x00 \x00\x00\x00\xff\xfflastSelCharacter\x000\x00\x03\x00\x15'\xff\xffonCreateAvatarResult\x00\x02\x01\x00\x19\x00\x03\x00\xff\xffonRemoveAvatar\x00\x01\x03\x00\x13'\xff\xffonReqAvatarList\x00\x01\x1a\x00\x11'\xff\xffreqAvatarList\x00\x00\x12'\xff\xffreqCreateAvatar\x00\x02\x01\x00\n\x00\x01\x00\xff\xffreqRemoveAvatar\x00\x01\n\x00\x02\x00\xff\xffreqRemoveAvatarDBID\x00\x01\x03\x00\x14'\xff\xffselectAvatarGame\x00\x01\x03\x00Avatar\x00\x02\x00\x16\x00\x07\x00\x00\x00\x05\x00@\x9c\x04\x00\x00\x00\xff\xffposition\x00\x00\x14\x00A\x9c\x04\x00\x00\x00\xff\xffdirection\x00\x00\x14\x00B\x9c\x02\x00\x00\x00\xff\xffspaceID\x00\x00\x04\x00\x99\xb7\x04\x00\x00\x00\xff\xffHP\x000\x00\x07\x00\x9a\xb7\x04\x00\x00\x00\xff\xffHP_Max\x000\x00\x07\x00\x9b\xb7\x04\x00\x00\x00\xff\xffMP\x000\x00\x07\x00\x9c\xb7\x04\x00\x00\x00\xff\xffMP_Max\x000\x00\x07\x00\x10\x00\xfd\x00\x00\x00\xff\xffcomponent1\x00\x00!\x00\x15\x00a\x00\x00\x00\xff\xffcomponent2\x00\x00\"\x00\x16\x00\x9d\x00\x00\x00\xff\xffcomponent3\x00\x00#\x00\x9d\xb7\x04\x00\x00\x00\xff\xffforbids\x000\x00\x07\x00*\xa0\x08\x00\x00\x00\xff\xfflevel\x00\x00\x02\x00.\xa0\x04\x00\x00\x00\xff\xffmodelID\x000\x00\x04\x00/\xa0\x04\x00\x00\x00\xff\xffmodelScale\x0030\x00\x01\x00\x0b\x00\x04\x00\x00\x00\xff\xffmoveSpeed\x0050\x00\x01\x00+\xa0\x04\x00\x00\x00\xff\xffname\x00\x00\n\x00\x06\x00\x10\x00\x00\x00\xff\xffown_val\x00\x00\x02\x00)\xa0\x08\x00\x00\x00\xff\xffspaceUType\x00\x00\x04\x00\x9e\xb7\x04\x00\x00\x00\xff\xffstate\x000\x00\x05\x00\x9f\xb7\x04\x00\x00\x00\xff\xffsubState\x00\x00\x01\x00,\xa0\x04\x00\x00\x00\xff\xffuid\x000\x00\x04\x00-\xa0\x04\x00\x00\x00\xff\xffutype\x000\x00\x04\x00u'\xff\xffdialog_addOption\x00\x04\x01\x00\x04\x00\n\x00\x07\x00x'\xff\xffdialog_close\x00\x00v'\xff\xffdialog_setText\x00\x04\n\x00\x01\x00\x04\x00\n\x00\x0c\x00\xff\xffonAddSkill\x00\x01\x07\x00\x07\x00\xff\xffonJump\x00\x00\r\x00\xff\xffonRemoveSkill\x00\x01\x07\x00\x10\x00\xff\xffrecvDamage\x00\x04\x07\x00\x07\x00\x07\x00\x07\x00\xfb*\xff\xffdialog\x00\x02\x07\x00\x04\x00\x05\x00\xff\xffjump\x00\x00\x04\x00\xff\xffrelive\x00\x01\x01\x00\x0b\x00\xff\xffrequestPull\x00\x00\xf9*\xff\xffuseTargetSkill\x00\x02\x07\x00\x07\x00Test\x00\x03\x00\x05\x00\x01\x00\x01\x00\x01\x00@\x9c\x04\x00\x00\x00\xff\xffposition\x00\x00\x14\x00A\x9c\x04\x00\x00\x00\xff\xffdirection\x00\x00\x14\x00B\x9c\x02\x00\x00\x00\xff\xffspaceID\x00\x00\x04\x00\x12\x00\x08\x00\x00\x00\xff\xffown\x001001\x00\x07\x00\x11\x00\x04\x00\x00\x00\xff\xffstate\x00100\x00\x07\x00\x1c\x00\xff\xffhelloCB\x00\x01\x07\x00\x1b\x00\xff\xffsay\x00\x01\x07\x00\x1a\x00\xff\xffhello\x00\x01\x07\x00TestNoBase\x00\x04\x00\x05\x00\x01\x00\x00\x00\x01\x00@\x9c\x04\x00\x00\x00\xff\xffposition\x00\x00\x14\x00A\x9c\x04\x00\x00\x00\xff\xffdirection\x00\x00\x14\x00B\x9c\x02\x00\x00\x00\xff\xffspaceID\x00\x00\x04\x00\x18\x00\x08\x00\x00\x00\xff\xffown\x001001\x00\x07\x00\x17\x00\x04\x00\x00\x00\xff\xffstate\x00100\x00\x07\x00\x1e\x00\xff\xffhelloCB\x00\x01\x07\x00\x1d\x00\xff\xffhello\x00\x01\x07\x00Monster\x00\x05\x00\x11\x00\x01\x00\x00\x00\x00\x00@\x9c\x04\x00\x00\x00\xff\xffposition\x00\x00\x14\x00A\x9c\x04\x00\x00\x00\xff\xffdirection\x00\x00\x14\x00B\x9c\x02\x00\x00\x00\xff\xffspaceID\x00\x00\x04\x00\x99\xb7\x04\x00\x00\x00\xff\xffHP\x000\x00\x07\x00\x9a\xb7\x04\x00\x00\x00\xff\xffHP_Max\x000\x00\x07\x00\x9b\xb7\x04\x00\x00\x00\xff\xffMP\x000\x00\x07\x00\x9c\xb7\x04\x00\x00\x00\xff\xffMP_Max\x000\x00\x07\x00?\xc7\x04\x00\x00\x00\xff\xffentityNO\x000\x00\x04\x00\x9d\xb7\x04\x00\x00\x00\xff\xffforbids\x000\x00\x07\x00.\xa0\x04\x00\x00\x00\xff\xffmodelID\x000\x00\x04\x00/\xa0\x04\x00\x00\x00\xff\xffmodelScale\x0030\x00\x01\x00 \x00\x04\x00\x00\x00\xff\xffmoveSpeed\x0050\x00\x01\x00+\xa0\x04\x00\x00\x00\xff\xffname\x00\x00\n\x00\x9e\xb7\x04\x00\x00\x00\xff\xffstate\x000\x00\x05\x00\x9f\xb7\x04\x00\x00\x00\xff\xffsubState\x00\x00\x01\x00,\xa0\x04\x00\x00\x00\xff\xffuid\x000\x00\x04\x00-\xa0\x04\x00\x00\x00\xff\xffutype\x000\x00\x04\x00\"\x00\xff\xffrecvDamage\x00\x04\x07\x00\x07\x00\x07\x00\x07\x00NPC\x00\x06\x00\n\x00\x00\x00\x00\x00\x00\x00@\x9c\x04\x00\x00\x00\xff\xffposition\x00\x00\x14\x00A\x9c\x04\x00\x00\x00\xff\xffdirection\x00\x00\x14\x00B\x9c\x02\x00\x00\x00\xff\xffspaceID\x00\x00\x04\x00?\xc7\x04\x00\x00\x00\xff\xffentityNO\x000\x00\x04\x00.\xa0\x04\x00\x00\x00\xff\xffmodelID\x000\x00\x04\x00/\xa0\x04\x00\x00\x00\xff\xffmodelScale\x0030\x00\x01\x00+\x00\x04\x00\x00\x00\xff\xffmoveSpeed\x0050\x00\x01\x00+\xa0\x04\x00\x00\x00\xff\xffname\x00\x00\n\x00,\xa0\x04\x00\x00\x00\xff\xffuid\x000\x00\x04\x00-\xa0\x04\x00\x00\x00\xff\xffutype\x000\x00\x04\x00Gate\x00\x07\x00\t\x00\x00\x00\x00\x00\x00\x00@\x9c\x04\x00\x00\x00\xff\xffposition\x00\x00\x14\x00A\x9c\x04\x00\x00\x00\xff\xffdirection\x00\x00\x14\x00B\x9c\x02\x00\x00\x00\xff\xffspaceID\x00\x00\x04\x00?\xc7\x04\x00\x00\x00\xff\xffentityNO\x000\x00\x04\x00.\xa0\x04\x00\x00\x00\xff\xffmodelID\x000\x00\x04\x00/\xa0\x04\x00\x00\x00\xff\xffmodelScale\x0030\x00\x01\x00+\xa0\x04\x00\x00\x00\xff\xffname\x00\x00\n\x00,\xa0\x04\x00\x00\x00\xff\xffuid\x000\x00\x04\x00-\xa0\x04\x00\x00\x00\xff\xffutype\x000\x00\x04\x00"

    def test_on_import_client_entity_def(self):
        """Тест для Client::onImportClientEntityDef."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnImportClientEntityDefMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id

        assert len(res.result.entities) == 7
        assert len(res.result.types) == 35


class TestOnEntityLeaveSpace:
    """Test Client::onEntityLeaveSpace."""

    msg_spec = msgspec.client.onEntityLeaveSpace
    # INT32: 1500
    data = b"\xfe\x01\x04\x00\xdc\x05\x00\x00"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_entity_leave_space(self):
        """Тест для Client::onEntityLeaveSpace."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnEntityLeaveSpaceMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnKicked:
    """Test Client::onKicked."""

    msg_spec = msgspec.client.onKicked
    # UINT16: 0x0400 (4) - ServerError.ENTITYDEFS_NOT_MATCH
    data = b"\x05\x02\x02\x00\x04\x00"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_kicked(self):
        """Тест для Client::onKicked."""
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"
        assert not data_tail

        res = OnKickedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id
