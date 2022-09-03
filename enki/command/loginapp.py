"""Commands for sending messages to LoginApp."""

from __future__ import annotations
import logging
from typing import List, Tuple, Optional
from dataclasses import dataclass

from enki import settings
from enki import descr, kbeenum, kbeclient, exception, dcdescr
from enki.interface import IMessage

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
            return _base.CommandResult(False, _base.TIMEOUT_ERROR_MSG)

        if resp_msg.id == descr.app.client.onVersionNotMatch.id:
            kbe_version = self._msg.get_values()[0]
            actual_kbe_version = resp_msg.get_values()[0]
            msg = f'Plugin designed for KBEngine version "{kbe_version}". ' \
                  f'But actual KBEngine version is "{actual_kbe_version}"'
            return _base.CommandResult(False, msg)

        if resp_msg.id == descr.app.client.onScriptVersionNotMatch.id:
            script_version = self._msg.get_values()[1]
            actual_script_version = resp_msg.get_values()[0]
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
            err_code, user_data = resp_msg.get_values()
            return LoginCommandResult(
                False,
                LoginCommandResultData(
                    ret_code=kbeenum.ServerError(err_code)
                ),
                kbeenum.ServerError(err_code).name
            )

        return LoginCommandResult(
            True,
            LoginCommandResultData(kbeenum.ServerError.SUCCESS, *resp_msg.get_values())
        )


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

    def __init__(self, client: kbeclient.Client):
        super().__init__(client)

        self._req_msg_spec = descr.app.loginapp.importServerErrorsDescr
        self._success_resp_msg_spec = descr.app.client.onImportServerErrorsDescr
        self._error_resp_msg_specs = []

        self._msg = kbeclient.Message(spec=self._req_msg_spec, fields=tuple())

    async def execute(self) -> memoryview:
        await self._client.send(self._msg)
        resp_msg = await self._waiting_for(settings.WAITING_FOR_SERVER_TIMEOUT)
        data = resp_msg.get_values()[0]
        return data
