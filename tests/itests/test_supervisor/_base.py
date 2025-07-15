"""Тест на получение Supervisor'ом Machine::onBroadcastInterface ."""

from enki.core import msgspec
from enki.net.addr import Addr
from enki.core.message import MessageEncoder
from enki.net import server

from enki.app.supervisor.supervisorapp import Supervisor

from unittest import IsolatedAsyncioTestCase


class SupervisorTestCase(IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        super().setUp()
        self._udp_port = server.get_free_port()
        self._tcp_port = server.get_free_port()
        self._supervisor_app = Supervisor(
            Addr('0.0.0.0', self._udp_port),
            Addr('0.0.0.0', self._tcp_port)
        )

        self._machine_serializer = MessageEncoder(msgspec.app.machine.SPEC_BY_ID)

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()
        await self._supervisor_app.stop()
