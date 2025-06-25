"""Integration tests for "OnQueryAllInterfaceInfos"."""

from enki.app.appaddr import AppAddr
from enki.command.machine import OnQueryAllInterfaceInfosCommand

from unittest import IsolatedAsyncioTestCase


class OnQueryAllInterfaceInfosCommandTestCase(IsolatedAsyncioTestCase):

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
