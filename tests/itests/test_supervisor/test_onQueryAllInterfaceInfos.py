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

from ._base import SupervisorTestCase


class OnBroadcastInterfaceTestCase(SupervisorTestCase):

    async def test_about_self(self):
        """Приложение возвращает ответ о самом себе."""
        res = await self._app.start()
        assert res.success

        client = StreamClient(
            AppAddr('0.0.0.0', self._tcp_port), msgspec.app.machine.SPEC_BY_ID
        )
        res = await client.start()
        assert res.success, res.text
        cmd = OnQueryAllInterfaceInfosCommand(
            client=client,
            uid=0,
            username='123',
            finderRecvPort=0
        )
        client.set_msg_receiver(cmd)
        resp = await cmd.execute()
        assert resp.success, resp.text

        info = resp.result.infos[0]
        assert info.external_address == self._app.tcp_addr

