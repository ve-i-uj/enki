from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
import time

from enki import settings
from enki.misc import devonly
from enki.net.client import StreamClient, TCPClient
from enki.core.message import Message, MsgDescr

from ._base import CommandResult, StreamCommand

logger = logging.getLogger(__name__)


@dataclass
class LookAppResultData:
    component_type: int
    component_id: int
    istate: int


@dataclass
class LookAppCommandResult(CommandResult):
    success: bool
    result: LookAppResultData
    text: str = ''


class LookAppCommand(StreamCommand):
    """The base class for the 'lookApp' command."""

    def __init__(self, client: StreamClient, req_msg_spec: MsgDescr,
                 fake_resp_msg_spec: MsgDescr):
        """Constructor.

        Args:
            client (StreamClient): клиент, который в ответ на подключение
                получит открытый стрим
            req_msg_spec (MsgDescr): сообщение, на которое сервер откроет скрим
            fake_resp_msg_spec (MsgDescr): фэйковое сообщение, в котором описаны
                поля для декодирования стрима (см. Enki::fakeRespLookApp)
        """
        super().__init__(client)
        client.set_resp_msg_spec(fake_resp_msg_spec)

        self._req_msg_spec = req_msg_spec
        self._success_resp_msg_spec = None
        self._error_resp_msg_specs = []

        self._msg = Message(spec=self._req_msg_spec, fields=tuple())

    async def execute(self) -> LookAppCommandResult:
        await self._client.send_msg(self._msg)
        timeout_time = time.time() + settings.WAITING_FOR_SERVER_TIMEOUT
        while timeout_time > time.time():
            if self.is_updated:
                break
            await asyncio.sleep(settings.SECOND * 0.5)

        if not self._client.is_alive:
            return LookAppCommandResult(False,
                                        text=self.get_timeout_err_text())

        self._client.stop()
        res = await self.get_result()
        if not res:
            return LookAppCommandResult(False, text='No data from server')

        return LookAppCommandResult(True, LookAppResultData(*res[0]))
