"""???"""

import asyncio
import collections
import logging
import sys
from enki.core import msgspec
from enki.core.kbeenum import ComponentType
from enki.core.message import Message

from enki.misc import log, devonly
from enki.core.enkitype import AppAddr, Result
from enki.core import msgspec
from enki.net.server import UDPServer
from enki.net.inet import IAppComponent, IChannel, IServerMsgReceiver
from enki.handler.serverhandler.machinehandler import OnBroadcastInterfaceHandler, OnBroadcastInterfaceHandlerResult, OnBroadcastInterfaceParsedData

logger = logging.getLogger(__name__)


class Supervisor(IAppComponent):

    def __init__(self, udp_addr: AppAddr) -> None:
        self._udp_server = UDPServer(
            udp_addr,
            msgspec.app.machine.SPEC_BY_ID,
            msg_receiver=self
        )
        # TODO: [2023-05-15 18:05 burov_alexey@mail.ru]:
        # Пока подразумеваем, что будет только по одному компонента каждого типа
        self._components_infos: dict[ComponentType, OnBroadcastInterfaceParsedData] = {}

    async def start(self) -> Result:
        res = await self._udp_server.start()
        if not res.success:
            return res

        return Result(True, None)

    def stop(self):
        self._udp_server.stop()

    def on_receive_msg(self, msg: Message, channel: IChannel):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        if msg.id == msgspec.app.machine.onBroadcastInterface.id:
            res = OnBroadcastInterfaceHandler().handle(msg)
            self._components_infos[res.result.component_type] = res.result

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'

    __repr__ = __str__
