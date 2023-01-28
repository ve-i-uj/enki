"""Commands for sending messages to the Logger component."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from enki import settings, devonly
from enki.enkitype import AppAddr
from enki.net import msgspec
from enki.net.kbeclient.client import Client
from enki.net.kbeclient.message import IMsgReceiver, Message, MsgDescr


from . import _base

logger = logging.getLogger(__name__)


@dataclass
class QueryLoadResultData:
    pass


@dataclass
class QueryLoadCommandResult(_base.CommandResult):
    success: bool
    result: QueryLoadResultData
    text: str = ''


class QueryLoadCommandResultCommand(_base.Command):
    """Logger command 'queryLoad'."""

    def __init__(self, client: Client):
        super().__init__(client)

        self._req_msg_spec = msgspec.app.logger.queryLoad
        self._success_resp_msg_spec = None
        self._error_resp_msg_specs = []

        self._msg = Message(
            spec=self._req_msg_spec,
            fields=tuple()
        )

    async def execute(self) -> QueryLoadCommandResult:
        await self._client.send(self._msg)
        await self._waiting_for(settings.SECOND)

        if self.status == _base.AwaitableCommandState.ERROR_CONNECTION_CLOSED:
            return QueryLoadCommandResult(
                False, text='Connection abnormaly closed by server'
            )

        return QueryLoadCommandResult(True)
