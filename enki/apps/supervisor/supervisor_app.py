"""Компонент повторяющий функционал KBEngine-компонента Machine."""

from __future__ import annotations

import abc
import asyncio
import logging
from asyncio import Future
from typing import Generic, TypeAlias, TypeVar

from enki import msgspec
from enki.core import kbemath
from enki.kbeenum import ComponentState, ComponentType
from enki.kbetype.decoders.custom_decoders import (
    KBEComponentId,
    KBEComponentType,
    KBEIntAddr,
    KBEIntPort,
    KBEShutdownState,
)
from enki.misc import devonly
from enki.misc.result import Result
from enki.misc.startable import IStartable
from enki.msg.imsg import IClientMsgSender, IMsgBackChannel, IServerMsgReceiver
from enki.msg.message import Message
from enki.msg.msg_client import UdpMsgClient
from enki.msg.msg_descr import ComponentMsgSpecById, MsgSpecById
from enki.msg.msg_server import (
    TCPMsgBackChannel,
    TCPMsgServer,
    UDPMsgBackChannel,
    UDPMsgServer,
)
from enki.msg_parser.machine_msg_parser import (
    OnBroadcastInterfaceMsgParser,
    OnBroadcastInterfaceParsedData,
    OnFindInterfaceAddrMsgParser,
    OnQueryAllInterfaceInfosMsgParser,
    QueryComponentIDMsgParser,
)
from enki.msg_parser.supervisor_msg_parser import OnStopComponentMsgParser
from enki.msgspec import (
    BaseappMgrMsgSpecByID,
    BaseappMsgSpecByID,
    CellappMgrMsgSpecByID,
    CellappMsgSpecByID,
    DBMgrMsgSpecByID,
    InterfacesMsgSpecByID,
    LoggerMsgSpecByID,
    LoginappMsgSpecByID,
    MachineMsgSpecByID,
    SupervisorMsgSpecByID,
)
from enki.net import server
from enki.net.addr import Addr, Port

logger = logging.getLogger(__name__)

ComponentInfo: TypeAlias = OnBroadcastInterfaceParsedData


class _RegisteredComponentsStorage:
    """Хранилище для зарегистрированных компонентов.

    Часть компонентов запускаются в единственном числе (Machine, Interfaces,
    Logger, менеджеры), часть компонентов может иметь несколько инстансов
    (CellApp, BaseApp, LoginApp). Данный класс инкапсулирует способ хранения
    информации о компонентах и предоставляет простые методы регистрации доступа
    к информации о компонентах.
    """

    def __init__(self) -> None:
        self._single_comp_info_by_type: dict[
            ComponentType, ComponentInfo | None
        ] = {
            ComponentType.MACHINE: None,
            ComponentType.LOGGER: None,
            ComponentType.INTERFACES: None,
            ComponentType.DBMGR: None,
            ComponentType.BASEAPPMGR: None,
            ComponentType.CELLAPPMGR: None,
            ComponentType.LOGINAPP: None,
        }
        self._multiple_comp_infos_by_type: dict[
            ComponentType, dict[int, ComponentInfo]
        ] = {
            ComponentType.BASEAPP: {},
            ComponentType.CELLAPP: {},
        }
        self._comp_info_by_comp_id: dict[int, ComponentInfo] = {}
        self._shutting_down_comps: dict[int, ComponentInfo] = {}

    def register_component(self, comp_info: ComponentInfo) -> None:
        """Зарегистрировать компонент с кластере.

        Args:
            comp_info (ComponentInfo): информация о новом компоненте

        Raises:
            NotImplementedError: нереализованная логика

        """
        comp_type = comp_info.component_type
        comp_id = comp_info.componentID
        if comp_type in self._single_comp_info_by_type:
            old_pd = self._single_comp_info_by_type.get(comp_type)
            # При запуске компонентов KBEngine отправляется два сообщения
            # регистрации (пока не известно с какой целью). Поэтому, чтобы не
            # фонить в логах вводиться ещё доп. проверка на id компонента
            # (изменился ли он).
            if old_pd is not None and old_pd.componentID != comp_info.componentID:
                logger.info(
                    '[%s] The component "%s" is already registered. '
                    'Delete its info (old componentID = "%s")',
                    self,
                    comp_type.name,
                    old_pd.componentID,
                )
                self._comp_info_by_comp_id.pop(old_pd.componentID)
            self._single_comp_info_by_type[comp_type] = comp_info
        elif comp_type in self._multiple_comp_infos_by_type:
            # Пока просто добавить, т.к. неизвестно это, например, второй
            # CellApp или первый упал и переподключается.
            infos = self._multiple_comp_infos_by_type[comp_type]
            infos[comp_id] = comp_info
        else:
            err_text = f'The component "{comp_type}" cannot be registered'
            raise NotImplementedError(err_text)

        self._comp_info_by_comp_id[comp_id] = comp_info
        logger.info(
            (
                '[%s] A new component has been registered (type = "%s", '
                'componentID = "%s")'
            ),
            self,
            comp_type.name,
            comp_id,
        )

    def get_component_info(self, comp_type: ComponentType) -> list[ComponentInfo]:
        """Получить информацию о компонентах указанного типа.

        Для компонентов, которые могут существовать в единственном экземпляре,
        возвращает список из одного элемента. Для компонентов, которые могут
        иметь несколько экземпляров, возвращает список всех зарегистрированных
        компонентов этого типа. Возвращаются копии объектов, чтобы избежать
        изменения внутреннего состояния хранилища.

        Args:
            comp_type (ComponentType): тип компонента

        Returns:
            list[ComponentInfo]: список информации о компонентах указанного типа

        """
        if comp_type in self._single_comp_info_by_type:
            res = self._single_comp_info_by_type[comp_type]
            if res is None:
                return []
            return [res.copy()]

        if comp_type in self._multiple_comp_infos_by_type:
            infos = self._multiple_comp_infos_by_type[comp_type]
            return [info.copy() for info in infos.values()]

        return []

    def get_comp_info_by_comp_id(self, comp_id: int) -> ComponentInfo | None:
        """Получить информацию о компоненте по его идентификатору.

        Возвращает копию объекта ComponentInfo, чтобы избежать изменения
        внутреннего состояния хранилища.

        Args:
            comp_id (int): уникальный идентификатор компонента

        Returns:
            ComponentInfo | None: информация о компоненте или None, если компонент
                                с указанным ID не зарегистрирован

        """
        res = self._comp_info_by_comp_id.get(comp_id)
        if res is None:
            return None
        return res.copy()

    def get_comp_infos(self) -> list[ComponentInfo]:
        """Возвращает копии информации обо всех зарегестрированных компонентах.

        Копии возвращаются, что избежать повреждения данных.

        Returns:
            list[ComponentInfo]: информация о зарегистрированных компонентах

        """
        return [info.copy() for info in self._comp_info_by_comp_id.values()]

    def deregister_single_component(self, comp_type: ComponentType) -> None:
        """Удалить регистрацию компонента, который существует в единственном экземпляре.

        Метод удаляет информацию о компоненте из хранилища. Если компонент не был
        зарегистрирован, выводится предупреждение в лог. Для компонентов, которые
        могут иметь несколько экземпляров, следует использовать метод
        deregister_multiple_component.

        Args:
            comp_type (ComponentType): тип компонента для удаления регистрации

        """
        infos = self.get_component_info(comp_type)
        if not infos:
            logger.warning(
                '[%s] The component "%s" cannot '
                "be deregistered. It has not been registered yet"
                '(componentType = "%s")',
                self,
                comp_type,
                comp_type,
            )
            return

        info = infos[0]
        self._single_comp_info_by_type[comp_type] = None
        self._comp_info_by_comp_id.pop(info.componentID)
        logger.info(
            '[%s] The component "%s" has been deregistered (componentID = "%s")',
            self,
            comp_type.name,
            info.componentID,
        )

    def deregister_multiple_component(self, comp_id: KBEComponentId) -> None:
        """Удалить регистрацию одного из компонентов, у которых несколько экземпляров.

        Метод удаляет информацию о компоненте по его идентификатору. Если
        компонент с указанным ID не был зарегистрирован, выводится
        предупреждение в лог. Для компонентов, которые существуют в единственном
        экземпляре, следует использовать метод deregister_single_component.

        Args:
            comp_id (KBEComponentId): идентификатор компонента для удаления
                регистрации

        """
        info = self._comp_info_by_comp_id.get(comp_id)
        if info is None:
            logger.warning(
                '[%s] The component "%s" cannot '
                "be deregistered. It has not been registered yet",
                self,
                comp_id,
            )
            return

        self._multiple_comp_infos_by_type[info.component_type].pop(comp_id)
        self._comp_info_by_comp_id.pop(comp_id)
        logger.info(
            '[%s] The component "%s" has been deregistered (componentID = "%s")',
            self,
            info.component_type.name,
            info.componentID,
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"


class Supervisor(IStartable, IServerMsgReceiver):
    """Компонент повторяющий функционал KBEngine-компонента Machine."""

    def __init__(self, udp_addr: Addr, tcp_addr: Addr) -> None:
        """Конструктор KBEngine-компонента Supervisor.

        Args:
            udp_addr (ComponentAddr): адрес приёма UDP-подключений
            tcp_addr (ComponentAddr): адрес приёма TCP-подключений

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        self._server_is_running: Future[None] | None = None

        udp_addr = Addr(server.get_real_host_ip(udp_addr.ip_addr), udp_addr.port)
        tcp_addr = Addr(server.get_real_host_ip(tcp_addr.ip_addr), tcp_addr.port)

        self._udp_addr = udp_addr
        self._tcp_addr = tcp_addr

        # Компоненты, которым Supervisor отправляет сообщения
        self._comp_msg_specs: dict[ComponentType, ComponentMsgSpecById] = {
            comp_msg_spec_by_id.component: comp_msg_spec_by_id
            for comp_msg_spec_by_id in (
                LoggerMsgSpecByID,
                DBMgrMsgSpecByID,
                InterfacesMsgSpecByID,
                BaseappMgrMsgSpecByID,
                CellappMgrMsgSpecByID,
                BaseappMsgSpecByID,
                CellappMsgSpecByID,
                LoginappMsgSpecByID,
                SupervisorMsgSpecByID,
                MachineMsgSpecByID,
            )
        }

        # Сообщения, которые Supervisor обрабатывает. Добавим к сообщениям
        # Machine расширение от Supervisor
        spec_by_id: MsgSpecById = {}
        spec_by_id.update(MachineMsgSpecByID.msg_spec_by_id.copy())
        spec_by_id.update(SupervisorMsgSpecByID.msg_spec_by_id.copy())
        machine_msg_spec_by_id = ComponentMsgSpecById(
            ComponentType.MACHINE, spec_by_id
        )

        # Сервера для обслуживания соединений.
        self._udp_server = UDPMsgServer(
            self._udp_addr,
            ComponentType.SUPERVISOR,
            msg_receiver=self,
        )
        self._tcp_server = TCPMsgServer(
            self._tcp_addr,
            machine_msg_spec_by_id,
            msg_receiver=self,
            comp_msg_specs=self._comp_msg_specs,
        )

        # TODO: [burov_alexey@mail.ru 13.07.2025 16:53]
        # Пока не понял зачем он нужен. Возможно, для внутренней коммуникации
        # компонентов
        self._internal_tcp_addr = Addr(
            tcp_addr.ip_addr, Port(server.get_free_port())
        )
        self._internal_tcp_server = TCPMsgServer(
            self._internal_tcp_addr,
            machine_msg_spec_by_id,
            msg_receiver=self,
            comp_msg_specs=self._comp_msg_specs,
        )

        # Уникальный идентификатор компонента, генерируемый Машиной
        self._component_id_cntr = 0

        # Хранилище данных компонентов запущенного сервера
        self._comp_storage = _RegisteredComponentsStorage()

        # Обработчики сообщений
        self._handlers: dict[int, _SupervisorHandler] = {
            msgspec.machine.onBroadcastInterface.id: _OnBroadcastInterfaceHandler(
                self
            ),
            msgspec.machine.onQueryAllInterfaceInfos.id: _OnQueryAllInterfaceInfosHandler(
                self
            ),
            msgspec.machine.queryComponentID.id: _QueryComponentIDHandler(self),
            msgspec.machine.onFindInterfaceAddr.id: _OnFindInterfaceAddrHandler(
                self
            ),
            msgspec.machine.lookApp.id: _LookAppHandler(self),
            # Загрузка компонента не нужна, т.к. это делает инфрастуктура
            # Docker. В KBEngine не реализована обработка этого сообщения
            msgspec.machine.queryLoad.id: _NotImplementedMessageHandler(
                self,
                'Handler for the "Machine::queryLoad" message is not implemented',
            ),
            msgspec.machine.startserver.id: _NotImplementedMessageHandler(
                self,
                (
                    'Handler for the "Machine::startserver" message is not '
                    "implemented. Use Docker to start or stop services"
                ),
            ),
            msgspec.machine.stopserver.id: _NotImplementedMessageHandler(
                self,
                (
                    'Handler for the "Machine::stopserver" message is not '
                    "implemented. Use Docker to start or stop services"
                ),
            ),
            msgspec.machine.killserver.id: _NotImplementedMessageHandler(
                self,
                (
                    'Handler for the "Machine::killserver" message is not '
                    "implemented. Use Docker to start or stop services"
                ),
            ),
            # Это сообщение, скорей всего, только для отладки
            msgspec.machine.setflags.id: _NotImplementedMessageHandler(
                self,
                (
                    'Handler for the "Machine::setflags" message is not implemented yet'
                ),
            ),
            msgspec.machine.reqKillServer.id: _NotImplementedMessageHandler(
                self,
                (
                    'Handler for the "Machine::reqKillServer" message is not '
                    "implemented. Use Docker to start or stop services"
                ),
            ),
            # Это сообщение для Супервизора, что компонент начал останавливаться.
            # Сообщение отправляется из пускового скрипта в docker-контейнере.
            # На случай, если компонент сам не сообщит, что отключается.
            msgspec.supervisor.onStopComponent.id: _OnStopComponentHandler(self),
        }

        logger.info("[%s] Initialized", self)

    async def wait_until_stop(self) -> None:
        """Ожидание, когда сервер завершит работу.

        Returns:
            Future: фюче-объект, показывающий работает ли серевер

        """
        if self._server_is_running is None:
            return

        await self._server_is_running

    def generate_component_id(self) -> int:
        """Возвращает уникальный идентификатор для компонента.

        Returns:
            int: идентификтор компонента

        """
        while True:
            self._component_id_cntr += 1
            comp_id = self._component_id_cntr
            if self._comp_storage.get_comp_info_by_comp_id(comp_id) is None:
                break

        return comp_id

    @property
    def comp_storage(self) -> _RegisteredComponentsStorage:
        """Получить экзепляр хранилища зарегистрированных компонентов.

        Returns:
            _RegisteredComponentsStorage: экзепляр хранилища зарегистрированных
                компонентов

        """
        return self._comp_storage

    async def start(self) -> Result:
        """Запустить компонент Супервизор.

        Returns:
            Result: результат запуска компонента

        """
        res = await self._udp_server.start()
        if not res.success:
            return res

        res = await self._tcp_server.start()
        if not res.success:
            return res

        res = await self._internal_tcp_server.start()
        if not res.success:
            return res

        # Сразу заполним информацию о Машине / Супервизоре
        info = ComponentInfo.get_empty()
        info.componentType = KBEComponentType(ComponentType.MACHINE.value)
        info.componentID = KBEComponentId(self.generate_component_id())
        info.intaddr = KBEIntAddr(kbemath.ip2int(self._internal_tcp_addr.ip_addr))
        info.intport = KBEIntPort(kbemath.port2int(self._internal_tcp_addr.port))
        info.extaddr = KBEIntAddr(kbemath.ip2int(self._tcp_addr.ip_addr))
        info.extport = KBEIntPort(kbemath.port2int(self._tcp_addr.port))
        self._comp_storage.register_component(info)

        # Переменная, что сервер запущен
        self._server_is_running = Future()

        return Result(success=True, result=None)

    def stop(self) -> None:
        """Остановить компонент."""
        if not self.is_alive:
            return

        self._udp_server.stop()
        self._tcp_server.stop()
        self._internal_tcp_server.stop()

        if self._server_is_running is not None:
            self._server_is_running.set_result(None)

    @property
    def is_alive(self) -> bool:
        """Флаг запущен ли Супервизор.

        Returns:
            bool: Флаг запущен ли Супервизор

        """
        return (
            self._server_is_running is not None
            and not self._server_is_running.done()
        )

    def on_receive_msg(self, msg: Message, back_channel: IMsgBackChannel) -> None:
        """Колбэк на полученное сообщение.

        Args:
            msg (Message): полученное сервером сообщение
            back_channel (IMsgBackChannel): канал обратной связи

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        handler = self._handlers.get(msg.id)
        if handler is None:
            logger.warning(
                "[%s] There is no handler for the message %s", self, msg.id
            )
            return

        asyncio.create_task(handler.handle(msg, back_channel))  # noqa: RUF006

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"


_T_IMsgBackChannel = TypeVar("_T_IMsgBackChannel", bound=IMsgBackChannel)


class _SupervisorHandler(abc.ABC, Generic[_T_IMsgBackChannel]):
    """Абстрактный класс для обработчика сообщения компонента Supervisor."""

    def __init__(self, app: Supervisor) -> None:
        self._app = app

    @abc.abstractmethod
    async def handle(
        self, msg: Message, back_channel: _T_IMsgBackChannel
    ) -> None:
        """Обработать сообщение."""

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    __repr__ = __str__


class _OnBroadcastInterfaceHandler(_SupervisorHandler[UDPMsgBackChannel]):
    """Обработчик для сообщения Machine::onBroadcastInterface.

    Компонент запускаясь отправляет на Machine это сообщение, чтобы
    зарегистрироваться.
    """

    async def handle(
        self,
        msg: Message,
        back_channel: UDPMsgBackChannel,
    ) -> None:
        """Обработать сообщение Machine::onBroadcastInterface.

        Args:
            msg (Message): сообщение Machine::onBroadcastInterface
            back_channel (UDPMsgBackChannel): канал обратной связи

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        res = OnBroadcastInterfaceMsgParser().parse(msg)

        self._app.comp_storage.register_component(res.result)

        back_channel.close()


class _OnQueryAllInterfaceInfosHandler(_SupervisorHandler[UDPMsgBackChannel]):
    """Обработчик для сообщения Machine::onQueryAllInterfaceInfos .

    В ответ отправляем статистику о всех зарегестрированных компонентах,
    плюс о себе (через сообщения Machine::onBroadcastInterface). Ответ нужно
    отправлять без оболочки сразу данными либо на переданных порт, либо в
    тоже udp соединение.
    """

    async def handle(self, msg: Message, back_channel: UDPMsgBackChannel) -> None:
        """Обработать сообщение Machine::onQueryAllInterfaceInfos.

        Args:
            msg (Message): сообщение Machine::onBroadcastInterface
            back_channel (TCPMsgBackChannel): канал обратной связи по udp

        """
        logger.debug("[%s] %s ", self, devonly.func_args_values())

        # Порт для UDP ответа
        res = OnQueryAllInterfaceInfosMsgParser().parse(msg)
        assert res.success

        pd = res.result

        resp_msgs = []
        for info in self._app.comp_storage.get_comp_infos():
            resp_msg = Message(
                msgspec.machine.onBroadcastInterface.id,
                msgspec.machine.onBroadcastInterface.name,
                msgspec.machine.onBroadcastInterface.component_type,
                info.values(),
            )
            resp_msgs.append(resp_msg)

        if pd.callback_port.is_no_port():
            for resp_msg in resp_msgs:
                await back_channel.send_msg_content(resp_msg)

            return

        # Задан порт ответа. Ответ будут ждут на этом порту, а не на
        # клиентском сокете
        cb_addr = Addr(
            back_channel.conn_info.client_addr.ip_addr, pd.callback_port
        )
        client = UdpMsgClient(cb_addr, ComponentType.MACHINE)
        for resp_msg in resp_msgs:
            await client.send_msg_content(resp_msg)


class _QueryComponentIDHandler(_SupervisorHandler[UDPMsgBackChannel]):
    """Обработчик для сообщения Machine::queryComponentID .

    Через это сообщение компоненты запращивают себе id в кластере.

    В ответ вычисляется componentID и передаётся обратно UDP сообщением
    Machine::queryComponentID без обёртки на порт из поля finderRecvPort.
    Адрес для ответа - это источник запроса.
    """

    async def handle(self, msg: Message, back_channel: UDPMsgBackChannel) -> None:
        """Обработать сообщение Machine::queryComponentID.

        Args:
            msg (Message): сообщение Machine::queryComponentID
            back_channel (TCPMsgBackChannel): канал обратной связи по udp

        """
        logger.debug("[%s] %s ", self, devonly.func_args_values())

        res = QueryComponentIDMsgParser().parse(msg)
        assert res.result is not None
        pd = res.result

        pd.componentID = KBEComponentId(self._app.generate_component_id())

        resp_msg = Message(
            msgspec.machine.queryComponentID.id,
            msgspec.machine.queryComponentID.name,
            msgspec.machine.queryComponentID.component_type,
            pd.values(),
        )

        if Port(pd.callback_port).is_no_port():
            # Адрес хоста, который отправил запрос на бродкаст нам не известен,
            # поэтому ответ отправляем тоже на бродкаст (откуда пришло)
            await back_channel.send_msg_content(resp_msg)
            return

        client = UdpMsgClient(
            Addr(
                back_channel.conn_info.client_addr.ip_addr, Port(pd.callback_port)
            ),
            ComponentType.MACHINE,
        )
        await client.send_msg_content(resp_msg)


class _OnFindInterfaceAddrHandler(_SupervisorHandler[UDPMsgBackChannel]):
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

    В KBEngine не фильтруют по componentID, только по типу компонента и
    uid. Но при развёртке в Docker поле uid не имеет смысла (uid нужен
    для нескольких серверов от разных пользователей на одном хосте). Поэтому
    если нужно найти данные конктретного компонента, то нужно делать поиск уже
    в ответе среди компонентов одного типа.
    """

    async def handle(self, msg: Message, back_channel: UDPMsgBackChannel) -> None:
        """Обработать сообщение Machine::onFindInterfaceAddr.

        Args:
            msg (Message): сообщение Machine::onFindInterfaceAddr
            back_channel (UDPMsgBackChannel): канал обратной связи

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        res = OnFindInterfaceAddrMsgParser().parse(msg)
        req_pd = res.result

        find_component_type = req_pd.find_component_type

        logger.info(
            '[%s] Request from the "%s" to find the "%s" component',
            self,
            req_pd.component_type.name,
            find_component_type.name,
        )
        infos = self._app.comp_storage.get_component_info(find_component_type)

        # Это делается в Machine (отправляется пустое значение)
        if not infos:
            logger.warning(
                '[%s] Requested not registered component "%s". Return empty info',
                self,
                find_component_type,
            )
            info = OnBroadcastInterfaceParsedData.get_empty()
            info.componentIDEx = req_pd.componentID
            infos = [info]

        for info in infos:
            onBroadcastInterface_msg = Message.create(  # noqa: N806  # pylint: disable=invalid-name
                msgspec.machine.onBroadcastInterface,
                info.values(),
            )

            if req_pd.callback_address.port.is_no_port():
                # Адрес для обратной связи. Адрес есть в любом случае, но он может
                # придти с портом "ноль". Это означает ответ в клиентский udp-сокет.
                await back_channel.send_msg_content(onBroadcastInterface_msg)

                logger.info(
                    (
                        '[%s] The info of the "%s" component is found and sent to '
                        "the back channel"
                    ),
                    self,
                    find_component_type.name,
                )
            else:
                # Если ip адрес и порт заданы, нужно на них ответить
                client = UdpMsgClient(
                    req_pd.callback_address.copy(), ComponentType.MACHINE
                )
                await client.send_msg_content(onBroadcastInterface_msg)

                logger.info(
                    '[%s] The info of the "%s" component is found and sent to "%s"',
                    self,
                    find_component_type.name,
                    req_pd.callback_address,
                )
                client.close()


class _LookAppHandler(_SupervisorHandler[TCPMsgBackChannel]):
    """Обработчик для сообщения Machine::lookApp.

    Используется для проверки живой компонент или нет.
    """

    async def handle(self, msg: Message, back_channel: TCPMsgBackChannel) -> None:
        """Обработать сообщение Machine::lookApp.

        Args:
            msg (Message): сообщение Machine::lookApp
            back_channel (TCPMsgBackChannel): канал обратной связи

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        infos = self._app.comp_storage.get_component_info(ComponentType.MACHINE)
        # Данные компонента о самом себе должны заполняться при инициализации.
        assert infos, "There is no info about self (logic error)"
        info = infos[0]

        values = (
            info.componentType,
            info.componentID,
            KBEShutdownState(ComponentState.RUN),
        )
        resp_msg = Message(
            msgspec.machine.onLookApp.id,
            msgspec.machine.onLookApp.name,
            msgspec.machine.onLookApp.component_type,
            values,
        )
        await back_channel.send_msg_content(resp_msg)

        back_channel.close()


class _OnStopComponentHandler(_SupervisorHandler[UDPMsgBackChannel]):
    """Обработчик для сообщения Supervisor::onStopComponent.

    Уведомление Supervisor о том, что компоненту отправили сообщение на
    завершение. Компонент завершает исполнение и уведомляет об этом Супервизор.
    """

    async def handle(self, msg: Message, back_channel: UDPMsgBackChannel) -> None:
        """Обработать сообщение Supervisor::onStopComponent.

        Args:
            msg (Message): сообщение Supervisor::onStopComponent
            back_channel (UDPMsgBackChannel): канал обратной связи

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        res = OnStopComponentMsgParser().parse(msg)
        component_id = res.result.componentID

        comp_info = self._app.comp_storage.get_comp_info_by_comp_id(component_id)
        if comp_info is None:
            logger.warning(
                '[%s] There is no component with id "%s" (back_channel=%s)',
                self,
                component_id,
                back_channel,
            )
            return

        if comp_info.component_type == ComponentType.MACHINE:
            # Т.е. Супервизору пришло уведомление, что пора завершаться
            self._app.comp_storage.deregister_single_component(
                ComponentType.MACHINE
            )
            logger.info("[%s] Supervisor is stopping. Start finalization", self)
            self._app.stop()
            return

        logger.info(
            '[%s] The component "%s-%s" is stopping. Deregister it',
            self,
            comp_info.component_type.name,
            comp_info.componentID,
        )
        if comp_info.component_type.is_multiple_type():
            self._app.comp_storage.deregister_multiple_component(component_id)
        else:
            self._app.comp_storage.deregister_single_component(
                comp_info.component_type
            )


class _NotImplementedMessageHandler(_SupervisorHandler[TCPMsgBackChannel]):
    """Обработчик для Machine сообщений, которые не поддерживаются в Supervisor."""

    def __init__(self, app: Supervisor, err_text: str) -> None:
        super().__init__(app)
        self._err_text = err_text

    async def handle(self, msg: Message, back_channel: TCPMsgBackChannel) -> None:
        logger.warning(
            "[%s] The message handler is not implemented! %s",
            self,
            devonly.func_args_values(),
        )
        back_channel.close()
