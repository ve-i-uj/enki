"""Commands for sending messages to BaseApp."""

import logging
from typing import List, Tuple, Optional

from enki import exception, settings, descr, kbeclient, dcdescr
from enki import interface
from enki.interface import IClient, IMsgReceiver, IResult
from enki.kbeclient.message import Message

from . import _base

logger = logging.getLogger(__name__)


class ImportClientMessagesCommand(_base.Command):
    """BaseApp command 'importClientMessages'."""

    def __init__(self, client: interface.IClient):
        super().__init__(client)

        self._req_msg_spec: dcdescr.MessageDescr = descr.app.baseapp.importClientMessages
        self._success_resp_msg_spec: dcdescr.MessageDescr = descr.app.client.onImportClientMessages
        self._error_resp_msg_specs: List[dcdescr.MessageDescr] = []

        self._msg = kbeclient.Message(spec=self._req_msg_spec, fields=tuple())

    async def execute(self) -> bytes:
        await self._client.send(self._msg)
        resp_msg = await self._waiting_for(settings.WAITING_FOR_SERVER_TIMEOUT)
        if resp_msg is None:
            logger.error(_base.TIMEOUT_ERROR_MSG)
            return b''
        data = resp_msg.get_values()[0]
        return data


class ImportClientEntityDefCommand(_base.Command):
    """BaseApp command 'importClientEntityDef'."""

    def __init__(self, client: interface.IClient):
        super().__init__(client)

        self._req_msg_spec: dcdescr.MessageDescr = descr.app.baseapp.importClientEntityDef
        self._success_resp_msg_spec: dcdescr.MessageDescr = descr.app.client.onImportClientEntityDef
        self._error_resp_msg_specs: List[dcdescr.MessageDescr] = []

        self._msg = kbeclient.Message(spec=self._req_msg_spec, fields=tuple())

    async def execute(self) -> memoryview:
        await self._client.send(self._msg)
        resp_msg = await self._waiting_for(settings.WAITING_FOR_SERVER_TIMEOUT)
        if resp_msg is None:
            logger.error(_base.TIMEOUT_ERROR_MSG)
            return memoryview(b'')
        data = resp_msg.get_values()[0]
        return data


class HelloCommand(_base.Command):
    """BaseApp command 'hello'."""

    def __init__(self, kbe_version: str, script_version: str, encrypted_key: bytes,
                 client: interface.IClient):
        super().__init__(client)

        self._req_msg_spec: dcdescr.MessageDescr = descr.app.baseapp.hello
        self._success_resp_msg_spec: dcdescr.MessageDescr = descr.app.client.onHelloCB
        self._error_resp_msg_specs: List[dcdescr.MessageDescr] = [
            descr.app.client.onVersionNotMatch,
            descr.app.client.onScriptVersionNotMatch,
        ]

        self._msg = kbeclient.Message(
            spec=self._req_msg_spec,
            fields=(kbe_version, script_version, encrypted_key)
        )

    async def execute(self) -> Tuple[bool, str]:
        await self._client.send(self._msg)
        resp_msg = await self._waiting_for(settings.WAITING_FOR_SERVER_TIMEOUT)
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


class OnClientActiveTickCommand(_base.Command):
    """BaseApp command 'onClientActiveTick'."""

    def __init__(self, client: interface.IClient,
                 timeout: float = 0.0):
        super().__init__(client)

        self._req_msg_spec: dcdescr.MessageDescr = descr.app.baseapp.onClientActiveTick
        self._success_resp_msg_spec: dcdescr.MessageDescr = descr.app.client.onAppActiveTickCB
        self._error_resp_msg_specs: List[dcdescr.MessageDescr] = []

        self._timeout = timeout
        self._msg = kbeclient.Message(spec=self._req_msg_spec, fields=tuple())

    async def execute(self) -> _base.CommandResult:
        await self._client.send(self._msg)
        resp_msg = await self._waiting_for(self._timeout)
        if resp_msg is None:
            return _base.CommandResult(
                False, f'No response for the "{self._req_msg_spec.name}"'
            )

        return _base.CommandResult(True)


class LoginBaseappCommand(_base.Command):

    def __init__(self, client: IClient, account_name: str, password: str):
        super().__init__(client)
        self._account_name = account_name
        self._password = password

        self._req_msg_spec = descr.app.baseapp.loginBaseapp
        self._success_resp_msg_spec = None
        self._error_resp_msg_specs = [descr.app.client.onLoginBaseappFailed]

    async def execute(self) -> _base.CommandResult:
        msg = kbeclient.Message(
            descr.app.baseapp.loginBaseapp, (self._account_name, self._password)
        )
        await self._client.send(msg)
        resp_msg = await self._waiting_for(settings.WAITING_FOR_SERVER_TIMEOUT)
        if resp_msg is None:
            # Good. There were no error messages.
            return _base.CommandResult(True, '')
        err_code = resp_msg.get_values()[0]
        err_name = descr.servererror.ERROR_BY_ID[err_code].name
        text = f'The client cannot connect to the BaseApp ({err_name})'
        return _base.CommandResult(False, text)