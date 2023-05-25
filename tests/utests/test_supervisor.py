"""Тесты сообщений компонента Supervisor."""

import unittest

from enki.app.supervisor.supervisorapp import ComponentStorage, Supervisor, ComponentInfo
from enki.core.enkitype import AppAddr
from enki.core.kbeenum import ComponentType
from enki.net import server


class ComponentStorageTestCase(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self._app = Supervisor(
            AppAddr('0.0.0.0', server.get_free_port()),
            AppAddr('0.0.0.0', server.get_free_port())
        )

    def test_only_machine(self):
        """После инициализации должна быть информация о Машине."""
        storage = self._app.comp_storage
        info = storage.get_single_component_info(ComponentType.MACHINE)
        assert info is not None
        assert info.component_type == ComponentType.MACHINE
        assert info.componentID != 0
        assert info.internal_address == self._app.internal_tcp_addr
        assert info.external_address == self._app.tcp_addr

        assert storage.get_comp_info_by_comp_id(info.componentID) == info

    def test_register_logger(self):
        """Регистрируется Логгер."""
        storage = self._app.comp_storage
        logger_info = ComponentInfo.get_empty()
        logger_info.componentType = ComponentType.LOGGER.value
        logger_info.componentID = self._app.generate_component_id()
        storage.register_component(logger_info)

        info = storage.get_single_component_info(ComponentType.LOGGER)
        assert info is not None
        assert info.component_type == ComponentType.LOGGER
        assert info.componentID == logger_info.componentID

        assert storage.get_comp_info_by_comp_id(info.componentID) == logger_info

    def test_register_logger_twice(self):
        """Регистрируется Логгер дважды.

        Ожидается, что данные заменяться в этом случае.
        """
        storage = self._app.comp_storage
        logger_info = ComponentInfo.get_empty()
        logger_info.componentType = ComponentType.LOGGER.value
        logger_info.componentID = self._app.generate_component_id()
        storage.register_component(logger_info)

        logger_info_2 = logger_info.copy()
        logger_info_2.componentID = self._app.generate_component_id()
        storage.register_component(logger_info_2)

        info = storage.get_single_component_info(ComponentType.LOGGER)
        assert info is not None
        assert info.component_type == ComponentType.LOGGER
        assert info.componentID == logger_info_2.componentID

        assert storage.get_comp_info_by_comp_id(info.componentID) == logger_info_2

    def test_deregister_logger(self):
        """Отменяем регистрацию Логгера."""
        storage = self._app.comp_storage
        logger_info = ComponentInfo.get_empty()
        logger_info.componentType = ComponentType.LOGGER.value
        logger_info.componentID = self._app.generate_component_id()
        storage.register_component(logger_info)

        storage.deregister_single_component(ComponentType.LOGGER)
        assert storage.get_single_component_info(ComponentType.LOGGER) is None
        assert storage.get_comp_info_by_comp_id(logger_info.componentID) is None
