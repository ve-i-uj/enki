"""Тест на получение Supervisor'ом Machine::onBroadcastInterface ."""

import asyncio
import socket
import asynctest

from enki.core import msgspec
from enki.core.enkitype import AppAddr
from enki.core.message import MessageSerializer
from enki.command.machine import OnQueryAllInterfaceInfosCommand
from enki.core.kbeenum import ComponentType
from enki.core.message import Message
from enki.net.client import StreamClient
from enki.net import server

from enki.app.supervisor.supervisorapp import Supervisor


class OnBroadcastInterfaceTestCase(asynctest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self._udp_port = server.get_free_port()
        self._tcp_port = server.get_free_port()
        self._app = Supervisor(
            AppAddr('0.0.0.0', self._udp_port),
            AppAddr('0.0.0.0', self._tcp_port)
        )

    async def tearDown(self) -> None:
        super().tearDown()
        await self._app.stop()
"""Тест на получение Supervisor'ом Machine::onBroadcastInterface ."""

import asyncio
import socket
import asynctest

from enki.core.enkitype import AppAddr
from enki.net import server

from enki.app.supervisor.supervisorapp import Supervisor


class SupervisorTestCase(asynctest.TestCase):
    """Родительский класс для интеграционных тестов Супервизора."""

    def setUp(self) -> None:
        super().setUp()
        self._udp_port = server.get_free_port()
        self._tcp_port = server.get_free_port()
        self._app = Supervisor(
            AppAddr('0.0.0.0', self._udp_port),
            AppAddr('0.0.0.0', self._tcp_port)
        )
        self._machine_serializer = MessageSerializer(msgspec.app.machine.SPEC_BY_ID)

    async def tearDown(self) -> None:
        super().tearDown()
        await self._app.stop()
