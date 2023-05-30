"""Компонент повторяющий функционал компонента Machine серверного игрового движка KBEngine."""

from __future__ import annotations
import abc
import asyncio

import logging
from typing import Optional

from enki.core import msgspec
from enki.core import kbemath
from enki.core.kbeenum import ComponentState, ComponentType, ShutdownState
from enki.core.message import Message, MessageSerializer

from enki.misc import devonly
from enki.core.enkitype import AppAddr, Result
from enki.core import msgspec
from enki.net.channel import TCPChannel, UDPChannel
from enki.net import server
from enki.net.server import TCPServer, UDPMsgServer
from enki.net.inet import ChannelType, IChannel, IServerMsgReceiver, \
    ChannelType, IStartable
from enki.handler.serverhandler.machinehandler import OnBroadcastInterfaceHandler, \
    OnBroadcastInterfaceParsedData, OnFindInterfaceAddrHandler, QueryComponentIDHandler

logger = logging.getLogger(__name__)

ComponentID = int
ComponentInfo = OnBroadcastInterfaceParsedData


class ComponentStorage:
    """Хранилище для зарегестрированных компонентов.

    Часть компонентов запускаются в единственном числе (Machine, Interfaces,
    Logger, менеджеры), часть компонентов может иметь несколько инстансов
    (CellApp, BaseApp, LoginApp). Данный класс инкапсулирует способ хранения
    информации о компонентах и предоставляет простые методы регистрации доступа
    к информации о компонентах.
    """

    def __init__(self, app: Supervisor) -> None:
        self._app = app
        self._single_comp_info_by_type: dict[ComponentType, Optional[ComponentInfo]] = {
            ComponentType.MACHINE: None,
            ComponentType.LOGGER: None,
            ComponentType.INTERFACES: None,
            ComponentType.DBMGR: None,
            ComponentType.BASEAPPMGR: None,
            ComponentType.CELLAPPMGR: None,
        }
        self._multiple_comp_infos_by_type: dict[ComponentType, dict[ComponentID, ComponentInfo]] = {
            ComponentType.BASEAPP: {},
            ComponentType.CELLAPP: {},
            ComponentType.LOGINAPP: {},
        }
        self._comp_info_by_comp_id: dict[ComponentID, ComponentInfo] = {}

    def register_component(self, comp_info: ComponentInfo):
        comp_type = comp_info.component_type
        comp_id = comp_info.componentID
        if comp_type in self._single_comp_info_by_type:
            old_pd = self._single_comp_info_by_type.pop(comp_type, None)
            # При запуске компонентов KBEngine отправляется два сообщения
            # регистрации (пока не известно с какой целью). Поэтому, чтобы не
            # фонить в логах вводиться ещё доп. проверка на id компонента
            # (изменился ли он).
            if old_pd is not None and old_pd.componentID != comp_info.componentID:
                logger.info(
                    f'[{self}] The component "{comp_type}" is already registered. '
                    f'Delete its info (old componentID = "{old_pd.componentID}")'
                )
                self._comp_info_by_comp_id.pop(old_pd.componentID)
            self._single_comp_info_by_type[comp_type] = comp_info
        elif comp_type in self._multiple_comp_infos_by_type:
            # Пока просто добавить, т.к. неизвестно это, например, второй
            # CellApp или первый упал и переподключается.
            infos = self._multiple_comp_infos_by_type[comp_type]
            infos[comp_id] = comp_info
        else:
            raise NotImplementedError(f'The component "{comp_type}" cannot be registered')

        self._comp_info_by_comp_id[comp_id] = comp_info
        logger.info(f'[{self}] A new component has been registered '
                    f'(type = "{comp_type.name}", componentID = "{comp_id}"')

    def get_component_info(self, comp_type: ComponentType) -> list[ComponentInfo]:
        if comp_type in self._single_comp_info_by_type:
            res = self._single_comp_info_by_type[comp_type]
            if res is None:
                return []
            return [res.copy()]
        elif comp_type in self._multiple_comp_infos_by_type:
            infos = self._multiple_comp_infos_by_type[comp_type]
            return [info.copy() for info in infos.values()]
        return []

    def get_comp_info_by_comp_id(self, comp_id: ComponentID) -> ComponentInfo | None:
        res = self._comp_info_by_comp_id.get(comp_id)
        if res is None:
            return None
        return res.copy()

    def get_comp_infos(self) -> list[ComponentInfo]:
        """Возвращает копии информации обо всех зарегестрированных компонентах.

        Копии возвращаются, что избежать повреждения данных.
        """
        return [info.copy() for info in self._comp_info_by_comp_id.values()]

    def deregister_single_component(self, comp_type: ComponentType):
        infos = self.get_component_info(comp_type)
        if not infos:
            logger.warning(f'[{self}] The component "{comp_type}" cannot '
                            f'be deregistered. It has not been registered yet'
                            f'(componentType = "{comp_type}")')
            return
        info = infos[0]
        self._single_comp_info_by_type.pop(comp_type)
        self._comp_info_by_comp_id.pop(info.componentID)
        logger.info(
            f'[{self}] The component "{comp_type}" has been deregistered '
            f'(componentID = "{info.componentID}")'
        )

    def deregister_multiple_component(self, comp_id: ComponentID):
        info = self._comp_info_by_comp_id.get(comp_id)
        if info is None:
            logger.warning(f'[{self}] The component "{comp_id}" cannot '
                            f'be deregistered. It has not been registered yet')
            return
        self._multiple_comp_infos_by_type[info.component_type].pop(comp_id)
        self._comp_info_by_comp_id.pop(comp_id)
        logger.info(
            f'[{self}] The component "{info.component_type}" has been deregistered '
            f'(componentID = "{info.componentID}")'
        )

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'


class Supervisor(IStartable, IServerMsgReceiver):

    def __init__(self, udp_addr: AppAddr, tcp_addr: AppAddr) -> None:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        # Если пришло ими контейнера, нужно преобразовать его в ip адрес, т.к.
        # адрес компонента в KBEngine сохраняется и распространяется в
        # трансформированном виде socket.inet_aton
        udp_addr.host = server.get_real_host_ip(udp_addr.host)
        tcp_addr.host = server.get_real_host_ip(tcp_addr.host)

        self._udp_addr = udp_addr
        self._tcp_addr = tcp_addr
        self._internal_tcp_addr = AppAddr(tcp_addr.host, server.get_free_port())

        # Сервера для обслуживания соединений
        self._udp_server = UDPMsgServer(udp_addr, msgspec.app.machine.SPEC_BY_ID, self)
        self._tcp_server = TCPServer(tcp_addr, msgspec.app.machine.SPEC_BY_ID, self)
        self._internal_tcp_server = TCPServer(self._internal_tcp_addr, msgspec.app.machine.SPEC_BY_ID, self)

        # Уникальный идентификатор компонента, генерируемый Машиной
        self._component_id_cntr = 0

        # Хранилище данных о компонентах
        self._comp_storage = ComponentStorage(self)

        # Обработчики сообщений
        self._handlers = {
            msgspec.app.machine.onBroadcastInterface.id: _OnBroadcastInterfaceHandler(self),
            msgspec.app.machine.onQueryAllInterfaceInfos.id: _OnQueryAllInterfaceInfosHandler(self),
            msgspec.app.machine.queryComponentID.id: _QueryComponentIDHandler(self),
            msgspec.app.machine.onFindInterfaceAddr.id: _OnFindInterfaceAddrHandler(self),
            msgspec.app.machine.lookApp.id: _LookAppHandler(self),
        }

        # Сразу заполним информацию о Машине / Супервизоре
        info = ComponentInfo.get_empty()
        info.componentType = ComponentType.MACHINE.value
        info.componentID = self.generate_component_id()
        info.intaddr=kbemath.ip2int(self.internal_tcp_addr.host)
        info.intport=kbemath.port2int(self.internal_tcp_addr.port)
        info.extaddr=kbemath.ip2int(self.tcp_addr.host)
        info.extport=kbemath.port2int(self.tcp_addr.port)
        self._comp_storage.register_component(info)

        logger.info('[%s] Initialized', self)

    def generate_component_id(self) -> int:
        while True:
            self._component_id_cntr += 1
            comp_id = self._component_id_cntr
            if self._comp_storage.get_comp_info_by_comp_id(comp_id) is None:
                break

        return comp_id

    @property
    def comp_storage(self) -> ComponentStorage:
        return self._comp_storage

    @property
    def tcp_addr(self) -> AppAddr:
        return self._tcp_addr

    @property
    def udp_addr(self) -> AppAddr:
        return self._udp_addr

    @property
    def internal_tcp_addr(self) -> AppAddr:
        return self._internal_tcp_addr

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

    @property
    def is_alive(self) -> bool:
        return True

    async def on_receive_msg(self, msg: Message, channel: IChannel):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        handler = self._handlers.get(msg.id)
        if handler is None:
            logger.warning('[%s] There is no handler for the message %s', self, msg.id)
            return
        await handler.handle(msg, channel)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'


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
        logger.debug('[%s] %s', self, devonly.func_args_values())
        res = OnBroadcastInterfaceHandler().handle(msg)
        pd = res.result
        assert pd is not None
        self._app.comp_storage.register_component(pd)


class _OnQueryAllInterfaceInfosHandler(_SupervisorHandler):
    """Обработчик для сообщения Machine::onQueryAllInterfaceInfos .

    В ответ отправляем статистику обо всех зарегестрированных компонентах,
    плюс о себе (через сообщения Machine::onBroadcastInterface). Ответ нужно
    отправлять без оболочки сразу данными либо на запрошенный порт, либо в
    тоже tcp соединение.
    """

    async def handle(self, msg: Message, channel: TCPChannel):
        for info in self._app.comp_storage.get_comp_infos():
            resp_msg = Message(msgspec.app.machine.onBroadcastInterface, info.values())
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

        pd.componentID = self._app.generate_component_id()
        resp_msg = Message(msgspec.app.machine.queryComponentID, pd.values())
        data = self._serializer.serialize(resp_msg, only_data=True)

        # Адрес хоста, который отправил запрос на бродкаст нам не известен,
        # поэтому ответ отправляем тоже на бродкаст
        cb_addr = AppAddr('255.255.255.255', pd.callback_port)
        await channel.send_msg_content(data, cb_addr, ChannelType.BROADCAST)


class _OnFindInterfaceAddrHandler(_SupervisorHandler):
    """Обработчик для сообщения Machine::onFindInterfaceAddr .

    Запрос на сетевой адрес компонента. Сетевой адрес известен из сообщения
    Machine::OnBroadcastInterface, которое каждый компонент отправляет
    при старте.

    В оригинале ещё происходит фильтрация по uid (у меня задаётся UUID другим
    компонентам, у Супервизора его нет). Скорей всего это расчитано на случай,
    когда на хосте развёрнуто несколько кластеров. Но в данном случае докер
    изолирует кластеры друг от друга, в фильтрации по uid смысла нет.

    TODO: [2023-05-27 06:05 burov_alexey@mail.ru]:
    Так же в оригинале ещё проверяется живой ли компонент, отправляя ему lookApp.
    Это можно добавить, но не срочно, т.к. за здоровьем компонента должен
    следить Docker.
    """

    async def handle(self, msg: Message, channel: IChannel):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        res = OnFindInterfaceAddrHandler().handle(msg)
        pd = res.result
        cb_address = pd.callback_address

        comp_type = pd.find_component_type
        logger.info('[%s] Request to find "%s" component from "%s"', self,
                    comp_type.name, pd.component_type)
        infos = self._app.comp_storage.get_component_info(comp_type)

        if not infos:
            logger.warning('[%s] Requested not registered component "%s". '
                           'Return empty info', self, comp_type)
            info = OnBroadcastInterfaceParsedData.get_empty()
            infos = [info]
        # Компонентов одного типа может быть несколько, поэтому отправляем
        # по одному сообщению на каждый элемент в списке.
        for info in infos:
            # Возвращается копия инфы, а не ссылка, поэтому можем изменять
            info.componentIDEx = pd.componentID
            onBroadcastInterface_msg = Message(
                msgspec.app.machine.onBroadcastInterface, info.values()
            )
            data = self._serializer.serialize(onBroadcastInterface_msg, only_data=True)
            logger.info('[%s] The info of the "%s" component is found and sent to "%s"',
                        self, comp_type.name, cb_address)
            await channel.send_msg_content(data, cb_address, channel.type)


class _LookAppHandler(_SupervisorHandler):
    """Обработчик для сообщения Machine::lookApp.

    Используется для проверки живой компонент или нет.
    """

    async def handle(self, msg: Message, channel: TCPChannel):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        infos = self._app.comp_storage.get_component_info(ComponentType.MACHINE)
        # Данные компонента о самом себе должны заполняться при инициализации.
        assert infos, 'There is no info about self (logic error)'
        info = infos[0]
        resp_msg = Message(
            msgspec.custom.onLookApp,
            (info.componentType, info.componentID, ComponentState.RUN)
        )
        data = self._serializer.serialize(resp_msg, only_data=True)
        await channel.send_msg_content(
            data, channel.connection_info.src_addr, ChannelType.TCP
        )
