"""Commands for sending messages to BaseApp."""

import logging
from typing import List, Tuple

from enki import settings, descr, kbeclient, dcdescr
from ..kbeclient import interface

from . import _base

logger = logging.getLogger(__name__)


class ImportClientMessagesCommand(_base.Command):
    """BaseApp command 'importClientMessages'."""

    _req_msg_spec: dcdescr.MessageDescr = descr.app.baseapp.importClientMessages
    _success_resp_msg_spec: dcdescr.MessageDescr = descr.app.client.onImportClientMessages
    _error_resp_msg_specs: List[dcdescr.MessageDescr] = []

    def __init__(self, client: interface.IClient):
        super().__init__(client)
        self._msg = kbeclient.Message(spec=self._req_msg_spec, fields=tuple())

    async def execute(self) -> bytes:
        await self.send(self._msg)
        resp_msg = await self._waiting_for(
            self._success_resp_msg_spec, [], settings.WAITING_FOR_SERVER_TIMEOUT
        )
        if resp_msg is None:
            logger.error(_base.TIMEOUT_ERROR_MSG)
            return b''
        data = resp_msg.get_values()[0]
        return data


class ImportClientEntityDefCommand(_base.Command):
    """BaseApp command 'importClientEntityDef'."""

    _req_msg_spec: dcdescr.MessageDescr = descr.app.baseapp.importClientEntityDef
    _success_resp_msg_spec: dcdescr.MessageDescr = descr.app.client.onImportClientEntityDef
    _error_resp_msg_specs: List[dcdescr.MessageDescr] = []

    def __init__(self, client: interface.IClient):
        super().__init__(client)
        self._msg = kbeclient.Message(spec=self._req_msg_spec, fields=tuple())

    async def execute(self) -> bytes:
        await self.send(self._msg)
        resp_msg = await self._waiting_for(
            self._success_resp_msg_spec, [], settings.WAITING_FOR_SERVER_TIMEOUT
        )
        if resp_msg is None:
            logger.error(_base.TIMEOUT_ERROR_MSG)
            return b''
        data = resp_msg.get_values()[0]
        return data


class HelloCommand(_base.Command):
    """BaseApp command 'hello'."""

    _req_msg_spec: dcdescr.MessageDescr = descr.app.baseapp.hello
    _success_resp_msg_spec: dcdescr.MessageDescr = descr.app.client.onHelloCB
    _error_resp_msg_specs: List[dcdescr.MessageDescr] = [
        descr.app.client.onVersionNotMatch,
        descr.app.client.onScriptVersionNotMatch,
    ]

    def __init__(self, kbe_version: str, script_version: str, encrypted_key: str,
                 client: interface.IClient):
        super().__init__(client)
        self._msg = kbeclient.Message(
            spec=self._req_msg_spec,
            fields=(kbe_version, script_version, encrypted_key)
        )

    async def execute(self) -> Tuple[bool, str]:
        await self.send(self._msg)
        resp_msg = await self._waiting_for(self._success_resp_msg_spec,
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


class OnClientActiveTickCommand(_base.Command):
    """BaseApp command 'onClientActiveTick'."""

    def __init__(self, client: interface.IClient,
                 receiver: interface.IMsgReceiver = None,
                 timeout: int = 0):
        super().__init__(client, receiver)

        # TODO: [30.07.2021 burov_alexey@mail.ru]:
        # Описание команды, должно быть атрибутом команды.
        # Т.к. onClientActiveTick генерируемое сообщение
        self._req_msg_spec: dcdescr.MessageDescr = descr.app.baseapp.onClientActiveTick
        self._success_resp_msg_spec: dcdescr.MessageDescr = descr.app.client.onAppActiveTickCB
        self._error_resp_msg_specs: List[dcdescr.MessageDescr] = []

        self._timeout = timeout
        self._msg = kbeclient.Message(spec=self._req_msg_spec, fields=tuple())

    async def execute(self) -> bool:
        await self.send(self._msg)
        resp_msg = await self._waiting_for(self._success_resp_msg_spec,
                                           self._error_resp_msg_specs,
                                           self._timeout)
        if resp_msg is None:
            logger.error(_base.TIMEOUT_ERROR_MSG)
            return False

        if resp_msg.id != descr.app.client.onAppActiveTickCB.id:
            msg = f'Unexpected response (response id = "{resp_msg.id}")'
            logger.warning(msg)
            return False

        return True
