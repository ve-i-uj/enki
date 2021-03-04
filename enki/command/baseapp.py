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
