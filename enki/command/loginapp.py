"""Commands for sending messages to LoginApp."""

from __future__ import annotations
import logging
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass

from enki import settings
from enki import descr, kbeenum, kbeclient, exception, dcdescr, kbetype
from enki.interface import IClient, IMessage
from enki.kbeenum import ServerError

from . import _base

logger = logging.getLogger(__name__)


class HelloCommand(_base.Command):
    """LoginApp command 'hello'."""

    def __init__(self, kbe_version: str, script_version: str, encrypted_key: bytes,
                 client: kbeclient.Client):
        super().__init__(client)

        self._req_msg_spec = descr.app.loginapp.hello
        self._success_resp_msg_spec = descr.app.client.onHelloCB
        self._error_resp_msg_specs = [
            descr.app.client.onVersionNotMatch,
            descr.app.client.onScriptVersionNotMatch,
        ]

        self._msg = kbeclient.Message(
            spec=self._req_msg_spec,
            fields=(kbe_version, script_version, encrypted_key)
        )

    async def execute(self) -> _base.CommandResult:
        await self._client.send(self._msg)
        resp_msg = await self._waiting_for(settings.WAITING_FOR_SERVER_TIMEOUT)
        if resp_msg is None:
            return _base.CommandResult(False, text=self.get_timeout_err_text())

        if resp_msg.id == descr.app.client.onVersionNotMatch.id:
            kbe_version = self._msg.get_values()[0]
            data: memoryview = resp_msg.get_values()[0]
            actual_kbe_version, offset = kbetype.STRING.decode(data)
            data = data[offset:]
            msg = f'Plugin designed for KBEngine version "{kbe_version}". ' \
                  f'But actual KBEngine version is "{actual_kbe_version}"'
            return _base.CommandResult(False, msg)

        if resp_msg.id == descr.app.client.onScriptVersionNotMatch.id:
            script_version = self._msg.get_values()[1]
            data: memoryview = resp_msg.get_values()[0]
            actual_script_version, offset = kbetype.STRING.decode(data)
            data = data[offset:]
            msg = f'Plugin designed for script version "{script_version}". ' \
                  f'But actual script version is "{actual_script_version}"'
            return _base.CommandResult(False, msg)

        return _base.CommandResult(True, '')


@dataclass
class LoginCommandResultData:
    ret_code: kbeenum.ServerError
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


class LoginCommand(_base.Command):
    """LoginApp command 'login'."""

    def __init__(self, client_type: kbeenum.ClientType, client_data: bytes,
                 account_name: str, password: str, force_login: bool,
                 client: kbeclient.Client):
        super().__init__(client)

        self._req_msg_spec: dcdescr.MessageDescr = descr.app.loginapp.login
        self._success_resp_msg_spec: dcdescr.MessageDescr = descr.app.client.onLoginSuccessfully
        self._error_resp_msg_specs: List[dcdescr.MessageDescr] = [
            descr.app.client.onLoginFailed,
        ]

        self._msg = kbeclient.Message(
            spec=self._req_msg_spec,
            fields=(client_type.value, client_data, account_name, password,
                    '' if not force_login else force_login)
        )

    async def execute(self) -> LoginCommandResult:
        await self._client.send(self._msg)
        resp_msg = await self._waiting_for(settings.WAITING_FOR_SERVER_TIMEOUT)
        if resp_msg is None:
            return LoginCommandResult(
                False,
                LoginCommandResultData(kbeenum.ServerError.MAX),
                self.get_timeout_err_text()
            )

        if resp_msg.id == descr.app.client.onLoginFailed.id:
            data: memoryview = resp_msg.get_values()[0]
            err_code, offset = kbetype.SERVER_ERROR.decode(data)
            data = data[offset:]
            _user_data, offset = kbetype.BLOB.decode(data)
            data = data[offset:]
            return LoginCommandResult(
                False,
                LoginCommandResultData(kbeenum.ServerError(err_code)),
                kbeenum.ServerError(err_code).name
            )

        res_data = LoginCommandResultData(ServerError.SUCCESS)
        data: memoryview = resp_msg.get_values()[0]
        res_data.account_name, offset = kbetype.STRING.decode(data)
        data = data[offset:]
        res_data.host, offset = kbetype.STRING.decode(data)
        data = data[offset:]
        res_data.tcp_port, offset = kbetype.UINT16.decode(data)
        data = data[offset:]
        res_data.udp_port, offset = kbetype.UINT16.decode(data)
        data = data[offset:]
        res_data.data, offset = kbetype.BLOB.decode(data)
        data = data[offset:]

        return LoginCommandResult(True, res_data)


class ImportClientMessagesCommand(_base.Command):
    """LoginApp command 'importClientMessages'."""

    def __init__(self, client: kbeclient.Client):
        super().__init__(client)

        self._req_msg_spec: dcdescr.MessageDescr = descr.app.loginapp.importClientMessages
        self._success_resp_msg_spec: dcdescr.MessageDescr = descr.app.client.onImportClientMessages
        self._error_resp_msg_specs: List[dcdescr.MessageDescr] = []

        self._msg = kbeclient.Message(spec=self._req_msg_spec, fields=tuple())

    async def execute(self) -> bytes:
        await self._client.send(self._msg)
        resp_msg = await self._waiting_for(settings.WAITING_FOR_SERVER_TIMEOUT)
        if resp_msg is None:
            raise exception.StopClientException()
        data = resp_msg.get_values()[0]
        return data


class ImportServerErrorsDescrCommand(_base.Command):
    """LoginApp command 'importServerErrorsDescr'."""

    def __init__(self, client: IClient):
        super().__init__(client)

        self._req_msg_spec = descr.app.loginapp.importServerErrorsDescr
        self._success_resp_msg_spec = descr.app.client.onImportServerErrorsDescr
        self._error_resp_msg_specs = []

        self._msg = kbeclient.Message(spec=self._req_msg_spec, fields=tuple())

    async def execute(self) -> memoryview:
        await self._client.send(self._msg)
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


class ReqAccountResetPasswordCommand(_base.Command):
    """LoginApp command 'reqAccountResetPassword'."""

    def __init__(self, client: IClient, account_name: str):
        super().__init__(client)
        self._account_name = account_name

        self._req_msg_spec = descr.app.loginapp.reqAccountResetPassword
        self._success_resp_msg_spec = descr.app.client.onReqAccountResetPasswordCB
        self._error_resp_msg_specs = []

    async def execute(self) -> ReqAccountResetPasswordCommandResult:
        msg = kbeclient.Message(self._req_msg_spec, (self._account_name, ))
        await self._client.send(msg)
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


class OnClientActiveTickCommand(_base.Command):
    """LoginAPp command 'onClientActiveTick'."""

    def __init__(self, client: IClient, timeout: float = 0.0):
        super().__init__(client)

        self._req_msg_spec: dcdescr.MessageDescr = descr.app.loginapp.onClientActiveTick
        self._success_resp_msg_spec: dcdescr.MessageDescr = descr.app.client.onAppActiveTickCB
        self._error_resp_msg_specs: List[dcdescr.MessageDescr] = []

        self._timeout = timeout

    async def execute(self) -> _base.CommandResult:
        msg = kbeclient.Message(spec=self._req_msg_spec, fields=tuple())
        await self._client.send(msg)
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


class ReqCreateAccountCommand(_base.Command):
    """LoginAPp command 'reqCreateAccount'."""

    def __init__(self, client: IClient, account_name: str, password: str, data: bytes):
        super().__init__(client)
        self._account_name = account_name
        self._password = password
        self._data = data

        self._req_msg_spec = descr.app.loginapp.reqCreateAccount
        self._success_resp_msg_spec = descr.app.client.onCreateAccountResult
        self._error_resp_msg_specs = []

    async def execute(self) -> ReqCreateAccountCommandResult:
        msg = kbeclient.Message(
            spec=self._req_msg_spec,
            fields=(self._account_name, self._password, self._data)
        )
        await self._client.send(msg)
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

    def __init__(self, client: IClient, account_name: str, password: str, data: bytes):
        super().__init__(client, account_name, password, data)

        self._req_msg_spec = descr.app.loginapp.reqCreateMailAccount


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


class ImportClientSDKCommand(_base.Command):
    _TIMEOUT = 5 * settings.SECOND

    def __init__(self, client: IClient, options: str, chunk_size: int,
                 cb_host: str, cb_port: int):
        super().__init__(client)
        self._options = options
        self._chunk_size = chunk_size
        self._cb_host = cb_host
        self._cb_port = cb_port

        self._req_msg_spec: dcdescr.MessageDescr = descr.app.loginapp.importClientSDK
        self._success_resp_msg_spec: dcdescr.MessageDescr = descr.app.client.onImportClientSDK
        self._error_resp_msg_specs: List[dcdescr.MessageDescr] = []

    async def execute(self) -> ImportClientSDKCommandResult:
        msg = kbeclient.Message(
            spec=self._req_msg_spec,
            fields=(self._options, self._chunk_size, self._cb_host, self._cb_port)
        )
        await self._client.send(msg)
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
