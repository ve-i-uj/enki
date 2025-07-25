"""Тесты сообщений компонента Supervisor."""

import asyncio
import socket
from asyncio import DatagramProtocol
from unittest import IsolatedAsyncioTestCase

import pytest

from enki.apps.supervisor.machine_msg_parser import (
    OnBroadcastInterfaceMsgParser,
    OnFindInterfaceAddrMsgParser,
    QueryComponentIDMsgParser,
)
from enki.apps.supervisor.supervisor_app import ComponentInfo, Supervisor
from enki.apps.supervisor.supervisor_msg_parser import OnLookAppMsgParser
from enki.kbeenum import ComponentState, ComponentType
from enki.kbetype.decoders.custom_decoders import KBEComponentId, KBEComponentType
from enki.msg import msgspec
from enki.msg.message import Message
from enki.msg.msg_serializer import MessageSerializer
from enki.net import server
from enki.net.addr import Addr


class RegisteredComponentsStorageTestCase(IsolatedAsyncioTestCase):
    """Тесты для хранилища зарегистрированных компонентов."""

    def setUp(self) -> None:
        super().setUp()
        self._app = Supervisor(
            Addr("0.0.0.0", server.get_free_port()),
            Addr("0.0.0.0", server.get_free_port()),
        )

    def tearDown(self):
        super().tearDown()
        if self._app.is_alive:
            self._app.stop()

    async def test_only_machine(self):
        """После запуска должна быть информация о Машине."""
        await self._app.start()
        storage = self._app.comp_storage
        infos = storage.get_component_info(ComponentType.MACHINE)
        assert len(infos) == 1
        info = infos[0]
        assert info.component_type == ComponentType.MACHINE
        assert info.componentID != 0
        assert info.internal_address == self._app._internal_tcp_addr
        assert info.external_address == self._app._tcp_addr

        assert storage.get_comp_info_by_comp_id(info.componentID) == info

    def test_register_logger(self):
        """Регистрируется Логгер."""
        storage = self._app.comp_storage
        logger_info = ComponentInfo.get_empty()
        logger_info.componentType = KBEComponentType(ComponentType.LOGGER.value)
        logger_info.componentID = KBEComponentId(self._app.generate_component_id())
        storage.register_component(logger_info)

        infos = storage.get_component_info(ComponentType.LOGGER)
        assert len(infos) == 1
        info = infos[0]
        assert info.component_type == ComponentType.LOGGER
        assert info.componentID == logger_info.componentID

        assert storage.get_comp_info_by_comp_id(info.componentID) == logger_info

    def test_register_logger_twice(self):
        """Регистрируется Логгер дважды.

        Ожидается, что данные заменяться в этом случае.
        """
        storage = self._app.comp_storage
        logger_info = ComponentInfo.get_empty()
        logger_info.componentType = KBEComponentType(ComponentType.LOGGER.value)
        logger_info.componentID = KBEComponentId(self._app.generate_component_id())
        storage.register_component(logger_info)

        logger_info_2 = logger_info.copy()
        logger_info_2.componentID = KBEComponentId(self._app.generate_component_id())
        storage.register_component(logger_info_2)

        infos = storage.get_component_info(ComponentType.LOGGER)
        assert len(infos) == 1
        info = infos[0]
        assert info.component_type == ComponentType.LOGGER
        assert info.componentID == logger_info_2.componentID

        assert storage.get_comp_info_by_comp_id(info.componentID) == logger_info_2

    def test_deregister_logger(self):
        """Отменяем регистрацию Логгера."""
        storage = self._app.comp_storage
        logger_info = ComponentInfo.get_empty()
        logger_info.componentType = KBEComponentType(ComponentType.LOGGER.value)
        logger_info.componentID = KBEComponentId(self._app.generate_component_id())
        storage.register_component(logger_info)

        storage.deregister_single_component(ComponentType.LOGGER)
        assert len(storage.get_component_info(ComponentType.LOGGER)) == 0
        assert storage.get_comp_info_by_comp_id(logger_info.componentID) is None


@pytest.fixture
async def started_supervisor():
    """Фикстура для запущенного Супервизора."""
    udp_addr = Addr("0.0.0.0", server.get_free_port())
    tcp_addr = Addr("0.0.0.0", server.get_free_port())
    supervisor = Supervisor(udp_addr, tcp_addr)
    res = await supervisor.start()
    assert res.success

    yield udp_addr, tcp_addr, supervisor

    supervisor.stop()


class TestSupervisor:
    """Тесты компонента Supervisor."""

    @pytest.mark.timeout(5)
    async def test_start_stop(self):
        """Проверяем, что Супервизор запускается и останавливается."""
        supervisor = Supervisor(
            Addr("0.0.0.0", server.get_free_port()),
            Addr("0.0.0.0", server.get_free_port()),
        )
        assert not supervisor.is_alive

        res = await supervisor.start()
        assert res.success
        assert supervisor.is_alive

        supervisor.stop()
        assert not supervisor.is_alive

    @pytest.mark.timeout(5)
    async def test_onBroadcastInterface(self, started_supervisor) -> None:
        """Проверка обработки сообщения Machine::onBroadcastInterface."""
        udp_addr, tcp_addr, supervisor = started_supervisor

        # Сериализованное Machine::onBroadcastInterface от Logger
        data = b"\x08\x00q\x00\xc7n\x00\x00root\x00\n\x00\x00\x00\x00\x00\x05\xd4\xeb8Od\x01\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xac\x19\x00\x03\xb9\xb1\xac\x19\x00\x03\xc5g\x00\xbb\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x1e\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd0\x84\x00\x00\x00\x00\x00\x00\xac\x19\x00\x03PK"
        serializer = MessageSerializer(msgspec.MachineMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(data))

        assert msg is not None
        assert msg.id == msgspec.machine.onBroadcastInterface.id
        assert not data_tail

        # Нет информации о Логгере
        assert not supervisor.comp_storage.get_component_info(ComponentType.LOGGER)

        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            DatagramProtocol,
            remote_addr=(udp_addr.host, udp_addr.port),
        )
        transport.sendto(data)

        await asyncio.sleep(0.2)

        # Появилась информацию о Логгере
        assert supervisor.comp_storage.get_component_info(ComponentType.LOGGER)

    @pytest.mark.timeout(5)
    async def test_lookApp(self, started_supervisor) -> None:
        """Проверка обработки сообщения Machine::lookApp."""
        udp_addr, tcp_addr, supervisor = started_supervisor

        # Сериализованное Machine::lookApp
        data = b"\n\x00"

        reader, writer = await asyncio.open_connection(*tcp_addr.to_tuple())
        writer.write(data)
        await writer.drain()

        resp_data = await reader.read(1024)
        serializer = MessageSerializer(msgspec.SupervisorMsgSpecByID)
        resp_msg, data_tail = serializer.deserialize_only_data(
            resp_data, msgspec.supervisor.onLookApp.id
        )
        assert resp_msg is not None
        assert not data_tail

        # Пришёл ответ и содержит то, что нужно
        assert resp_msg.name == "Supervisor::onLookApp"

        parser_res = OnLookAppMsgParser().parse(resp_msg)
        assert parser_res.success

        assert parser_res.result.component_type == ComponentType.MACHINE
        assert parser_res.result.component_id == 1
        assert parser_res.result.component_state == ComponentState.RUN

    @pytest.mark.timeout(5)
    async def test_onFindInterfaceAddr(self, started_supervisor) -> None:
        """Проверка обработки сообщения Machine::onFindInterfaceAddr.

        На сообщнение Machine::onFindInterfaceAddr нужно отдать
        Machine::onBroadcastInterface без оболочки на UDP адрес.
        """
        udp_addr, tcp_addr, supervisor = started_supervisor

        # Зарегестрируем Logger через сообщение
        # Сериализованное Machine::onBroadcastInterface
        data = b"\x08\x00q\x00\xc7n\x00\x00root\x00\n\x00\x00\x00\x00\x00\x05\xd4\xeb8Od\x01\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xac\x19\x00\x03\xb9\xb1\xac\x19\x00\x03\xc5g\x00\xbb\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x1e\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd0\x84\x00\x00\x00\x00\x00\x00\xac\x19\x00\x03PK"
        udp_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        udp_sock.sendto(data, ("0.0.0.0", udp_addr.port))

        await asyncio.sleep(0.2)

        # Данные Machine::onFindInterfaceAddr, которые отправляет DBMGR_TYPE,
        # чтобы узнать адрес LOGGER_TYPE.
        data = b"\x01\x00\x1f\x00\xb4 \x00\x00root\x00\x01\x00\x00\x00\x00\x00\x0c\xfb\x95_hd\n\x00\x00\x00\xac\x1b\x00\x07Q\x07"
        serializer = MessageSerializer(msgspec.MachineMsgSpecByID)
        msg, _ = serializer.deserialize(memoryview(data))
        assert msg is not None

        res = OnFindInterfaceAddrMsgParser().parse(msg)
        pd = res.result
        # Данные для отправки взяты из реального взаимодействия, поэтому нужно
        # адрес колбэка подменить на тот, где сейчас в тесте запущен udp-сервер
        udp_server_port = server.get_free_port()
        # Под копотом поменяется finderRecvPort
        pd.callback_address = Addr("0.0.0.0", udp_server_port)

        msg = Message(
            msgspec.machine.onFindInterfaceAddr.id,
            msgspec.machine.onFindInterfaceAddr.name,
            msgspec.machine.onFindInterfaceAddr.component_type,
            pd.values(),
        )
        # Это теперь обновлённый Machine::onFindInterfaceAddr с адресом
        # udp-сервера для тестов        data = serializer.serialize(msg)
        data = serializer.serialize(msg)

        # Запросим теперь себе на udp-сервер данные о Logger

        # Создаем UDP сервер
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(("0.0.0.0", udp_server_port))

        # Отправим запрос на Supervisor
        udp_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        udp_sock.sendto(data, ("0.0.0.0", udp_addr.port))

        await asyncio.sleep(0.2)

        # Supervisor в ответ должен отправть ответ на порт, указанный в
        # finderRecvPort
        data, _ = server_socket.recvfrom(4096)
        msg, data_tail = serializer.deserialize_only_data(
            data, msgspec.machine.onBroadcastInterface.id
        )
        assert msg is not None
        assert not data_tail

        onBroadcastInterface_res = OnBroadcastInterfaceMsgParser().parse(msg)
        assert onBroadcastInterface_res.success
        assert onBroadcastInterface_res.result.component_type == ComponentType.LOGGER

    async def test_queryComponentID(self, started_supervisor):
        """На сообщнение Machine::queryComponentID нужно отдать новый id компонента."""
        udp_addr, tcp_addr, supervisor = started_supervisor

        serializer = MessageSerializer(msgspec.MachineMsgSpecByID)

        # В этих данных ожидается, что ответ придёт на порт 40087. Данные
        # взяты от Интерфейсес к Машине.
        hex_data = "09001a000d0000000000000000000000859200009c97675400004d060000"
        data = bytes.fromhex(hex_data)

        # Нужно подменить порт на свободный порт из тестов
        req_msg, _ = serializer.deserialize(memoryview(data))
        assert req_msg is not None

        req_res = QueryComponentIDMsgParser().parse(req_msg)
        req_pd = req_res.result
        assert req_pd is not None

        req_pd.callback_port = server.get_free_port()
        data = serializer.serialize(
            Message.create(msgspec.machine.queryComponentID, req_pd.values())
        )

        # Открываем прослушку порта (как-будто на стороне Интерфейсес) и ждём ответа
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(("0.0.0.0", req_pd.callback_port))

        # Отправим запрос на Supervisor
        udp_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        udp_sock.sendto(data, ("0.0.0.0", udp_addr.port))

        await asyncio.sleep(0.2)

        # Supervisor в ответ должен отправть ответ на порт, указанный в сообщении
        resp_data, _ = server_socket.recvfrom(4096)
        resp_msg, data_tail = serializer.deserialize_only_data(
            resp_data, msgspec.machine.queryComponentID.id
        )
        assert resp_msg is not None
        assert not data_tail

        # В ответ отправляется тоже (как и в запросе) Machine::queryComponentID
        assert resp_msg.id == msgspec.machine.queryComponentID.id

        res = QueryComponentIDMsgParser().parse(resp_msg)
        assert res.success, res.text

        resp_pd = res.result
        assert resp_pd is not None
        # Это ответ тому же компоненту, что и запрашивал id
        assert resp_pd.component_type == req_pd.component_type
        # Id компонента был ноль, вернулся не ноль (т.е. Supervisor присвоил id)
        assert req_pd.componentID == 0
        assert resp_pd.componentID != 0
