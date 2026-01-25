"""Тесты на парсинг сообщений от компонента Baseapp."""

import pytest

from enki import msgspec
from enki.kbeenum import ClientType
from enki.msg.msg_serializer import MessageSerializer
from enki.msg_parser.baseapp_msg_parser import (
    HelloMsgParser,
    ImportClientEntityDefMsgParser,
    ImportClientMessagesMsgParser,
    LoginBaseappMsgParser,
    LogoutBaseappMsgParser,
    LookAppMsgParser,
    OnAppActiveTickMsgParser,
    OnBackupEntityCellDataMsgParser,
    OnBroadcastBaseAppDataChangedMsgParser,
    OnBroadcastGlobalDataChangedMsgParser,
    OnClientActiveTickMsgParser,
    OnCreateCellFailureMsgParser,
    OnCreateEntityAnywhereCallbackMsgParser,
    OnCreateEntityAnywhereMsgParser,
    OnCreateEntityRemotelyCallbackMsgParser,
    OnCreateEntityRemotelyMsgParser,
    OnDbmgrInitCompletedMsgParser,
    OnEntityAutoLoadCBFromDBMgrMsgParser,
    OnEntityCallMsgParser,
    OnEntityGetCellMsgParser,
    OnExecScriptCommandMsgParser,
    OnGetEntityAppFromDbmgrMsgParser,
    OnLookAppMsgParser,
    OnQueryAccountCBFromDbmgrMsgParser,
    OnRegisterNewAppMsgParser,
    OnRemoteCallCellMethodFromClientMsgParser,
    OnRemoteMethodCallMsgParser,
    OnReqAllocEntityIDMsgParser,
    OnUpdateDataFromClientForControlledEntityMsgParser,
    OnUpdateDataFromClientMsgParser,
    OnWriteToDBCallbackMsgParser,
    QueryLoadMsgParser,
    RegisterPendingLoginMsgParser,
    ReloginBaseappMsgParser,
    ReqAccountBindEmailMsgParser,
    ReqAccountNewPasswordMsgParser,
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


class TestBaseapp_OnDbmgrInitCompleted:
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


class TestBaseapp_OnEntityAutoLoadCBFromDBMgr:
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


class TestBaseapp_OnBroadcastGlobalDataChanged:
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


class TestBaseapp_OnEntityGetCell:
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
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

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


class Test_onLookApp:
    msg_spec = msgspec.baseapp.onLookApp
    data = b"\x06\x00\x00\x00A\x1f\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00@\x9c\x00\x00"

    def test_onLookApp(self):
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize_only_data(
            self.data, msgspec.baseapp.onLookApp.id
        )
        assert msg is not None
        assert not data_tail

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
        assert res.msg_id == msgspec.baseapp.onLookApp.id

        pd = res.result

        assert pd.componentType == 6
        assert pd.componentId == 8001
        assert pd.shutdownState == 1
        assert pd.entitiesSize == 0
        assert pd.numClients == 0
        assert pd.numProxices == 0
        assert pd.port == 40000


class Test_onBackupEntityCellData:
    """Тесты для парсера Baseapp::onBackupEntityCellData."""

    msg_spec = msgspec.baseapp.onBackupEntityCellData

    # Пример данных сообщения - нужно заменить на реальные данные
    # Структура: KBERowByteData
    data = b"\x0b\x00*\x00\xe8\x03\x00\x00\x01\x02\x03\x04\x05"  # Пример байтовых данных

    @pytest.mark.skip("Случайные данные")
    def test_onBackupEntityCellData_parser(self):
        """Тест парсера Baseapp::onBackupEntityCellData."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))

        assert msg is not None
        assert not data_tail

        res = OnBackupEntityCellDataMsgParser().parse(msg)

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

        # Проверка специфичных данных
        assert res.msg_id == msgspec.baseapp.onBackupEntityCellData.id
        pd = res.result

        # Проверка KBERowByteData
        assert pd.data is not None


class Test_onWriteToDBCallback:
    msg_spec = msgspec.baseapp.onWriteToDBCallback
    data = b"$\x00\xd3\x07\x00\x00\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01"

    def test_onWriteToDBCallback(self):
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

        res = OnWriteToDBCallbackMsgParser().parse(msg)

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
        assert res.msg_id == msgspec.baseapp.onWriteToDBCallback.id

        pd = res.result

        assert pd.entity_id == 2003
        assert pd.entityDBID == 7
        assert pd.dbInterfaceIndex == 0
        assert pd.callbackID == 0
        assert pd.success_int == 1

        assert pd.success is True


class TestBaseapp_Hello:
    """Тесты сообщения Baseapp::hello."""

    msg_spec = msgspec.baseapp.hello
    data = b"\xc8\x00\x11\x002.5.10\x000.1.0\x00\x00\x00\x00\x00"

    def test_hello(self):
        """Удачный парсинг сообщения hello."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = HelloMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id
        assert (
            res.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            res.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )

        pd = res.result
        assert pd.server_version == "2.5.10"
        assert pd.assets_version == "0.1.0"
        assert pd.encrypted_key == b""


class TestBaseapp_ImportClientMessages:
    """Тесты сообщения Baseapp::importClientMessages."""

    msg_spec = msgspec.baseapp.importClientMessages
    data = b"\xcf\x00"  # ID сообщения 207, длина 0

    def test_importClientMessages(self):
        """Удачный парсинг сообщения importClientMessages."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = ImportClientMessagesMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestBaseapp_ImportClientEntityDef:
    """Тесты сообщения Baseapp::importClientEntityDef."""

    msg_spec = msgspec.baseapp.importClientEntityDef
    data = b"\xd0\x00"  # ID сообщения 208, длина 0

    def test_importClientEntityDef(self):
        """Удачный парсинг сообщения importClientEntityDef."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = ImportClientEntityDefMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestBaseapp_LoginBaseapp:
    """Тесты сообщения Baseapp::loginBaseapp."""

    msg_spec = msgspec.baseapp.loginBaseapp
    # Формат: account_name (строка), password (строка)
    data = b"\xca\x00\x16\x00WzYCoozMVJ\x00shHXMwyfle\x00"

    def test_loginBaseapp(self):
        """Удачный парсинг сообщения loginBaseapp."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = LoginBaseappMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id

        pd = res.result
        assert pd.account_name == "WzYCoozMVJ"
        assert pd.password == "shHXMwyfle"


class TestBaseapp_OnClientActiveTick:
    """Тесты сообщения Baseapp::onClientActiveTick."""

    msg_spec = msgspec.baseapp.onClientActiveTick
    data = b"\xce\x00"  # ID сообщения 206, длина 0

    def test_onClientActiveTick(self):
        """Удачный парсинг сообщения onClientActiveTick."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnClientActiveTickMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestBaseapp_OnUpdateDataFromClient:
    """Тесты сообщения Baseapp::onUpdateDataFromClient."""

    msg_spec = msgspec.baseapp.onUpdateDataFromClient
    data = b"\x1b\x00\x19\x00\x00\x00\x80?\x00\x00\x00@\x00\x00@@\x00\x00\x80?\x00\x00\x00@\x00\x00@@\x01\x01\x00\x00\x00"

    @pytest.mark.skip("Случайные данные")
    def test_onUpdateDataFromClient(self):
        """Удачный парсинг сообщения onUpdateDataFromClient."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnUpdateDataFromClientMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id

        pd = res.result
        assert pd.x == 1.0
        assert pd.y == 2.0
        assert pd.z == 3.0
        assert pd.roll == 1.0
        assert pd.pitch == 2.0
        assert pd.yaw == 3.0
        assert pd.isOnGround == 1
        assert pd.spaceID == 1


class TestBaseapp_OnUpdateDataFromClientForControlledEntity:
    """Тесты сообщения Baseapp::onUpdateDataFromClientForControlledEntity."""

    msg_spec = msgspec.baseapp.onUpdateDataFromClientForControlledEntity
    # Формат: entity_id, x, y, z, roll, pitch, yaw (float), isOnGround (bool), spaceID
    data = b"\x1c\x00!\x00\xd2\x07\x00\x00\x00\x00\x80?\x00\x00\x00@\x00\x00@@\x00\x00\x80?\x00\x00\x00@\x00\x00@@\x01\x01\x00\x00\x00"

    def test_onUpdateDataFromClientForControlledEntity(self):
        """Удачный парсинг сообщения onUpdateDataFromClientForControlledEntity."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnUpdateDataFromClientForControlledEntityMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id

        pd = res.result
        assert pd.entity_id == 2002
        assert pd.x == 1.0
        assert pd.y == 2.0
        assert pd.z == 3.0
        assert pd.roll == 1.0
        assert pd.pitch == 2.0
        assert pd.yaw == 3.0
        assert pd.isOnGround == 1
        assert pd.spaceID == 1


class TestBaseapp_LookApp:
    """Тесты сообщения Baseapp::lookApp."""

    msg_spec = msgspec.baseapp.lookApp
    data = b"\x08\x00"  # ID сообщения 8, длина 0 (FIXED тип)

    def test_lookApp(self):
        """Удачный парсинг сообщения lookApp."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = LookAppMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestBaseapp_OnCreateEntityAnywhere:
    """Тесты сообщения Baseapp::onCreateEntityAnywhere."""

    msg_spec = msgspec.baseapp.onCreateEntityAnywhere
    # UINT8_ARRAY данные (пример: тип сущности, позиция и т.д.)
    data = b"\x10\x00\x08\x00\x01\x00\x00\x00\x00\x00\x00\x00"

    @pytest.mark.skip("Случайные данные")
    def test_onCreateEntityAnywhere(self):
        """Удачный парсинг сообщения onCreateEntityAnywhere."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnCreateEntityAnywhereMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestBaseapp_OnCreateEntityAnywhereCallback:
    """Тесты сообщения Baseapp::onCreateEntityAnywhereCallback."""

    msg_spec = msgspec.baseapp.onCreateEntityAnywhereCallback
    # UINT8_ARRAY данные
    data = b"\x11\x00\x08\x00\xd2\x07\x00\x00\x01\x00\x00\x00"

    def test_onCreateEntityAnywhereCallback(self):
        """Удачный парсинг сообщения onCreateEntityAnywhereCallback."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnCreateEntityAnywhereCallbackMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id

        pd = res.result
        assert pd.data is not None


class TestBaseapp_OnBroadcastBaseAppDataChanged:
    """Тесты сообщения Baseapp::onBroadcastBaseAppDataChanged."""

    msg_spec = msgspec.baseapp.onBroadcastBaseAppDataChanged
    # UINT8_ARRAY данные
    data = b"\x0f\x00\x08\x00\x01\x02\x03\x04\x05\x06\x07\x08"

    def test_onBroadcastBaseAppDataChanged(self):
        """Удачный парсинг сообщения onBroadcastBaseAppDataChanged."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnBroadcastBaseAppDataChangedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id

        pd = res.result
        assert pd.data == b"\x01\x02\x03\x04\x05\x06\x07\x08"


class TestBaseapp_OnCreateEntityRemotely:
    """Тесты сообщения Baseapp::onCreateEntityRemotely."""

    msg_spec = msgspec.baseapp.onCreateEntityRemotely
    # UINT8_ARRAY данные
    data = (
        b"\x12\x00\x0c\x00\x01\x00\xd2\x07\x00\x00\x01\x00\x00\x00\x00\x00\x80?"
    )

    @pytest.mark.skip("Случайные данные")
    def test_onCreateEntityRemotely(self):
        """Удачный парсинг сообщения onCreateEntityRemotely."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnCreateEntityRemotelyMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestBaseapp_OnCreateEntityRemotelyCallback:
    """Тесты сообщения Baseapp::onCreateEntityRemotelyCallback."""

    msg_spec = msgspec.baseapp.onCreateEntityRemotelyCallback
    # UINT8_ARRAY данные
    data = b"\x13\x00\x08\x00\xd2\x07\x00\x00\x01\x00\x00\x00"

    def test_onCreateEntityRemotelyCallback(self):
        """Удачный парсинг сообщения onCreateEntityRemotelyCallback."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnCreateEntityRemotelyCallbackMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestBaseapp_OnCreateCellFailure:
    """Тесты сообщения Baseapp::onCreateCellFailure."""

    msg_spec = msgspec.baseapp.onCreateCellFailure
    # UINT8_ARRAY данные
    data = b"\x15\x00\x08\x00\xd2\x07\x00\x00\x01\x00\x00\x00"

    def test_onCreateCellFailure(self):
        """Удачный парсинг сообщения onCreateCellFailure."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnCreateCellFailureMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestBaseapp_OnQueryAccountCBFromDbmgr:
    """Тесты сообщения Baseapp::onQueryAccountCBFromDbmgr."""

    msg_spec = msgspec.baseapp.onQueryAccountCBFromDbmgr
    # UINT8_ARRAY данные
    data = b"\x19\x00L\x00\x00\x00WzYCoozMVJ\x00shHXMwyfle\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x01\xd9\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0b\x00\x00\x00client_data\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

    # @pytest.mark.skip("Случайные данные")
    def test_onQueryAccountCBFromDbmgr(self):
        """Удачный парсинг сообщения onQueryAccountCBFromDbmgr."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnQueryAccountCBFromDbmgrMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestBaseapp_OnEntityCall:
    """Тесты сообщения Baseapp::onEntityCall."""

    msg_spec = msgspec.baseapp.onEntityCall
    # UINT8_ARRAY данные
    data = b"\x1a\x00\x0c\x00\xd2\x07\x00\x00\x01\x00\x00\x00\x00\x00\x80?"

    def test_onEntityCall(self):
        """Удачный парсинг сообщения onEntityCall."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnEntityCallMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestBaseapp_OnRemoteCallCellMethodFromClient:
    """Тесты сообщения Baseapp::onRemoteCallCellMethodFromClient."""

    msg_spec = msgspec.baseapp.onRemoteCallCellMethodFromClient
    # UINT8_ARRAY данные
    data = b"\xcd\x00\x0c\x00\xd2\x07\x00\x00\x01\x00onMethod\x00"

    @pytest.mark.skip("Случайные данные")
    def test_onRemoteCallCellMethodFromClient(self):
        """Удачный парсинг сообщения onRemoteCallCellMethodFromClient."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnRemoteCallCellMethodFromClientMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestBaseapp_ReloginBaseapp:
    """Тесты сообщения Baseapp::reloginBaseapp."""

    msg_spec = msgspec.baseapp.reloginBaseapp
    # Формат: account_name, password, key, entity_id
    data = b"\xcc\x00\x1e\x00test_account\x00test_password\x00\x01\x00\x00\x00\x00\x00\x00\x00\xd2\x07\x00\x00"

    @pytest.mark.skip("Случайные данные")
    def test_reloginBaseapp(self):
        """Удачный парсинг сообщения reloginBaseapp."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = ReloginBaseappMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id

        pd = res.result
        assert pd.account_name == "test_account"
        assert pd.password == "test_password"
        assert pd.key == 1
        assert pd.entity_id == 2002


class TestBaseapp_LogoutBaseapp:
    """Тесты сообщения Baseapp::logoutBaseapp."""

    msg_spec = msgspec.baseapp.logoutBaseapp
    # Формат: key (UINT64), entityID (INT32)
    data = b"\x18\x00\x0c\x00\x01\x00\x00\x00\x00\x00\x00\x00\xd2\x07\x00\x00"

    @pytest.mark.skip("Случайные данные")
    def test_logoutBaseapp(self):
        """Удачный парсинг сообщения logoutBaseapp."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = LogoutBaseappMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id

        pd = res.result
        assert pd.key == 1
        assert pd.entity_id == 2002


class TestBaseapp_ReqAccountBindEmail:
    """Тесты сообщения Baseapp::reqAccountBindEmail."""

    msg_spec = msgspec.baseapp.reqAccountBindEmail
    # Формат: entityID, password, email
    data = b"\x33\x00\x1c\x00\xd2\x07\x00\x00mypassword\x00test@example.com\x00"

    @pytest.mark.skip("Случайные данные")
    def test_reqAccountBindEmail(self):
        """Удачный парсинг сообщения reqAccountBindEmail."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = ReqAccountBindEmailMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id

        pd = res.result
        assert pd.entity_id == 2002
        assert pd.password == "mypassword"
        assert pd.email == "test@example.com"


class TestBaseapp_ReqAccountNewPassword:
    """Тесты сообщения Baseapp::reqAccountNewPassword."""

    msg_spec = msgspec.baseapp.reqAccountNewPassword
    # Формат: entityID, oldpassword, newpassword
    data = b"\x36\x00\x1e\x00\xd2\x07\x00\x00oldpass\x00newpass\x00"

    @pytest.mark.skip("Случайные данные")
    def test_reqAccountNewPassword(self):
        """Удачный парсинг сообщения reqAccountNewPassword."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = ReqAccountNewPasswordMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id

        pd = res.result
        assert pd.entity_id == 2002
        assert pd.oldpassword == "oldpass"
        assert pd.newpassword == "newpass"


class TestBaseapp_OnRemoteMethodCall:
    """Тесты сообщения Entity::onRemoteMethodCall."""

    msg_spec = msgspec.baseapp.onRemoteMethodCall
    # UINT8_ARRAY данные
    data = b"\x2e\x01\x0c\x00\xd2\x07\x00\x00\x01\x00methodName\x00"

    @pytest.mark.skip("Случайные данные")
    def test_onRemoteMethodCall(self):
        """Удачный парсинг сообщения onRemoteMethodCall."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnRemoteMethodCallMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestBaseapp_QueryLoad:
    """Тесты сообщения Baseapp::queryLoad."""

    msg_spec = msgspec.baseapp.queryLoad
    data = b"\t\x00"  # ID сообщения 9, длина 0

    @pytest.mark.skip("Случайные данные")
    def test_queryLoad(self):
        """Удачный парсинг сообщения queryLoad."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = QueryLoadMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestBaseapp_OnExecScriptCommand:
    """Тесты сообщения Baseapp::onExecScriptCommand."""

    msg_spec = msgspec.baseapp.onExecScriptCommand
    # Формат: command (STRING)
    data = b'\xd1\xb9\x01\x0c\x00print("Hello World")\x00'

    @pytest.mark.skip("Случайные данные")
    def test_onExecScriptCommand(self):
        """Удачный парсинг сообщения onExecScriptCommand."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnExecScriptCommandMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id

        pd = res.result
        assert pd.command == 'print("Hello World")'


class TestBaseapp_OnReqAllocEntityID:
    """Тесты сообщения Baseapp::onReqAllocEntityID."""

    msg_spec = msgspec.baseapp.onReqAllocEntityID
    # Формат: count (UINT32)
    data = b"\x0c\x00\x04\x00\x0a\x00\x00\x00"

    @pytest.mark.skip("Случайные данные")
    def test_onReqAllocEntityID(self):
        """Удачный парсинг сообщения onReqAllocEntityID."""
        serializer = MessageSerializer(BaseappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnReqAllocEntityIDMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id

        pd = res.result
        assert pd.count == 10
