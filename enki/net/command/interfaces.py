"""Commands for sending messages to the Logger component."""

from __future__ import annotations
import asyncio

import logging
from dataclasses import dataclass
import time

from enki import settings, devonly
from enki.net import msgspec
from enki.net.kbeclient.client import Client, StreamClient
from enki.net.kbeclient.message import IMsgReceiver, Message, MsgDescr


from . import _base

logger = logging.getLogger(__name__)


@dataclass
class QueryLoadResultData:
    component_type: int
    component_id: int
    istate: int


@dataclass
class QueryLoadCommandResult(_base.CommandResult):
    success: bool
    result: QueryLoadResultData
    text: str = ''


class QueryLoadCommand(_base.StreamCommand):
    """Logger command 'queryLoad'."""

    def __init__(self, client: StreamClient):
        super().__init__(client)
        client.set_resp_msg_spec(msgspec.app.interfaces.fakeRespLookApp)

        self._req_msg_spec = msgspec.app.interfaces.lookApp
        self._success_resp_msg_spec = None
        self._error_resp_msg_specs = []

        self._msg = Message(
            spec=self._req_msg_spec,
            fields=tuple()
        )

    async def execute(self) -> QueryLoadCommandResult:
        await self._client.send(self._msg)
        timeout_time = time.time() + settings.WAITING_FOR_SERVER_TIMEOUT
        while timeout_time > time.time():
            if self.is_updated:
                break
            await asyncio.sleep(settings.SECOND * 0.5)

        if self._client.is_stopped:
            return QueryLoadCommandResult(
                False, text=self.get_timeout_err_text()
            )

        self._client.stop()
        res = await self.get_result()

        return QueryLoadCommandResult(
            True, QueryLoadResultData(*res[0])
        )
