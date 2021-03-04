from __future__ import annotations
import abc
import asyncio
import collections
import logging
from typing import Union, List, Dict, Awaitable, Any, Tuple, ClassVar, Optional
from dataclasses import dataclass

from enki import settings
from enki import message, interface, kbeenum
from enki.misc import devonly

from . import _base

logger = logging.getLogger(__name__)


class HelloCommand(_base.Command):
    """LoginApp command 'hello'."""

    _req_msg_spec: message.MessageSpec = message.app.loginapp.hello
    _success_resp_msg_spec: message.MessageSpec = message.app.client.onHelloCB
    _error_resp_msg_specs: List[message.MessageSpec] = [
        message.app.client.onVersionNotMatch,
        message.app.client.onScriptVersionNotMatch,
    ]

    def __init__(self, kbe_version: str, script_version: str, encrypted_key: str,
                 client: interface.IClient):
        super().__init__(client)
        self._msg = message.Message(
            spec=self._req_msg_spec,
            fields=(kbe_version, script_version, encrypted_key)
        )

    async def execute(self) -> Tuple[bool, str]:
        await self.send(self._msg)
        resp_msg = await self.waiting_for(self._success_resp_msg_spec,
                                          self._error_resp_msg_specs,
                                          settings.WAITING_FOR_SERVER_TIMEOUT)
        if resp_msg.id == message.app.client.onVersionNotMatch.id:
            kbe_version = self._msg.get_values()[0]
            actual_kbe_version = resp_msg.get_values()[0]
            msg = f'Plugin designed for KBEngine version "{kbe_version}". ' \
                  f'But actual KBEngine version is "{actual_kbe_version}"'
            return False, msg

        if resp_msg.id == message.app.client.onScriptVersionNotMatch.id:
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
    account_name: Optional[str] = ''
    host: Optional[str] = ''
    tcp_port: Optional[int] = 0
    udp_port: Optional[int] = 0
    data: Optional[bytes] = b''


class LoginCommand(_base.Command):
    """LoginApp command 'login'."""

    _req_msg_spec: message.MessageSpec = message.app.loginapp.login
    _success_resp_msg_spec: message.MessageSpec = message.app.client.onLoginSuccessfully
    _error_resp_msg_specs: List[message.MessageSpec] = [
        message.app.client.onLoginFailed,
    ]

    def __init__(self, client_type: kbeenum.ClientType, client_data: bytes,
                 account_name: str, password: str, force_login: bool,
                 client: interface.IClient):
        super().__init__(client)
        if not force_login:
            force_login = ''
        self._msg = message.Message(
            spec=self._req_msg_spec,
            fields=(client_type.value, client_data, account_name, password,
                    force_login)
        )

    async def execute(self) -> LoginCommandResult:
        await self.send(self._msg)
        resp_msg = await self.waiting_for(self._success_resp_msg_spec,
                                          self._error_resp_msg_specs,
                                          settings.WAITING_FOR_SERVER_TIMEOUT)
        if resp_msg.id == message.app.client.onLoginFailed.id:
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

    _req_msg_spec: message.MessageSpec = message.app.loginapp.importClientMessages
    _success_resp_msg_spec: message.MessageSpec = message.app.client.onImportClientMessages
    _error_resp_msg_specs: List[message.MessageSpec] = []

    def __init__(self, client: interface.IClient):
        super().__init__(client)
        self._msg = message.Message(spec=self._req_msg_spec, fields=tuple())

    async def execute(self) -> bytes:
        await self.send(self._msg)
        resp_msg = await self.waiting_for(
            self._success_resp_msg_spec, [], settings.WAITING_FOR_SERVER_TIMEOUT
        )
        data = resp_msg.get_values()[0]
        return data


class ImportServerErrorsDescrCommand(_base.Command):
    """LoginApp command 'importServerErrorsDescr'."""

    _req_msg_spec: message.MessageSpec = message.app.loginapp.importServerErrorsDescr
    _success_resp_msg_spec: message.MessageSpec = message.app.client.onImportServerErrorsDescr
    _error_resp_msg_specs: List[message.MessageSpec] = []

    def __init__(self, client: interface.IClient):
        super().__init__(client)
        self._msg = message.Message(spec=self._req_msg_spec, fields=tuple())

    async def execute(self) -> bytes:
        await self.send(self._msg)
        resp_msg = await self.waiting_for(
            self._success_resp_msg_spec, [], settings.WAITING_FOR_SERVER_TIMEOUT
        )
        data = resp_msg.get_values()[0]
        return data
