"""Тест на получение Supervisor'ом Machine::onBroadcastInterface ."""

from enki.core.enkitype import AppAddr
from enki.net import server

from enki.app.supervisor.supervisorapp import Supervisor

from unittest import IsolatedAsyncioTestCase


class OnBroadcastInterfaceTestCase(IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        super().setUp()
        self._udp_port = server.get_free_port()
        self._tcp_port = server.get_free_port()
        self._app = Supervisor(
            AppAddr('0.0.0.0', self._udp_port),
            AppAddr('0.0.0.0', self._tcp_port)
        )

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()
        await self._app.stop()
