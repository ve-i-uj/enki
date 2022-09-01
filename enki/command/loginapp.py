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

    async def execute(self) -> Tuple[bool, str]:
        await self._client.send(self._msg)
        resp_msg: IMessage = await self._waiting_for(self._success_resp_msg_spec,
                                           self._error_resp_msg_specs,
                                           settings.WAITING_FOR_SERVER_TIMEOUT)
        if resp_msg is None:
            return False, _base.TIMEOUT_ERROR_MSG

        if resp_msg.id == descr.app.client.onVersionNotMatch.id:
            kbe_version = self._msg.get_values()[0]
            actual_kbe_version = resp_msg.get_values()[0]
            msg = f'Plugin designed for KBEngine version "{kbe_version}". ' \
                  f'But actual KBEngine version is "{actual_kbe_version}"'
            return False, msg

        if resp_msg.id == descr.app.client.onScriptVersionNotMatch.id:
            script_version = self._msg.get_values()[1]
            actual_script_version = resp_msg.get_values()[0]
            msg = f'Plugin designed for script version "{script_version}". ' \
                  f'But actual script version is "{actual_script_version}"'
            return False, msg

        return True, ''


@dataclass
class LoginCommandResult:
    """Result of command 'login'."""
    ret_code: kbeenum.ServerError
    account_name: str = ''
    host: str = ''
    tcp_port: int = 0
    udp_port: int = 0
    data: bytes = b''


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

        if not force_login:
            force_login = ''
        self._msg = kbeclient.Message(
            spec=self._req_msg_spec,
            fields=(client_type.value, client_data, account_name, password,
                    force_login)
        )

    async def execute(self) -> LoginCommandResult:
        await self._client.send(self._msg)
        resp_msg = await self._waiting_for(self._success_resp_msg_spec,
                                           self._error_resp_msg_specs,
                                           settings.WAITING_FOR_SERVER_TIMEOUT)
        if resp_msg is None:
            logger.error(_base.TIMEOUT_ERROR_MSG)
            return LoginCommandResult(ret_code=kbeenum.ServerError.MAX)

        if resp_msg.id == descr.app.client.onLoginFailed.id:
            values = resp_msg.get_values()
            return LoginCommandResult(ret_code=kbeenum.ServerError(values[0]),
                                      data=values[1])

        values = resp_msg.get_values()
        return LoginCommandResult(
            ret_code=kbeenum.ServerError.SUCCESS,
            account_name=values[0],
            host=values[1],
            tcp_port=values[2],
            udp_port=values[3],
            data=values[4]
        )


class ImportClientMessagesCommand(_base.Command):
    """LoginApp command 'importClientMessages'."""

    def __init__(self, client: kbeclient.Client):
        super().__init__(client)

        self._req_msg_spec: descr.MessageDescr = descr.app.loginapp.importClientMessages
        self._success_resp_msg_spec: descr.MessageDescr = descr.app.client.onImportClientMessages
        self._error_resp_msg_specs: List[descr.MessageDescr] = []

        self._msg = kbeclient.Message(spec=self._req_msg_spec, fields=tuple())

    async def execute(self) -> bytes:
        await self._client.send(self._msg)
        resp_msg = await self._waiting_for(
            self._success_resp_msg_spec, [], settings.WAITING_FOR_SERVER_TIMEOUT
        )
        if resp_msg is None:
            raise exception.StopClientException()
        data = resp_msg.get_values()[0]
        return data


class ImportServerErrorsDescrCommand(_base.Command):
    """LoginApp command 'importServerErrorsDescr'."""

    def __init__(self, client: kbeclient.Client):
        super().__init__(client)

        self._req_msg_spec: descr.MessageDescr = descr.app.loginapp.importServerErrorsDescr
        self._success_resp_msg_spec: descr.MessageDescr = descr.app.client.onImportServerErrorsDescr
        self._error_resp_msg_specs: List[descr.MessageDescr] = []

        self._msg = kbeclient.Message(spec=self._req_msg_spec, fields=tuple())

    async def execute(self) -> memoryview:
        await self._client.send(self._msg)
        resp_msg = await self._waiting_for(
            self._success_resp_msg_spec, [], settings.WAITING_FOR_SERVER_TIMEOUT
        )
        data = resp_msg.get_values()[0]
        return data
