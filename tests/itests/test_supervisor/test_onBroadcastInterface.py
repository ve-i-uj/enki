"""Тест на получение Supervisor'ом Machine::onBroadcastInterface ."""

import asyncio
import socket
import asynctest

from enki.core import msgspec
from enki.core.enkitype import AppAddr
from enki.command.machine import OnQueryAllInterfaceInfosCommand
from enki.core.kbeenum import ComponentType
from enki.net.client import StreamClient

from enki.app.supervisor.supervisorapp import Supervisor
from tools import msgreader

from ._base import SupervisorTestCase


class OnBroadcastInterfaceTestCase(SupervisorTestCase):

    async def test_register_logger(self):
        """Приложение сохраняет информацию по компоненту Logger."""
        res = await self._app.start()
        assert res.success

        onBroadcastInterface_hex_data = '08007100c76e0000726f6f74000a000000000005d4eb384f640100000000000000ffffffffffffffffffffffffac190003b9b1ac190003c56700bb000000000000000000000000201e010000000000000000000000000000000000000000000000000000000000d084000000000000ac190003504b'
        onBroadcastInterface_data = msgreader.normalize_wireshark_data(onBroadcastInterface_hex_data)

        assert not self._app.components_infos

        udp_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        udp_sock.sendto(onBroadcastInterface_data, ('0.0.0.0', self._udp_port))

        # В следующем тике будет обработка сообщения
        await asyncio.sleep(1)
        assert ComponentType.LOGGER_TYPE in self._app.components_infos
