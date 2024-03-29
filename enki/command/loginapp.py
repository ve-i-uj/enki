"""Commands for sending messages to LoginApp."""

from __future__ import annotations
import logging
from typing import List
from dataclasses import dataclass

from enki import settings
from enki.core import kbeenum
from enki.core import msgspec
from enki.core.kbeenum import ServerError
from enki.core import kbetype
from enki.handler.clienthandler import OnLoginSuccessfullyHandler
from enki.net.client import MsgTCPClient
from enki.core.message import Message, MsgDescr


from . import _base

logger = logging.getLogger(__name__)


@dataclass
class HelloCommandResultData:
    kbe_version: str
    script_version: str
    protocol_md5: str
    entity_def_md5: str
    component_type: int


@dataclass
class HelloCommandResult(_base.CommandResult):
    success: bool
    result: HelloCommandResultData
    text: str = ''


class HelloCommand(_base.TCPCommand):
    """LoginApp command 'hello'."""

    def __init__(self, kbe_version: str, script_version: str, encrypted_key: bytes,
                 client: MsgTCPClient):
        super().__init__(client)

        self._req_msg_spec = msgspec.app.loginapp.hello
        self._success_resp_msg_spec = msgspec.app.client.onHelloCB
        self._error_resp_msg_specs = [
            msgspec.app.client.onVersionNotMatch,
            msgspec.app.client.onScriptVersionNotMatch,
        ]

        self._msg = Message(
            spec=self._req_msg_spec,
            fields=(kbe_version, script_version, encrypted_key)
        )

    async def execute(self) -> _base.CommandResult:
        await self._client.send_msg(self._msg)
        resp_msg = await self._waiting_for(settings.WAITING_FOR_SERVER_TIMEOUT)
        if resp_msg is None:
            return _base.CommandResult(False, text=self.get_timeout_err_text())

        if resp_msg.id == msgspec.app.client.onVersionNotMatch.id:
            kbe_version = self._msg.get_values()[0]
            data: memoryview = resp_msg.get_values()[0]
            actual_kbe_version, offset = kbetype.STRING.decode(data)
            data = data[offset:]
            msg = f'Plugin designed for KBEngine version "{kbe_version}". ' \
                  f'But actual KBEngine version is "{actual_kbe_version}"'
            return _base.CommandResult(False, msg)

        if resp_msg.id == msgspec.app.client.onScriptVersionNotMatch.id:
            script_version = self._msg.get_values()[1]
            data: memoryview = resp_msg.get_values()[0]
            actual_script_version, offset = kbetype.STRING.decode(data)
            data = data[offset:]
            msg = f'Plugin designed for script version "{script_version}". ' \
                  f'But actual script version is "{actual_script_version}"'
            return _base.CommandResult(False, msg)

        return _base.CommandResult(
            True, HelloCommandResultData(*resp_msg.get_values()), ''
        )


@dataclass
class LoginCommandResultData:
    ret_code: ServerError
    account_name: str = ''
    host: str = ''
    tcp_port: int = 0
    udp_port: int = 0
    data: bytes = b''


@dataclass
class LoginCommandResult(_base.CommandResult):
    """Result of command 'login'."""
    success: bool
    result: LoginCommandResultData
    text: str = ''


class LoginCommand(_base.TCPCommand):
    """LoginApp command 'login'."""

    def __init__(self, client_type: kbeenum.ClientType, client_data: bytes,
                 account_name: str, password: str, force_login: bool,
                 client: MsgTCPClient):
        super().__init__(client)

        self._req_msg_spec: MsgDescr = msgspec.app.loginapp.login
        self._success_resp_msg_spec: MsgDescr = msgspec.app.client.onLoginSuccessfully
        self._error_resp_msg_specs: List[MsgDescr] = [
            msgspec.app.client.onLoginFailed,
        ]

        self._msg = Message(
            spec=self._req_msg_spec,
            fields=(client_type.value, client_data, account_name, password,
                    '' if not force_login else force_login)
        )

    async def execute(self) -> LoginCommandResult:
        await self._client.send_msg(self._msg)
        resp_msg = await self._waiting_for(settings.WAITING_FOR_SERVER_TIMEOUT)
        if resp_msg is None:
            return LoginCommandResult(
                False,
                LoginCommandResultData(kbeenum.ServerError.MAX),
                self.get_timeout_err_text()
            )

        if resp_msg.id == msgspec.app.client.onLoginFailed.id:
            data: memoryview = resp_msg.get_values()[0]
            err_code, offset = kbetype.SERVER_ERROR.decode(data)
            data = data[offset:]
            _user_data, offset = kbetype.BLOB.decode(data)
            data = data[offset:]
            return LoginCommandResult(
                False,
                LoginCommandResultData(kbeenum.ServerError(err_code)),
                str(kbeenum.ServerError(err_code))
            )

        handler = OnLoginSuccessfullyHandler()
        res = handler.handle(resp_msg)

        pd = res.result
        res_data = LoginCommandResultData(
            ServerError.SUCCESS, pd.account_name, pd.host, pd.tcp_port,
            pd.udp_port, pd.data
        )

        return LoginCommandResult(True, res_data)


@dataclass
class ImportClientMessagesParsedData:
    data: memoryview


class ImportClientMessagesCommandResult(_base.CommandResult):
    success: bool
    result: ImportClientMessagesParsedData
    text: str = ''


class ImportClientMessagesCommand(_base.TCPCommand):
    """LoginApp command 'importClientMessages'."""

    def __init__(self, client: MsgTCPClient):
        super().__init__(client)

        self._req_msg_spec: MsgDescr = msgspec.app.loginapp.importClientMessages
        self._success_resp_msg_spec: MsgDescr = msgspec.app.client.onImportClientMessages
        self._error_resp_msg_specs: List[MsgDescr] = []

        self._msg = Message(spec=self._req_msg_spec, fields=tuple())

    async def execute(self) -> ImportClientMessagesCommandResult:
        await self._client.send_msg(self._msg)
        resp_msg = await self._waiting_for(settings.WAITING_FOR_SERVER_TIMEOUT)
        if resp_msg is None:
            return ImportClientMessagesCommandResult(
                False, text=self.get_timeout_err_text()
            )

        data: memoryview = resp_msg.get_values()[0]
        return ImportClientMessagesCommandResult(
            True, ImportClientMessagesParsedData(data)
        )


class ImportServerErrorsDescrCommand(_base.TCPCommand):
    """LoginApp command 'importServerErrorsDescr'."""

    def __init__(self, client: MsgTCPClient):
        super().__init__(client)

        self._req_msg_spec = msgspec.app.loginapp.importServerErrorsDescr
        self._success_resp_msg_spec = msgspec.app.client.onImportServerErrorsDescr
        self._error_resp_msg_specs = []

        self._msg = Message(spec=self._req_msg_spec, fields=tuple())

    async def execute(self) -> memoryview:
        await self._client.send_msg(self._msg)
        resp_msg = await self._waiting_for(settings.WAITING_FOR_SERVER_TIMEOUT)
        assert resp_msg is not None
        data = resp_msg.get_values()[0]
        return data


@dataclass
class ReqAccountResetPasswordCommandResultData:
    code: ServerError = ServerError.MAX


@dataclass
class ReqAccountResetPasswordCommandResult(_base.CommandResult):
    success: bool
    result: ReqAccountResetPasswordCommandResultData = ReqAccountResetPasswordCommandResultData()
    text: str


class ReqAccountResetPasswordCommand(_base.TCPCommand):
    """LoginApp command 'reqAccountResetPassword'."""

    def __init__(self, client: MsgTCPClient, account_name: str):
        super().__init__(client)
        self._account_name = account_name

        self._req_msg_spec = msgspec.app.loginapp.reqAccountResetPassword
        self._success_resp_msg_spec = msgspec.app.client.onReqAccountResetPasswordCB
        self._error_resp_msg_specs = []

    async def execute(self) -> ReqAccountResetPasswordCommandResult:
        msg = Message(self._req_msg_spec, (self._account_name, ))
        await self._client.send_msg(msg)
        resp_msg = await self._waiting_for(settings.WAITING_FOR_SERVER_TIMEOUT)
        if resp_msg is None:
            return ReqAccountResetPasswordCommandResult(False, text=self.get_timeout_err_text())

        ret_code: int = resp_msg.get_values()[0]
        code = ServerError(ret_code)
        if code != ServerError.SUCCESS:
            return ReqAccountResetPasswordCommandResult(False, text=code.name)

        return ReqAccountResetPasswordCommandResult(
            True, ReqAccountResetPasswordCommandResultData(code)
        )


class OnClientActiveTickCommand(_base.TCPCommand):
    """LoginAPp command 'onClientActiveTick'."""

    def __init__(self, client: MsgTCPClient, timeout: float = 0.0):
        super().__init__(client)

        self._req_msg_spec: MsgDescr = msgspec.app.loginapp.onClientActiveTick
        self._success_resp_msg_spec: MsgDescr = msgspec.app.client.onAppActiveTickCB
        self._error_resp_msg_specs: List[MsgDescr] = []

        self._timeout = timeout

    async def execute(self) -> _base.CommandResult:
        msg = Message(spec=self._req_msg_spec, fields=tuple())
        await self._client.send_msg(msg)
        resp_msg = await self._waiting_for(self._timeout)
        if resp_msg is None:
            return _base.CommandResult(
                False, f'No response for the "{self._req_msg_spec.name}"'
            )

        return _base.CommandResult(True)


@dataclass
class ReqCreateAccountCommandResultData:
    code: ServerError = ServerError.MAX


@dataclass
class ReqCreateAccountCommandResult(_base.CommandResult):
    success: bool
    result: ReqCreateAccountCommandResultData
    text: str


class ReqCreateAccountCommand(_base.TCPCommand):
    """LoginAPp command 'reqCreateAccount'."""

    def __init__(self, client: MsgTCPClient, account_name: str, password: str, data: bytes):
        super().__init__(client)
        self._account_name = account_name
        self._password = password
        self._data = data

        self._req_msg_spec = msgspec.app.loginapp.reqCreateAccount
        self._success_resp_msg_spec = msgspec.app.client.onCreateAccountResult
        self._error_resp_msg_specs = []

    async def execute(self) -> ReqCreateAccountCommandResult:
        msg = Message(
            spec=self._req_msg_spec,
            fields=(self._account_name, self._password, self._data)
        )
        await self._client.send_msg(msg)
        resp_msg = await self._waiting_for()
        if resp_msg is None:
            return ReqCreateAccountCommandResult(False, text=self.get_timeout_err_text())

        data: memoryview = resp_msg.get_values()[0]
        ret_code, offset = kbetype.UINT16.decode(data)
        data = data[offset:]
        code = ServerError(ret_code)
        if code != ServerError.SUCCESS:
            return ReqCreateAccountCommandResult(
                False, ReqCreateAccountCommandResultData(code),str(code)
            )

        return ReqCreateAccountCommandResult(
            True,
            ReqCreateAccountCommandResultData(code)
        )


class ReqCreateMailAccountCommand(ReqCreateAccountCommand):
    """LoginAPp command 'reqCreateMailAccount'."""

    def __init__(self, client: MsgTCPClient, account_name: str, password: str, data: bytes):
        super().__init__(client, account_name, password, data)

        self._req_msg_spec = msgspec.app.loginapp.reqCreateMailAccount


@dataclass
class ImportClientSDKCommandResultData:
    pending_files_number: int
    file_name: str
    data_size: int
    data: memoryview


@dataclass
class ImportClientSDKCommandResult(_base.CommandResult):
    success: bool
    result: ImportClientSDKCommandResultData
    text: str


class ImportClientSDKCommand(_base.TCPCommand):
    _TIMEOUT = 5 * settings.SECOND

    def __init__(self, client: MsgTCPClient, options: str, chunk_size: int,
                 cb_host: str, cb_port: int):
        super().__init__(client)
        self._options = options
        self._chunk_size = chunk_size
        self._cb_host = cb_host
        self._cb_port = cb_port

        self._req_msg_spec: MsgDescr = msgspec.app.loginapp.importClientSDK
        self._success_resp_msg_spec: MsgDescr = msgspec.app.client.onImportClientSDK
        self._error_resp_msg_specs: List[MsgDescr] = []

    async def execute(self) -> ImportClientSDKCommandResult:
        msg = Message(
            spec=self._req_msg_spec,
            fields=(self._options, self._chunk_size, self._cb_host, self._cb_port)
        )
        await self._client.send_msg(msg)
        resp_msg = await self._waiting_for(self._TIMEOUT)
        if resp_msg is None:
            return ImportClientSDKCommandResult(False, text=self.get_timeout_err_text())

        data: memoryview = resp_msg.get_values()[0]
        pending_files, offset = kbetype.INT32.decode(data)
        data = data[offset:]
        file_name, offset = kbetype.STRING.decode(data)
        data = data[offset:]
        data_size, offset = kbetype.INT32.decode(data)
        data = data[offset:]

        return ImportClientSDKCommandResult(
            True,
            ImportClientSDKCommandResultData(
                pending_files, file_name, data_size, data
            )
        )
