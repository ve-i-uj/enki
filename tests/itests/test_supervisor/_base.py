"""Тест на получение Supervisor'ом Machine::onBroadcastInterface ."""

from enki.core import msgspec
from enki.app.appaddr import AppAddr
from enki.core.message import MessageSerializer
from enki.net import server

from enki.app.supervisor.supervisorapp import Supervisor

from unittest import IsolatedAsyncioTestCase


class SupervisorTestCase(IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        super().setUp()
        self._udp_port = server.get_free_port()
        self._tcp_port = server.get_free_port()
        self._supervisor_app = Supervisor(
            AppAddr('0.0.0.0', self._udp_port),
            AppAddr('0.0.0.0', self._tcp_port)
        )

        self._machine_serializer = MessageSerializer(msgspec.app.machine.SPEC_BY_ID)

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()
        await self._supervisor_app.stop()
