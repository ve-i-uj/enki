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


class ImportClientMessagesCommand(_base.Command):
    """BaseApp command 'importClientMessages'."""

    _req_msg_spec: message.MessageSpec = message.app.baseapp.importClientMessages
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


class ImportClientEntityDefCommand(_base.Command):
    """BaseApp command 'importClientEntityDef'."""

    _req_msg_spec: message.MessageSpec = message.app.baseapp.importClientEntityDef
    _success_resp_msg_spec: message.MessageSpec = message.app.client.onImportClientEntityDef
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


class HelloCommand(_base.Command):
    """BaseApp command 'hello'."""

    _req_msg_spec: message.MessageSpec = message.app.baseapp.hello
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
