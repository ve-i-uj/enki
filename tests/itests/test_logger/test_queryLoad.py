"""Integration tests for "queryLoad"."""

import unittest
import asynctest

from enki.net import msgspec
from enki.enkitype import AppAddr
from enki.net.command.logger import QueryLoadCommand
from enki.net.kbeclient.client import StreamClient


@unittest.skip('The Logger port is dynamic now')
class QueryLoadTestCase(asynctest.TestCase):

    async def test_ok(self):
        client = StreamClient(
            AppAddr('localhost', 45827),
            msgspec.app.logger.SPEC_BY_ID
        )
        assert (await client.start()).success

        cmd = QueryLoadCommand(client)
        client.set_msg_receiver(cmd)

        res = await cmd.execute()
        assert res.success, res.text
