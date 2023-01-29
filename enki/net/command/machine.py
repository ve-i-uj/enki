"""Commands for sending messages to Machine."""

from __future__ import annotations
import asyncio

import logging
from dataclasses import dataclass
import time

from enki import devonly, settings
from enki.net import msgspec
from enki.net.kbeclient.client import StreamClient
from enki.net.kbeclient.message import Message

from . import _base
from ._base import StreamCommand, LookAppCommand


logger = logging.getLogger(__name__)


@dataclass
class OnQueryAllInterfaceInfosCommandResultDataElement:
    uid: int
    username: str
    componentType: int
    componentID: int
    componentIDEx: int
    globalorderid: int
    grouporderid: int
    gus: int
    intaddr: int
    intport: int
    extaddr: int
    extport: int
    extaddrEx: str
    pid: int
    cpu: int
    mem: int
    usedmem: int
    state: int
    machineID: int
    extradata: int
    extradata1: int
    extradata2: int
    extradata3: int
    backRecvAddr: int
    backRecvPort: int


@dataclass
class OnQueryAllInterfaceInfosCommandResultData:
    """Ответ на Machine::onQueryAllInterfaceInfos."""
    infos: list[OnQueryAllInterfaceInfosCommandResultDataElement]


@dataclass
class OnQueryAllInterfaceInfosCommandResult(_base.CommandResult):
    success: bool
    result: OnQueryAllInterfaceInfosCommandResultData
    text: str = ''


class OnQueryAllInterfaceInfosCommand(StreamCommand):
    """Machine command 'OnQueryAllInterfaceInfos'."""

    def __init__(self, client: StreamClient, uid: int, username: str,
                 finderRecvPort: int = 0):
        super().__init__(client)
        self._client = client
        self._client.set_resp_msg_spec(
            msgspec.app.machine.fakeRespOnQueryAllInterfaceInfos
        )

        self._req_msg_spec = msgspec.app.machine.onQueryAllInterfaceInfos
        self._success_resp_msg_spec = msgspec.app.machine.fakeRespOnQueryAllInterfaceInfos
        self._error_resp_msg_specs = []

        self._msg = Message(
            spec=self._req_msg_spec,
            fields=(uid, username, finderRecvPort)
        )

    async def execute(self) -> OnQueryAllInterfaceInfosCommandResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        await self._client.send(self._msg)
        infos = []
        # На это сообщение сервер будет удерживать соединение, поэтому закроем
        # его сами. А о том, что ответ закончился узнаем только после закрытия.
        timeout_time = time.time() + settings.SECOND * 2
        while timeout_time > time.time():
            if self.last_chunk_time + settings.SECOND > time.time():
                # Давно уже ничего не отправляется, значит закончилась передача
                break
            await asyncio.sleep(settings.SECOND * 0.5)
        self._client.stop()
        for info in (await self.get_result()):
            infos.append(OnQueryAllInterfaceInfosCommandResultDataElement(*info))
        return OnQueryAllInterfaceInfosCommandResult(
            True, OnQueryAllInterfaceInfosCommandResultData(infos)
        )


class MachineLookAppCommand(LookAppCommand):
    """Machine command 'lookApp'."""

    def __init__(self, client: StreamClient):
        super().__init__(client, msgspec.app.machine.lookApp,
                         msgspec.app.machine.fakeRespLookApp)
