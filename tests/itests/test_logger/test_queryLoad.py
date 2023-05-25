"""Integration tests for "queryLoad"."""

import unittest
import asynctest

from enki.core import msgspec
from enki.core.enkitype import AppAddr


@unittest.skip('The Logger port is dynamic now')
class QueryLoadTestCase(asynctest.TestCase):

    async def test_ok(self):
        client = OneShotTCPClient(
            AppAddr('localhost', 45827),
            msgspec.app.logger.SPEC_BY_ID
        )
        assert (await client.start()).success

        cmd = QueryLoadCommand(client)
        client.set_msg_receiver(cmd)

        res = await cmd.execute()
        assert res.success, res.text
