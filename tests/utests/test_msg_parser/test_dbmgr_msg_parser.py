"""Тесты на парсинг сообщений от компонента DBMgr."""

import pytest

from enki import msgspec
from enki.kbeenum import AccountType, ClientType, ComponentType, ServerError
from enki.msg.msg_serializer import MessageSerializer
from enki.msg_parser.dbmgr_msg_parser import (
    AccountActivateMsgParser,
    AccountBindMailMsgParser,
    AccountNewPasswordMsgParser,
    AccountReqBindMailMsgParser,
    AccountReqResetPasswordMsgParser,
    AccountResetPasswordMsgParser,
    ChargeMsgParser,
    DeleteEntityByDBIDMsgParser,
    EntityAutoLoadMsgParser,
    EraseClientReqMsgParser,
    ExecuteRawDatabaseCommandMsgParser,
    LookAppMsgParser,
    LookUpEntityByDBIDMsgParser,
    OnAccountLoginMsgParser,
    OnAccountOnlineMsgParser,
    OnAppActiveTickMsgParser,
    OnBroadcastGlobalDataChangedMsgParser,
    OnChargeCBMsgParser,
    OnCreateAccountCBFromInterfacesMsgParser,
    OnEntityOfflineMsgParser,
    OnLoginAccountCBBFromInterfacesMsgParser,
    OnLookAppMsgParser,
    OnRegisterNewAppMsgParser,
    OnReqAllocEntityIDMsgParser,
    QueryAccountMsgParser,
    QueryEntityMsgParser,
    QueryLoadMsgParser,
    QueryWatcherMsgParser,
    RemoveEntityMsgParser,
    ReqCreateAccountMsgParser,
    ReqKillServerMsgParser,
    StartProfileMsgParser,
    SyncEntityStreamTemplateMsgParser,
    WriteEntityMsgParser,
)
from enki.msgspec import DBMgrMsgSpecByID


class TestDBMgr_lookApp:
    """Тесты сообщения Dbmgr::lookApp."""

    msg_spec = msgspec.dbmgr.lookApp
    data = b"\t\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = LookAppMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestDBMgr_onLookApp:
    """Тесты сообщения Dbmgr::onLookApp."""

    msg_spec = msgspec.dbmgr.onLookApp
    data = b"\x01\x00\x00\x00\xa1\x0f\x00\x00\x00\x00\x00\x00\x01"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize_only_data(self.data, self.msg_spec.id)
        assert msg is not None
        assert not data_tail

        result = OnLookAppMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        pd = result.result
        assert pd.componentType == 1
        assert pd.componentId == 4001
        assert pd.shutdownState == 1


class TestDBMgr_queryLoad:
    """Тесты сообщения Dbmgr::queryLoad."""

    msg_spec = msgspec.dbmgr.queryLoad
    data = b"\n\x00\x00\x00"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = QueryLoadMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        assert result.msg_id == self.msg_spec.id
        assert result.text == ""


class TestDBMgr_onReqAllocEntityID:
    """Тесты сообщения Dbmgr::onReqAllocEntityID."""

    msg_spec = msgspec.dbmgr.onReqAllocEntityID
    data = b"\x0b\x00\x02\x00\x05\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = OnReqAllocEntityIDMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        assert result.msg_id == self.msg_spec.id
        pd = result.result
        assert pd.componentType == 5  # CELLAPP
        assert pd.componentID == 0
        assert pd.component_type == ComponentType.CELLAPP


class TestDBMgr_reqCreateAccount:
    """Тесты сообщения Dbmgr::reqCreateAccount."""

    msg_spec = msgspec.dbmgr.reqCreateAccount
    data = b"\r\x00 \x00user@example.com\x00\x00\x02\t\x00\x00\x00test_data"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = ReqCreateAccountMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        assert result.msg_id == self.msg_spec.id
        pd = result.result
        assert pd.account_name == "user@example.com"
        assert pd.password == ""
        assert pd.accountType == 2
        assert pd.account_type == AccountType.MAIL
        assert pd.datas == b"test_data"


class TestDbmgr_onCreateAccountCBFromInterfaces:
    """Тесты сообщения Dbmgr::onCreateAccountCBFromInterfaces."""

    msg_spec = msgspec.dbmgr.onCreateAccountCBFromInterfaces
    data = b"\x0e\x003\x00)#\x00\x00\x00\x00\x00\x00NBkMtOWSbD\x00NBkMtOWSbD\x00rfrbeb843O\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = OnCreateAccountCBFromInterfacesMsgParser().parse(msg)

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
        assert pd.component_id == 9001
        assert pd.registerName == "NBkMtOWSbD"
        assert pd.realAccountName == "NBkMtOWSbD"
        assert pd.password == "rfrbeb843O"
        assert pd.retcode == 0
        assert pd.datas == b""


class TestDBMgr_queryAccount:
    """Тесты сообщения Dbmgr::queryAccount."""

    msg_spec = msgspec.dbmgr.queryAccount
    data = b"\x11\x001\x00DVtAgSqtaq\x00EOvxwgjKBJ\x00\x01A\x1f\x00\x00\x00\x00\x00\x00\xd3\x07\x00\x00\x07\x00\x00\x00\x00\x00\x00\x00\xac\x12\x00\x01\x81\x12"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = QueryAccountMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        assert result.msg_id == self.msg_spec.id
        pd = result.result
        assert pd.accountName == "DVtAgSqtaq"
        assert pd.password == "EOvxwgjKBJ"
        assert pd.needCheckPassword == 1
        assert pd.componentID == 8001
        assert pd.entityID == 2003
        assert pd.entityDBID == 7
        assert pd.ip == 16781996
        assert pd.port == 4737


class TestDBMgr_onAccountOnline:
    """Тесты сообщения Dbmgr::onAccountOnline."""

    msg_spec = msgspec.dbmgr.onAccountOnline
    data = b"\x12\x00\x18\x00testuser\x00)#\x00\x00\x00\x00\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = OnAccountOnlineMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        assert result.msg_id == self.msg_spec.id
        pd = result.result
        assert pd.account_name == "testuser"
        assert pd.component_id == 9001
        assert pd.entity_id == 0


class TestDBMgr_onEntityOffline:
    """Тесты сообщения Dbmgr::onEntityOffline."""

    msg_spec = msgspec.dbmgr.onEntityOffline
    data = b"\x13\x00\x07\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = OnEntityOfflineMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        assert result.msg_id == self.msg_spec.id
        pd = result.result
        assert pd.dbid == 7
        assert pd.sid == 1
        assert pd.dbInterfaceIndex == 0


class TestDBMgr_eraseClientReq:
    """Тесты сообщения Dbmgr::eraseClientReq."""

    msg_spec = msgspec.dbmgr.eraseClientReq
    data = b"\x14\x00\r\x00test_logkey\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = EraseClientReqMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        assert result.msg_id == self.msg_spec.id
        pd = result.result
        assert pd.logkey == "test_logkey"


class TestDBMgr_executeRawDatabaseCommand:
    """Тесты сообщения Dbmgr::executeRawDatabaseCommand."""

    msg_spec = msgspec.dbmgr.executeRawDatabaseCommand
    data = b"\x15\x00\x1f\x00\x00\x00\x00\x00\x00)#\x00\x05\x01\x00\x00\x00SELECT * FROM table\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = ExecuteRawDatabaseCommandMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        assert result.msg_id == self.msg_spec.id
        pd = result.result
        assert pd.entity_id == 0
        assert pd.dbInterfaceIndex == 0
        assert pd.component_id == 9001
        assert pd.componentType == 5  # CELLAPP
        assert pd.callback_id == 1
        assert pd.row_sql == b"SELECT * FROM table"
        assert pd.component_type_enum == ComponentType.CELLAPP


class TestDBMgr_writeEntity:
    """Тесты сообщения Dbmgr::writeEntity."""

    msg_spec = msgspec.dbmgr.writeEntity
    data = b"\x16\x001\x00A\x1f\x00\x00\x00\x00\x00\x00\xd3\x07\x00\x00\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\xff\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = WriteEntityMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        assert result.msg_id == self.msg_spec.id
        pd = result.result
        assert pd.componentID == 8001
        assert pd.entity_id == 2003
        assert pd.entity_db_id == 7
        assert pd.dbInterfaceIndex == 0
        assert pd.sid == 1
        assert pd.callback_id == 0
        assert pd.shouldAutoLoad == 0
        assert pd.ip == 65536
        assert pd.port == 0
        assert pd.data == b"\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00"


class TestDBMgr_removeEntity:
    """Тесты сообщения Dbmgr::removeEntity."""

    msg_spec = msgspec.dbmgr.removeEntity
    data = b"\x17\x00\x1f\x00\x00)#\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00entity_data\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = RemoveEntityMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        assert result.msg_id == self.msg_spec.id
        pd = result.result
        assert pd.dbInterfaceIndex == 0
        assert pd.componentID == 9001
        assert pd.entity_id == 0
        assert pd.entity_db_id == 0
        assert pd.sid == 1
        assert pd.data == b"entity_data"


class TestDBMgr_deleteEntityByDBID:
    """Тесты сообщения Dbmgr::deleteEntityByDBID."""

    msg_spec = msgspec.dbmgr.deleteEntityByDBID
    data = b"\x18\x00\x16\x00\x00)#\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = DeleteEntityByDBIDMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        assert result.msg_id == self.msg_spec.id
        pd = result.result
        assert pd.dbInterfaceIndex == 0
        assert pd.componentID == 9001
        assert pd.entity_db_id == 0
        assert pd.callback_id == 1
        assert pd.sid == 1


class TestDBMgr_lookUpEntityByDBID:
    """Тесты сообщения Dbmgr::lookUpEntityByDBID."""

    msg_spec = msgspec.dbmgr.lookUpEntityByDBID
    data = b"\x19\x00\x16\x00\x00)#\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = LookUpEntityByDBIDMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        assert result.msg_id == self.msg_spec.id
        pd = result.result
        assert pd.dbInterfaceIndex == 0
        assert pd.componentID == 9001
        assert pd.entity_db_id == 0
        assert pd.callback_id == 1
        assert pd.sid == 1


class TestDBMgr_queryEntity:
    """Тесты сообщения Dbmgr::queryEntity."""

    msg_spec = msgspec.dbmgr.queryEntity
    data = b"\x1b\x00-\x00\x00)#\x00\x00\x00\x00\x00\x00\x00\x00\x00TestEntity\x00\x01\x00\x00\x00\x00\x00\x00\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = QueryEntityMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        assert result.msg_id == self.msg_spec.id
        pd = result.result
        assert pd.dbInterfaceIndex == 0
        assert pd.componentID == 9001
        assert pd.queryMode == 0
        assert pd.entity_db_id == 0
        assert pd.entityType == "TestEntity"
        assert pd.callback_id == 1
        assert pd.entity_id == 0


class TestDBMgr_charge:
    """Тесты сообщения Dbmgr::charge."""

    msg_spec = msgspec.dbmgr.charge
    data = b"\x1e\x00$\x00charge123\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = ChargeMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        assert result.msg_id == self.msg_spec.id
        pd = result.result
        assert pd.chargeID == "charge123"
        assert pd.dbid == 0
        assert pd.data == b""
        assert pd.callback_id == 1


class TestDBMgr_onChargeCB:
    """Тесты сообщения Dbmgr::onChargeCB."""

    msg_spec = msgspec.dbmgr.onChargeCB
    data = b"\x1f\x00.\x00)#\x00charge123\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = OnChargeCBMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        assert result.msg_id == self.msg_spec.id
        pd = result.result
        assert pd.baseappID == 9001
        assert pd.order_id == "charge123"
        assert pd.dbid == 0
        assert pd.extraDatas == b""
        assert pd.cbid == 1
        assert pd.errorCode == 0
        assert pd.error_code_enum == ServerError.SUCCESS


class TestDBMgr_accountActivate:
    """Тесты сообщения Dbmgr::accountActivate."""

    msg_spec = msgspec.dbmgr.accountActivate
    data = b" \x00\r\x00activate123\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = AccountActivateMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        assert result.msg_id == self.msg_spec.id
        pd = result.result
        assert pd.scode == "activate123"


class TestDBMgr_accountReqResetPassword:
    """Тесты сообщения Dbmgr::accountReqResetPassword."""

    msg_spec = msgspec.dbmgr.accountReqResetPassword
    data = b"!\x00\r\x00testuser\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = AccountReqResetPasswordMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        assert result.msg_id == self.msg_spec.id
        pd = result.result
        assert pd.accountName == "testuser"


class TestDBMgr_accountResetPassword:
    """Тесты сообщения Dbmgr::accountResetPassword."""

    msg_spec = msgspec.dbmgr.accountResetPassword
    data = b'"\x00$\x00testuser\x00newpass123\x00code123\x00'

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = AccountResetPasswordMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        assert result.msg_id == self.msg_spec.id
        pd = result.result
        assert pd.accountName == "testuser"
        assert pd.newpassword == "newpass123"
        assert pd.code == "code123"


class TestDBMgr_accountReqBindMail:
    """Тесты сообщения Dbmgr::accountReqBindMail."""

    msg_spec = msgspec.dbmgr.accountReqBindMail
    data = b"#\x003\x00\x00\x00\x00\x00testuser\x00testpass\x00test@mail.com\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = AccountReqBindMailMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        assert result.msg_id == self.msg_spec.id
        pd = result.result
        assert pd.entityID == 0
        assert pd.accountName == "testuser"
        assert pd.password == "testpass"
        assert pd.email == "test@mail.com"


class TestDBMgr_accountBindMail:
    """Тесты сообщения Dbmgr::accountBindMail."""

    msg_spec = msgspec.dbmgr.accountBindMail
    data = b"$\x00\x19\x00testuser\x00code123\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = AccountBindMailMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        assert result.msg_id == self.msg_spec.id
        pd = result.result
        assert pd.accountName == "testuser"
        assert pd.code == "code123"


class TestDBMgr_accountNewPassword:
    """Тесты сообщения Dbmgr::accountNewPassword."""

    msg_spec = msgspec.dbmgr.accountNewPassword
    data = b"%\x002\x00\x00\x00\x00\x00testuser\x00oldpass\x00newpass\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = AccountNewPasswordMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        assert result.msg_id == self.msg_spec.id
        pd = result.result
        assert pd.entity_id == 0
        assert pd.accountName == "testuser"
        assert pd.password == "oldpass"
        assert pd.newPassword == "newpass"


class TestDBMgr_startProfile:
    """Тесты сообщения Dbmgr::startProfile."""

    msg_spec = msgspec.dbmgr.startProfile
    data = b"&\x00\x18\x00test_profile\x00\x01\x00\x00\x00\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = StartProfileMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        assert result.msg_id == self.msg_spec.id
        pd = result.result
        assert pd.profileName == "test_profile"
        assert pd.profileType == 1
        assert pd.timelen == 0


class TestDBMgr_reqKillServer:
    """Тесты сообщения Dbmgr::reqKillServer."""

    msg_spec = msgspec.dbmgr.reqKillServer
    data = b"'\x00.\x00)#\x00\x05root\x00\x00\x00\x00\x00reason_text\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = ReqKillServerMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        assert result.msg_id == self.msg_spec.id
        pd = result.result
        assert pd.component_id == 9001
        assert pd.componentType == 5  # CELLAPP
        assert pd.username == "root"
        assert pd.uid == 0
        assert pd.reason == "reason_text"
        assert pd.component_type_enum == ComponentType.CELLAPP


class TestDBMgr_queryWatcher:
    """Тесты сообщения Dbmgr::queryWatcher."""

    msg_spec = msgspec.dbmgr.queryWatcher
    data = b"n\xa0\x00\x00\r\x00/watcher/path\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = QueryWatcherMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        assert result.msg_id == self.msg_spec.id
        pd = result.result
        assert pd.path == "/watcher/path"


class TestDBMgr_onAppActiveTick:
    """Тесты сообщения Dbmgr::onAppActiveTick."""

    msg_spec = msgspec.dbmgr.onAppActiveTick
    data = b"A\xd7\x02\x00\x00\x00)#\x00\x00\x00\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
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

        pd = result.result
        assert pd.componentType == 2
        assert pd.componentID == 9001


class TestDBMgr_onRegisterNewApp:
    """Тесты сообщения Dbmgr::onRegisterNewApp."""

    msg_spec = msgspec.dbmgr.onRegisterNewApp
    data = b"\x08\x00*\x00\xe8\x03\x00\x00root\x00\x04\x00\x00\x00\x89\x13\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xac\x12\x00\x07\xcd\xc7\x00\x00\x00\x00\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
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
        assert pd.componentType == 4
        assert pd.componentID == 5001
        assert pd.globalorderID == -1
        assert pd.grouporderID == -1
        assert pd.intaddr == 117445292
        assert pd.intport == 51149
        assert pd.extaddr == 0
        assert pd.extport == 0
        assert pd.extaddrEx == ""


class TestDBMgr_onBroadcastGlobalDataChanged:
    """Тесты сообщения Dbmgr::onBroadcastGlobalDataChanged."""

    data = b"\x0e\x00F\x00\x00\r\x00\x00\x00Vspace_1\np0\n.0\x00\x00\x00c_upf\nEntityCall\np0\n(I2002\nI7001\nI9\nI1\ntp1\nRp2\n."
    msg_spec = msgspec.dbmgr.onBroadcastGlobalDataChanged

    @pytest.mark.skip("Случайные данные")
    def test_success_with_value(self):
        """Удачный парсинг сообщения с данными."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnBroadcastGlobalDataChangedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        assert res.msg_id == self.msg_spec.id
        assert (
            res.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )

        pd = res.result
        assert not pd.isDelete
        assert pd.key == "space_1"
        assert pd.value is not None


class TestDBMgr_syncEntityStreamTemplate:
    """Тесты сообщения Dbmgr::syncEntityStreamTemplate."""

    msg_spec = msgspec.dbmgr.syncEntityStreamTemplate
    data = b"\x1d\x00\x14\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = SyncEntityStreamTemplateMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        pd = result.result
        assert (
            pd.data
            == b"\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        )


class TestDBMgr_entityAutoLoad:
    """Тесты сообщения Dbmgr::entityAutoLoad."""

    msg_spec = msgspec.dbmgr.entityAutoLoad
    data = b"\x1c\x00\x14\x00\x00\x00Y\x1b\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00 \x00\x00\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

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
    """Тесты сообщения Dbmgr::onAccountLogin."""

    msg_spec = msgspec.dbmgr.onAccountLogin
    data = b"\x0f\x00\x1a\x00mbLYLNYIDF\x00hKjiTCXJSp\x00\x00\x00\x00\x00"

    def test_onAccountLogin(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
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
        assert pd.login == "mbLYLNYIDF"
        assert pd.password == "hKjiTCXJSp"
        assert pd.data == b""


class TestDBMgr_onLoginAccountCBBFromInterfaces:
    """Тесты сообщения Dbmgr::onLoginAccountCBBFromInterfaces."""

    msg_spec = msgspec.dbmgr.onLoginAccountCBBFromInterfaces
    data = b"\x10\x00I\x00)#\x00\x00\x00\x00\x00\x00DVtAgSqtaq\x00DVtAgSqtaq\x00EOvxwgjKBJ\x00#\x00\x0b\x00\x00\x00client_data\x0b\x00\x00\x00client_data"

    def test_onLoginAccountCBBFromInterfaces(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

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
        assert pd.login == "DVtAgSqtaq"
        assert pd.account_name == "DVtAgSqtaq"
        assert pd.password == "EOvxwgjKBJ"
        assert pd.component_id == 9001
        assert pd.retCode == 35
        assert pd.ret_code == ServerError.LOCAL_PROCESSING
        assert pd.postdatas == b"client_data"
        assert pd.getdatas == b"client_data"
