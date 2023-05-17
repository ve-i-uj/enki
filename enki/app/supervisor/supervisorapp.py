"""???"""

from __future__ import annotations
import abc

import asyncio
from asyncio import StreamWriter
import collections
import logging
import sys
from enki.core import msgspec
from enki.core import kbemath
from enki.core.kbeenum import ComponentType
from enki.core.message import Message, MessageSerializer
from enki.handler.base import Handler

from enki.misc import log, devonly
from enki.core.enkitype import AppAddr, Result
from enki.core import msgspec
from enki.net.channel import TCPChannel
from enki.net import server
from enki.net.server import TCPServer, UDPServer
from enki.net.inet import ChannelType, IAppComponent, IChannel, IServerMsgReceiver, \
    ConnectionInfo, ChannelType
from enki.handler.serverhandler.machinehandler import OnBroadcastInterfaceHandler, \
    OnBroadcastInterfaceHandlerResult, OnBroadcastInterfaceParsedData

logger = logging.getLogger(__name__)


class Supervisor(IAppComponent):

    def __init__(self, udp_addr: AppAddr, tcp_addr: AppAddr) -> None:
        self._udp_addr = udp_addr
        self._tcp_addr = tcp_addr
        self._internal_tcp_addr = AppAddr('0.0.0.0', server.get_free_port())

        # Сервера для обслуживания соединений
        self._udp_server = UDPServer(udp_addr, msgspec.app.machine.SPEC_BY_ID, self)
        self._tcp_server = TCPServer(tcp_addr, msgspec.app.machine.SPEC_BY_ID, self)
        self._internal_tcp_server = TCPServer(self._internal_tcp_addr, msgspec.app.machine.SPEC_BY_ID, self)

        self._components_infos: dict[ComponentType, OnBroadcastInterfaceParsedData] = {}
        self._handlers = {
            msgspec.app.machine.onQueryAllInterfaceInfos.id: _OnQueryAllInterfaceInfosHandler(self)
        }

    @property
    def info(self) -> OnBroadcastInterfaceParsedData:
        return OnBroadcastInterfaceParsedData(
            uid=1,
            username='root',
            componentType=ComponentType.MACHINE_TYPE.value,
            componentID=1,
            componentIDEx=0,
            globalorderid=-1,
            grouporderid=-1,
            gus=-1,
            intaddr=kbemath.ip2int(self._internal_tcp_addr.host),
            intport=kbemath.port2int(self._internal_tcp_addr.port),
            extaddr=kbemath.ip2int(self._tcp_addr.host),
            extport=kbemath.port2int(self._tcp_addr.port),
            extaddrEx='',
            pid=1,
            cpu=0,
            mem=0,
            usedmem=0,
            state=0,
            machineID=1,
            extradata=0,
            extradata1=0,
            extradata2=0,
            extradata3=0,
            backRecvAddr=0,
            backRecvPort=0
        )

    # @property
    # def udp_addr(self) -> AppAddr:
    #     return self._udp_addr

    @property
    def tcp_addr(self) -> AppAddr:
        return self._tcp_addr

    # @property
    # def internal_tcp_addr(self) -> AppAddr:
    #     return self._internal_tcp_addr

    @property
    def components_infos(self) -> dict[ComponentType, OnBroadcastInterfaceParsedData]:
        return self._components_infos

    async def start(self) -> Result:
        res = await self._udp_server.start()
        if not res.success:
            return res
        res = await self._tcp_server.start()
        if not res.success:
            return res
        res = await self._internal_tcp_server.start()
        if not res.success:
            return res

        return Result(True, None)

    async def stop(self):
        self._udp_server.stop()
        await self._tcp_server.stop()

    async def on_receive_msg(self, msg: Message, channel: IChannel):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        if msg.id == msgspec.app.machine.onBroadcastInterface.id:
            res = OnBroadcastInterfaceHandler().handle(msg)
            self._components_infos[res.result.component_type] = res.result
        handler = self._handlers.get(msg.id)
        if handler is None:
            logger.warning('[%s] There is no handler for the message %s', self, msg.id)
            return
        await handler.handle(msg, channel) # type: ignore

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'

    __repr__ = __str__


class _SupervisorHandler(abc.ABC):

    def __init__(self, app: Supervisor) -> None:
        self._app = app
        self._serializer = MessageSerializer(msgspec.app.machine.SPEC_BY_ID)

    @abc.abstractmethod
    async def handle(self, msg: Message, channel: IChannel):
        pass


class _OnQueryAllInterfaceInfosHandler(_SupervisorHandler):
    """Обработчик для сообщения Machine::onQueryAllInterfaceInfos .

    В ответ отправляем статистику обо всех зарегестрированных компонентах,
    плюс о себе (через сообщения Machine::onBroadcastInterface). Ответ нужно
    отправлять без оболочки сразу данными либо на запрошенный порт, либо в
    тоже tcp соединение.
    """

    async def handle(self, msg: Message, channel: TCPChannel):
        self._app.components_infos[ComponentType.MACHINE_TYPE] = self._app.info

        for _comp_type, pd in self._app.components_infos.items():
            resp_msg = Message(msgspec.app.machine.onBroadcastInterface, pd.values())
            data = self._serializer.serialize(resp_msg, only_data=True)
            await channel.send_msg_content(
                data, channel.connection_info.src_addr, ChannelType.TCP
            )
        await channel.close()
