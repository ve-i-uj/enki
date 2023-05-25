"""Integration tests for "QueryLoad"."""

import asynctest

from enki.core import msgspec
from enki.core.enkitype import AppAddr

import unittest

# TODO: [2023-05-13 15:23 burov_alexey@mail.ru]:
# Машина не отвечает тем, кто находится не на её хосте
@unittest.skip('KBEngine bug')
class QueryLoadCommandTestCase(asynctest.TestCase):

    async def test_ok(self):
        client = OneShotTCPClient(
            AppAddr('localhost', 20099),
            msgspec.app.machine.SPEC_BY_ID
        )
        conn_res = await client.start()
        assert conn_res.success

        cmd = MachineLookAppCommand(client)
        client.set_msg_receiver(cmd)

        assert client.is_alive
        res = await cmd.execute()
        assert res.success, res.text
