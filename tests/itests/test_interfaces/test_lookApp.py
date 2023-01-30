"""Integration tests for "QueryLoad"."""

import asynctest

from enki.net import msgspec
from enki.enkitype import AppAddr
from enki.net.command.interfaces import InterfacesLookAppCommand
from enki.net.kbeclient.client import StreamClient


class LookAppCommandTestCase(asynctest.TestCase):

    async def test_ok(self):
        client = StreamClient(
            AppAddr('localhost', 30099),
            msgspec.app.machine.SPEC_BY_ID
        )
        conn_res = await client.start()
        assert conn_res.success

        cmd = InterfacesLookAppCommand(client)
        client.set_msg_receiver(cmd)

        assert client.is_started
        res = await cmd.execute()
        assert res.success, res.text
