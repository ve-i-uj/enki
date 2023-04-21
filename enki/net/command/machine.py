"""Commands for sending messages to Machine."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from enki import settings, devonly
from enki.enkitype import AppAddr
from enki.net import msgspec
from enki.net.kbeclient.client import Client
from enki.net.kbeclient.message import IMsgReceiver, Message, MsgDescr


from . import _base

logger = logging.getLogger(__name__)


class OnQueryAllInterfaceInfosClient(Client):
    """Клиент для запроса Machine::onQueryAllInterfaceInfos."""

    def __init__(self, addr: AppAddr, msg_spec_by_id: dict[int, MsgDescr]):
        super().__init__(addr, msg_spec_by_id)
        self._stop_task = None

    def on_receive_data(self, data: memoryview):
        while data:
            fields = []
            for kbe_type in msgspec.app.machine.resp_onQueryAllInterfaceInfos.field_types:
                value, size = kbe_type.decode(data)
                fields.append(value)
                data = data[size:]
            self._msg_receiver.on_receive_msg(
                Message(
                    msgspec.app.machine.resp_onQueryAllInterfaceInfos,
                    tuple(fields)
                )
            )

        async def stop():
            await asyncio.sleep(settings.WAITING_FOR_SERVER_TIMEOUT)
            logger.debug('[%s] %s', self, devonly.func_args_values())
            self.stop()

        if self._stop_task is not None:
            self._stop_task.cancel()
        self._stop_task = asyncio.create_task(stop())


@dataclass
class OnQueryAllInterfaceInfosCommandResultDataElement:
    @property
    def uid(self) -> int:
        return None

    @property
    def username(self) -> str:
        return None

    @property
    def componentType(self) -> int:
        return None

    @property
    def componentID(self) -> int:
        return None

    @property
    def componentIDEx(self) -> int:
        return None

    @property
    def globalorderid(self) -> int:
        return None

    @property
    def grouporderid(self) -> int:
        return None

    @property
    def gus(self) -> int:
        return None

    @property
    def intaddr(self) -> int:
        return None

    @property
    def intport(self) -> int:
        return None

    @property
    def extaddr(self) -> int:
        return None

    @property
    def extport(self) -> int:
        return None

    @property
    def extaddrEx(self) -> str:
        return None

    @property
    def pid(self) -> int:
        return None

    @property
    def cpu(self) -> int:
        return None

    @property
    def mem(self) -> int:
        return None

    @property
    def usedmem(self) -> int:
        return None

    @property
    def state(self) -> int:
        return None

    @property
    def machineID(self) -> int:
        return None

    @property
    def extradata(self) -> int:
        return None

    @property
    def extradata1(self) -> int:
        return None

    @property
    def extradata2(self) -> int:
        return None

    @property
    def extradata3(self) -> int:
        return None

    @property
    def backRecvAddr(self) -> int:
        return None

    @property
    def backRecvPort(self) -> int:
        return None



@dataclass
class OnQueryAllInterfaceInfosCommandResultData:
    """Ответ на Machine::onQueryAllInterfaceInfos."""
    @property
    def infos(self) -> list[OnQueryAllInterfaceInfosCommandResultDataElement]:
        return None



@dataclass
class OnQueryAllInterfaceInfosCommandResult(_base.CommandResult):
    @property
    def success(self) -> bool:
        return None

    @property
    def result(self) -> OnQueryAllInterfaceInfosCommandResultData:
        return None

    @property
    def text(self) -> str:
        return None



class OnQueryAllInterfaceInfosCommand(_base.ICommand, IMsgReceiver):
    """Machine command 'OnQueryAllInterfaceInfos'."""

    def __init__(self, client: OnQueryAllInterfaceInfosClient, uid: int, username: str,
                 finderRecvPort: int = 0):
        self._client = client
        self._msg = Message(
            spec=msgspec.app.machine.onQueryAllInterfaceInfos,
            fields=(uid, username, finderRecvPort)
        )
        self._result_future = asyncio.get_event_loop().create_future()
        self._infos = []

    def on_receive_msg(self, msg: Message) -> bool:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._infos.append(
            OnQueryAllInterfaceInfosCommandResultDataElement(*msg.get_values())
        )
        return True

    def on_end_receive_msg(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._result_future.set_result(self._infos)

    async def execute(self) -> OnQueryAllInterfaceInfosCommandResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        await self._client.send(self._msg)
        infos = await self._result_future
        return OnQueryAllInterfaceInfosCommandResult(True, infos)
