"""Тест на получение Supervisor'ом Machine::onBroadcastInterface ."""

import asyncio
import socket
import asynctest

from enki.core import msgspec
from enki.core.enkitype import AppAddr
from enki.core.kbeenum import ComponentType
from enki.net.client import StreamClient
from enki.handler.serverhandler.machinehandler import OnBroadcastInterfaceHandler

from enki.app.supervisor.supervisorapp import Supervisor
from tools import msgreader

from ._base import SupervisorTestCase


class OnBroadcastInterfaceTestCase(SupervisorTestCase):

    async def test_register_logger(self):
        """Приложение сохраняет информацию по компоненту Logger."""
        res = await self._app.start()
        assert res.success

        # Информации о Логере нет в Супервизоре до запроса
        assert self._app.comp_storage.get_single_component_info(ComponentType.LOGGER_TYPE) is None

        onBroadcastInterface_hex_data = '08007100c76e0000726f6f74000a000000000005d4eb384f640100000000000000ffffffffffffffffffffffffac190003b9b1ac190003c56700bb000000000000000000000000201e010000000000000000000000000000000000000000000000000000000000d084000000000000ac190003504b'
        onBroadcastInterface_data = msgreader.normalize_wireshark_data(onBroadcastInterface_hex_data)

        req_msg, _ = self._machine_serializer.deserialize(memoryview(onBroadcastInterface_data))
        assert req_msg is not None
        req_pd = OnBroadcastInterfaceHandler().handle(req_msg).result
        assert req_pd is not None

        udp_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        udp_sock.sendto(onBroadcastInterface_data, ('0.0.0.0', self._udp_port))

        # В следующем тике будет обработка сообщения
        await asyncio.sleep(1)
        # Теперь компонент есть в данных Машины / Супервизора
        logger_info = self._app.comp_storage.get_single_component_info(ComponentType.LOGGER_TYPE)
        assert logger_info is not None
        assert logger_info.component_type == ComponentType.LOGGER_TYPE
        # Сохранён именно тот id, который сгенерировал и отправил Логер
        assert logger_info.componentID == req_pd.componentID
        # И есть информация о компоненте
