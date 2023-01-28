"""Integration tests for "OnQueryAllInterfaceInfos"."""

import asynctest

from enki.net import msgspec
from enki.enkitype import AppAddr
from enki.net.command.machine import OnQueryAllInterfaceInfosCommand
from enki.net.kbeclient.client import StreamClient


class OnQueryAllInterfaceInfosCommandTestCase(asynctest.TestCase):

    async def test_ok(self):
        client = StreamClient(
            AppAddr('localhost', 20099),
            msgspec.app.machine.SPEC_BY_ID
        )
        assert (await client.start()).success

        cmd = OnQueryAllInterfaceInfosCommand(
            client=client,
            uid=0,
            username='123',
            finderRecvPort=0
        )
        client.set_msg_receiver(cmd)

        res = await cmd.execute()
        assert res.success, res.text
        assert res.result.infos
