"""Commands for sending messages to the Logger component."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from enki import settings
from enki.misc import devonly
from enki.core.enkitype import AppAddr
from enki.core import msgspec
from enki.net.client import TCPClient
from enki.net.inet import IClientMsgReceiver
from enki.core.message import Message, MsgDescr


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


class QueryLoadCommand(_base.TCPCommand):
    """Logger command 'queryLoad'."""

    def __init__(self, client: TCPClient):
        super().__init__(client)

        self._req_msg_spec = msgspec.app.logger.queryLoad
        self._success_resp_msg_spec = None
        self._error_resp_msg_specs = []

        self._msg = Message(
            spec=self._req_msg_spec,
            fields=tuple()
        )

    async def execute(self) -> QueryLoadCommandResult:
        await self._client.send_msg(self._msg)
        await self._waiting_for(settings.SECOND)

        if self.status == _base.AwaitableCommandState.ERROR_CONNECTION_CLOSED:
            return QueryLoadCommandResult(
                False, text='Connection abnormaly closed by server'
            )

        return QueryLoadCommandResult(True)
