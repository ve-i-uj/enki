"""Integration tests for "OnQueryAllInterfaceInfos"."""

import asynctest

from enki.core import msgspec
from enki.core.enkitype import AppAddr
from enki.command.machine import OnQueryAllInterfaceInfosCommand



class OnQueryAllInterfaceInfosCommandTestCase(asynctest.TestCase):

    async def test_ok(self):
        cmd = OnQueryAllInterfaceInfosCommand(
            addr=AppAddr('localhost', 20099),
            uid=0,
            username='123',
            finderRecvPort=0
        )
        res = await cmd.execute()
        assert res.success, res.text
        assert res.result.infos
