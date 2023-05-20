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
from enki.net.channel import TCPChannel, UDPChannel
from enki.net import server
from enki.net.client import StreamClient
from enki.net.server import TCPServer, UDPMsgServer
from enki.net.inet import ChannelType, IAppComponent, IChannel, IServerMsgReceiver, \
    ConnectionInfo, ChannelType
from enki.handler.serverhandler.machinehandler import OnBroadcastInterfaceHandler, \
    OnBroadcastInterfaceHandlerResult, OnBroadcastInterfaceParsedData, QueryComponentIDHandler

logger = logging.getLogger(__name__)


class Supervisor(IAppComponent):

    def __init__(self, udp_addr: AppAddr, tcp_addr: AppAddr) -> None:
        # Если пришло ими контейнера, нужно преобразовать его в ip адрес, т.к.
        # адрес компонента в KBEngine сохраняется и распространяется в
        # трансформированном виде socket.inet_aton
        udp_addr.host = server.get_real_host_ip(udp_addr.host)
        tcp_addr.host = server.get_real_host_ip(tcp_addr.host)

        self._udp_addr = udp_addr
        self._tcp_addr = tcp_addr
        self._internal_tcp_addr = AppAddr('0.0.0.0', server.get_free_port())

        # Сервера для обслуживания соединений
        self._udp_server = UDPMsgServer(udp_addr, msgspec.app.machine.SPEC_BY_ID, self)
        self._tcp_server = TCPServer(tcp_addr, msgspec.app.machine.SPEC_BY_ID, self)
        self._internal_tcp_server = TCPServer(self._internal_tcp_addr, msgspec.app.machine.SPEC_BY_ID, self)

        # Уникальный идентификатор, генерируемый Машиной
        self._component_id_cntr = 0
        self._componet_info_by_id: dict[int, OnBroadcastInterfaceParsedData] = {}
        # Сразу заполним информацию о себе
        pd = OnBroadcastInterfaceParsedData.get_empty()
        pd.componentID = self.generate_component_id()
        pd.intaddr=kbemath.ip2int(self._internal_tcp_addr.host)
        pd.intport=kbemath.port2int(self._internal_tcp_addr.port)
        pd.extaddr=kbemath.ip2int(self._tcp_addr.host)
        pd.extport=kbemath.port2int(self._tcp_addr.port)
        self._componet_info_by_id[pd.componentID] = pd
        # Маппинг типа компонента к его id. По id компонента затем можно
        # получить инфу для OnBroadcastInterfaceParsedData
        self._component_id_by_type = {}
        self._component_id_by_type[ComponentType.MACHINE_TYPE] = pd.componentID

        self._handlers = {
            msgspec.app.machine.onBroadcastInterface.id: _OnBroadcastInterfaceHandler(self),
            msgspec.app.machine.onQueryAllInterfaceInfos.id: _OnQueryAllInterfaceInfosHandler(self),
            msgspec.app.machine.queryComponentID.id: _QueryComponentIDHandler(self),
        }

    def generate_component_id(self) -> int:
        while True:
            self._component_id_cntr += 1
            component_id = self._component_id_cntr
            if component_id not in self._componet_info_by_id:
                break

        return component_id

    @property
    def tcp_addr(self) -> AppAddr:
        return self._tcp_addr

    @property
    def udp_addr(self) -> AppAddr:
        return self._udp_addr

    @property
    def internal_tcp_addr(self) -> AppAddr:
        return self._internal_tcp_addr

    @property
    def component_info_by_id(self) -> dict[int, OnBroadcastInterfaceParsedData]:
        """Информация о компоненте по уникальному идентификатору сгенерированному Супервизором."""
        return self._componet_info_by_id

    @property
    def component_id_by_type(self) -> dict[ComponentType, int]:
        return self._component_id_by_type

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
        handler = self._handlers.get(msg.id)
        if handler is None:
            logger.warning('[%s] There is no handler for the message %s', self, msg.id)
            return
        await handler.handle(msg, channel)  # type: ignore

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

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'

    __repr__ = __str__


class _OnBroadcastInterfaceHandler(_SupervisorHandler):
    """Обработчик для сообщения Machine::OnBroadcastInterface .

    Компонент запускаясь отправляет на Машину это сообщение, чтобы
    зарегистрироваться.
    """

    async def handle(self, msg: Message, channel: UDPChannel):
        res = OnBroadcastInterfaceHandler().handle(msg)
        pd = res.result
        self._app.component_info_by_id[pd.componentID] = pd
        self._app.component_id_by_type[pd.component_type] = pd.componentID


class _OnQueryAllInterfaceInfosHandler(_SupervisorHandler):
    """Обработчик для сообщения Machine::onQueryAllInterfaceInfos .

    В ответ отправляем статистику обо всех зарегестрированных компонентах,
    плюс о себе (через сообщения Machine::onBroadcastInterface). Ответ нужно
    отправлять без оболочки сразу данными либо на запрошенный порт, либо в
    тоже tcp соединение.
    """

    async def handle(self, msg: Message, channel: TCPChannel):
        for _comp_type, pd in self._app.component_info_by_id.items():
            resp_msg = Message(msgspec.app.machine.onBroadcastInterface, pd.values())
            data = self._serializer.serialize(resp_msg, only_data=True)
            await channel.send_msg_content(
                data, channel.connection_info.src_addr, ChannelType.TCP
            )
        await channel.close()


class _QueryComponentIDHandler(_SupervisorHandler):
    """Обработчик для сообщения Machine::queryComponentID .

    В ответ вычисляется componentID и передаётся обратно UDP сообщением
    Machine::queryComponentID без обёртки на порт из поля finderRecvPort.
    Адрес для ответа берётся из источника запроса.
    """

    async def handle(self, msg: Message, channel: UDPChannel):
        res = QueryComponentIDHandler().handle(msg)
        pd = res.result
        assert pd is not None

        # Если запущено внутри контейнера, то хостом будет сетевой мост
        cb_addr = channel.connection_info.src_addr.copy()
        cb_addr.port = pd.callback_port
        logger.debug('[%s] cb_addr = "%s"', self, cb_addr)

        new_component_id = self._app.generate_component_id()
        self._app.component_id_by_type[pd.component_type] = new_component_id

        pd.componentID = new_component_id
        resp_msg = Message(msgspec.app.machine.queryComponentID, pd.values())
        data = self._serializer.serialize(resp_msg, only_data=True)

        # Пробуем на бродкаст
        cb_addr = AppAddr('255.255.255.255', pd.callback_port)
        logger.debug('[%s] cb_addr = "%s"', self, cb_addr)
        await channel.send_msg_content(data, cb_addr, ChannelType.BROADCAST)
