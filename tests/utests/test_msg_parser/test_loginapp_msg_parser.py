"""Тесты для парсеров собщений компонента Loginapp."""

import pytest

from enki import msgspec
from enki.kbeenum import ClientType, ServerError
from enki.msg.msg_serializer import MessageSerializer
from enki.msg_parser.loginapp_msg_parser import (
    HelloMsgParser,
    ImportClientMessagesMsgParser,
    ImportClientSDKMsgParser,
    ImportServerErrorsDescrMsgParser,
    LoginMsgParser,
    LookAppMsgParser,
    OnAccountActivatedMsgParser,
    OnAccountBindedEmailMsgParser,
    OnAccountResetPasswordMsgParser,
    OnAppActiveTickMsgParser,
    OnBaseappInitProgressMsgParser,
    OnClientActiveTickMsgParser,
    OnDbmgrInitCompletedMsgParser,
    OnLoginAccountQueryBaseappAddrFromBaseappmgrMsgParser,
    OnLoginAccountQueryResultFromDbmgrMsgParser,
    OnLookAppMsgParser,
    OnReqAccountBindEmailAllocCallbackLoginappMsgParser,
    OnReqAccountResetPasswordCBMsgParser,
    OnReqCreateAccountResultMsgParser,
    OnReqCreateMailAccountResultMsgParser,
    QueryLoadMsgParser,
    QueryWatcherMsgParser,
    ReqAccountResetPasswordMsgParser,
    ReqCloseMsgParser,
    ReqCloseServerMsgParser,
    ReqCreateAccountMsgParser,
    ReqCreateMailAccountMsgParser,
    ReqKillServerMsgParser,
    StartProfileMsgParser,
)
from enki.msgspec import LoginappMsgSpecByID


class TestOnDbmgrInitCompletedTestCase:
    data = b"\x0e\x00)\x00\x05\x00\x00\x00\x01\x00\x00\x0006E15F102B481ACF8CA19E2F410D1B64\x00"
    msg_spec = msgspec.loginapp.onDbmgrInitCompleted

    def test_onDbmgrInitCompleted(self):
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

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

        assert pd.startID == 1
        assert pd.endID == 826619440
        assert pd.startGlobalOrder == 808535605
        assert pd.startGroupOrder == 942948914
        assert pd.digest == "1ACF8CA19E2F410D1B64"


class TestLoginapp_onBaseappInitProgress:
    """Тесты сообщения Loginapp::onBaseappInitProgress."""

    msg_spec = msgspec.loginapp.onBaseappInitProgress
    data = b"\x18\x00\x00\x00\xc8B"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = OnBaseappInitProgressMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        pd = result.result
        assert pd.progress == 100.0


class TestOnAppActiveTick:
    """Тесты для Loginapp::onAppActiveTick."""

    data = b"B\xd7\n\x00\x00\x00\xd1\x07\x00\x00\x00\x00\x00\x00"
    msg_spec = msgspec.loginapp.onAppActiveTick

    def test_OnAppActiveTickHandler(self):
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnAppActiveTickMsgParser().parse(msg)

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

        assert pd.componentType == 10
        assert pd.componentID == 2001


class TestLoginappHello:
    """Тест парсинга сообщения Loginapp::hello."""

    data = b"\x04\x00\x11\x002.5.10\x000.1.0\x00\x00\x00\x00\x00"
    msg_spec = msgspec.loginapp.hello

    def test_hello(self):
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = HelloMsgParser().parse(msg)

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

        assert pd.kbe_version == "2.5.10"
        assert pd.script_version == "0.1.0"
        assert pd.encrypted_key == b""


class TestLoginappLogin:
    """Тест парсинга сообщения Loginapp::login."""

    data = b"\x03\x00!\x00\x00\x00\x00\x00\x00ACCOUNT_NAME\x00PASSWORD\x00False\x00"
    msg_spec = msgspec.loginapp.login

    def test_login(self):
        """Тест парсинга сообщения."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = LoginMsgParser().parse(msg)

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

        assert pd.client_type == ClientType.UNKNOWN
        assert pd.clientData == b""
        assert pd.accountName == "ACCOUNT_NAME"
        assert pd.password == "PASSWORD"
        assert pd.force_login is False


class Test_OnLoginAccountQueryResultFromDbmgr:
    """Тест парсинга сообщения Loginapp::onLoginAccountQueryResultFromDbmgr."""

    data = b"\x0f\x00H\x00\x00\x00mbLYLNYIDF\x00mbLYLNYIDF\x00hKjiTCXJSp\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    msg_spec = msgspec.loginapp.onLoginAccountQueryResultFromDbmgr

    def test_login(self):
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnLoginAccountQueryResultFromDbmgrMsgParser().parse(msg)

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

        assert pd.ret_code == ServerError.SUCCESS
        assert pd.login == "mbLYLNYIDF"
        assert pd.account_name == "mbLYLNYIDF"
        assert pd.password == "hKjiTCXJSp"
        assert pd.needCheckPassword == 1
        assert pd.componentID == 0
        assert pd.entitiy_id == 0
        assert pd.db_id == 1
        assert pd.flags == 0
        assert pd.deadline == 0
        assert pd.data == ""


class TestLoginapp_onLoginAccountQueryBaseappAddrFromBaseappmgr:
    """Тесты сообщения Loginapp::onLoginAccountQueryBaseappAddrFromBaseappmgr."""

    msg_spec = msgspec.loginapp.onLoginAccountQueryBaseappAddrFromBaseappmgr
    data = b"\x10\x00\x10\x001\x001\x000.0.0.0\x00N/N%"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = OnLoginAccountQueryBaseappAddrFromBaseappmgrMsgParser().parse(
            msg
        )

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        pd = result.result
        assert pd.loginName == "1"
        assert pd.accountName == "1"
        assert pd.addr == "0.0.0.0"
        assert pd.tcp_port == 12110
        assert pd.udp_port == 9550


class TestLoginapp_onLookApp:
    """Тесты сообщения Loginapp::onLookApp."""

    msg_spec = msgspec.loginapp.onLookApp
    data = b"\x02\x00\x00\x00)#\x00\x00\x00\x00\x00\x00\x01"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
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
        assert pd.componentType == 2
        assert pd.componentId == 9001
        assert pd.shutdownState == 1


class TestLoginapp_lookApp:
    """Тесты сообщения Loginapp::lookApp."""

    msg_spec = msgspec.loginapp.lookApp
    data = b"\t\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = LookAppMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        # Сообщение пустое


class TestReqClose:
    """Test Loginapp::reqClose."""

    msg_spec = msgspec.loginapp.reqClose
    # Сообщение без данных (пустые аргументы)
    data = b"\x01\x00\x00\x00"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_req_close(self):
        """Тест для Loginapp::reqClose."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = ReqCloseMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestReqCreateAccount:
    """Test Loginapp::reqCreateAccount."""

    msg_spec = msgspec.loginapp.reqCreateAccount
    # account_name, password, client_data
    data = b"\x02\x00\x12\x00test_account\x00password123\x00\x00\x00\x00\x00"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_req_create_account(self):
        """Тест для Loginapp::reqCreateAccount."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = ReqCreateAccountMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestReqCreateMailAccount:
    """Test Loginapp::reqCreateMailAccount."""

    msg_spec = msgspec.loginapp.reqCreateMailAccount
    # account_name, password, client_data
    data = b"\x06\x00\x12\x00test_mail\x00password456\x00\x00\x00\x00\x00"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_req_create_mail_account(self):
        """Тест для Loginapp::reqCreateMailAccount."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = ReqCreateMailAccountMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestImportClientMessages:
    """Test Loginapp::importClientMessages."""

    msg_spec = msgspec.loginapp.importClientMessages
    # Сообщение без данных
    data = b"\x05\x00\x00\x00"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_import_client_messages(self):
        """Тест для Loginapp::importClientMessages."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = ImportClientMessagesMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestImportClientSDK:
    """Test Loginapp::importClientSDK."""

    msg_spec = msgspec.loginapp.importClientSDK
    # options, clientWindowSize, callbackIP, callbackPort
    data = (
        b"\x07\x00\x1a\x00test_options\x00\x00\x00\x00\x00127.0.0.1\x00\x11\x27"
    )

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_import_client_sdk(self):
        """Тест для Loginapp::importClientSDK."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = ImportClientSDKMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestImportServerErrorsDescr:
    """Test Loginapp::importServerErrorsDescr."""

    msg_spec = msgspec.loginapp.importServerErrorsDescr
    # Сообщение без данных
    data = b"\x08\x00\x00\x00"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_import_server_errors_descr(self):
        """Тест для Loginapp::importServerErrorsDescr."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = ImportServerErrorsDescrMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnClientActiveTick:
    """Test Loginapp::onClientActiveTick."""

    msg_spec = msgspec.loginapp.onClientActiveTick
    # Сообщение без данных
    data = b"\x0b\x00\x00\x00"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_client_active_tick(self):
        """Тест для Loginapp::onClientActiveTick."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = OnClientActiveTickMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestReqAccountResetPassword:
    """Test Loginapp::reqAccountResetPassword."""

    msg_spec = msgspec.loginapp.reqAccountResetPassword
    # account_name
    data = b"\x0c\x00\x0c\x00test_account\x00"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_req_account_reset_password(self):
        """Тест для Loginapp::reqAccountResetPassword."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = ReqAccountResetPasswordMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestOnReqAccountResetPasswordCB:
    """Test Loginapp::onReqAccountResetPasswordCB."""

    msg_spec = msgspec.loginapp.onReqAccountResetPasswordCB
    # account_name, email, failedcode, code
    data = (
        b"\r\x00\x1e\x00test_account\x00test@email.com\x00\x01\x00code123\x00"
    )

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_req_account_reset_password_cb(self):
        """Тест для Loginapp::onReqAccountResetPasswordCB."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = OnReqAccountResetPasswordCBMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id
        assert res.result.ret_code == ServerError.SUCCESS


class TestOnReqCreateAccountResult:
    """Test Loginapp::onReqCreateAccountResult."""

    msg_spec = msgspec.loginapp.onReqCreateAccountResult
    # failedcode, register_name, password, getdatas
    data = b"\x11\x00\x1a\x00\x01\x00new_user\x00pass123\x00data\x00"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_req_create_account_result(self):
        """Тест для Loginapp::onReqCreateAccountResult."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = OnReqCreateAccountResultMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id
        assert res.result.ret_code == ServerError.SUCCESS


class TestOnReqCreateMailAccountResult:
    """Test Loginapp::onReqCreateMailAccountResult."""

    msg_spec = msgspec.loginapp.onReqCreateMailAccountResult
    # failedcode, register_name, password, getdatas
    data = b"\x12\x00\x1b\x00\x01\x00mail_user\x00mailpass\x00maildata\x00"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_req_create_mail_account_result(self):
        """Тест для Loginapp::onReqCreateMailAccountResult."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = OnReqCreateMailAccountResultMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id
        assert res.result.ret_code == ServerError.SUCCESS


class TestOnAccountActivated:
    """Test Loginapp::onAccountActivated."""

    msg_spec = msgspec.loginapp.onAccountActivated
    # code, success
    data = b"\x13\x00\x0b\x00ACT123\x00\x01"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_account_activated(self):
        """Тест для Loginapp::onAccountActivated."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = OnAccountActivatedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id
        assert res.result.success is True


class TestOnAccountBindedEmail:
    """Test Loginapp::onAccountBindedEmail."""

    msg_spec = msgspec.loginapp.onAccountBindedEmail
    # code, success
    data = b"\x14\x00\x0b\x00BIND456\x00\x01"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_account_binded_email(self):
        """Тест для Loginapp::onAccountBindedEmail."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = OnAccountBindedEmailMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id
        assert res.result.success is True


class TestOnAccountResetPassword:
    """Test Loginapp::onAccountResetPassword."""

    msg_spec = msgspec.loginapp.onAccountResetPassword
    # code, success
    data = b"\x15\x00\x0c\x00RESET789\x00\x01"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_account_reset_password(self):
        """Тест для Loginapp::onAccountResetPassword."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = OnAccountResetPasswordMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id
        assert res.result.success is True


class TestOnReqAccountBindEmailAllocCallbackLoginapp:
    """Test Loginapp::onReqAccountBindEmailAllocCallbackLoginapp."""

    msg_spec = msgspec.loginapp.onReqAccountBindEmailAllocCallbackLoginapp
    # reqBaseappID, entityID, accountName, email, failedcode, code
    data = b"\x16\x00.\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00user123\x00email@test.com\x00\x01\x00CODE123\x00"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_on_req_account_bind_email_alloc_callback_loginapp(self):
        """Тест для Loginapp::onReqAccountBindEmailAllocCallbackLoginapp."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = OnReqAccountBindEmailAllocCallbackLoginappMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id
        assert res.result.ret_code == ServerError.SUCCESS


class TestReqCloseServer:
    """Test Loginapp::reqCloseServer."""

    msg_spec = msgspec.loginapp.reqCloseServer
    # Сообщение без данных
    data = b"\x17\x00\x00\x00"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_req_close_server(self):
        """Тест для Loginapp::reqCloseServer."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = ReqCloseServerMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestQueryLoad:
    """Test Loginapp::queryLoad."""

    msg_spec = msgspec.loginapp.queryLoad
    # Сообщение без данных
    data = b"\n\x00\x00\x00"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_query_load(self):
        """Тест для Loginapp::queryLoad."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = QueryLoadMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestStartProfile:
    """Test Loginapp::startProfile."""

    msg_spec = msgspec.loginapp.startProfile
    # profileName, profileType, timelen
    data = b"\x19\x00\x15\x00test_profile\x00\x01\x00\x00\x00\x00"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_start_profile(self):
        """Тест для Loginapp::startProfile."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = StartProfileMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestReqKillServer:
    """Test Loginapp::reqKillServer."""

    msg_spec = msgspec.loginapp.reqKillServer
    # component_id, componentType, username, uid, reason
    data = b"\x1a\x00*\x00\x00\x00\x00\x00\x01\x00admin\x00\x01\x00\x00\x00shutdown\x00"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_req_kill_server(self):
        """Тест для Loginapp::reqKillServer."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = ReqKillServerMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestQueryWatcher:
    """Test Loginapp::queryWatcher."""

    msg_spec = msgspec.loginapp.queryWatcher
    # path
    data = b"\x8b\xa0\x00\x00\x0f\x00/components/loginapp\x00"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_query_watcher(self):
        """Тест для Loginapp::queryWatcher."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = QueryWatcherMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id


class TestLoginapp_onDbmgrInitCompleted:
    """Тесты сообщения Loginapp::onDbmgrInitCompleted."""

    msg_spec = msgspec.loginapp.onDbmgrInitCompleted
    data = b"\x0e\x00)\x00\x03\x00\x00\x00\x01\x00\x00\x0006E15F102B481ACF8CA19E2F410D1B64\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = OnDbmgrInitCompletedMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        pd = result.result
        assert pd.gametime == 3
        assert pd.startID == 1
        assert pd.endID == 826619440
        assert pd.startGlobalOrder == 808535605
        assert pd.startGroupOrder == 942948914
        assert pd.digest == "1ACF8CA19E2F410D1B64"
