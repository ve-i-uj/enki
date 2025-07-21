"""Тесты сообщений компонента Supervisor."""

from asyncio import DatagramProtocol
import asyncio
import socket
from unittest import IsolatedAsyncioTestCase

import pytest

from enki.components.supervisor.supervisorapp import ComponentInfo, Supervisor
from enki.kbeenum import ComponentType
from enki.kbetype.decoders.custom_decoders import KBEComponentId, KBEComponentTypeId
from enki.msg import msgspec
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
        logger_info.componentType = KBEComponentTypeId(ComponentType.LOGGER.value)
        logger_info.componentID = KBEComponentId(self._app._generate_component_id())
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
        logger_info.componentType = KBEComponentTypeId(ComponentType.LOGGER.value)
        logger_info.componentID = KBEComponentId(self._app._generate_component_id())
        storage.register_component(logger_info)

        logger_info_2 = logger_info.copy()
        logger_info_2.componentID = KBEComponentId(self._app._generate_component_id())
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
        logger_info.componentType = KBEComponentTypeId(ComponentType.LOGGER.value)
        logger_info.componentID = KBEComponentId(self._app._generate_component_id())
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
