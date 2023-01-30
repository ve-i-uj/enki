"""Integration tests for "QueryLoad"."""

import socket

import asynctest

from enki import kbeenum
from enki.net import msgspec
from enki.enkitype import AppAddr
from enki.net.command.dbmgr import DBMgrLookAppCommand
from enki.net.command.machine import OnQueryAllInterfaceInfosCommand
from enki.net.kbeclient.client import StreamClient


class LookAppCommandTestCase(asynctest.TestCase):

    async def test_ok(self):
        machine_client = StreamClient(
            AppAddr('localhost', 20099),
            msgspec.app.machine.SPEC_BY_ID
        )
        assert (await machine_client.start()).success

        cmd = OnQueryAllInterfaceInfosCommand(
            client=machine_client,
            uid=0,
            username='123',
            finderRecvPort=0
        )
        machine_client.set_msg_receiver(cmd)
        res = await cmd.execute()

        dbmgr_port = socket.ntohs(
            res.get_info(kbeenum.ComponentType.DBMGR_TYPE)[0].intport
        )

        dbmgr_client = StreamClient(
            AppAddr('localhost', dbmgr_port),
            msgspec.app.machine.SPEC_BY_ID
        )
        conn_res = await dbmgr_client.start()
        assert conn_res.success

        cmd = DBMgrLookAppCommand(dbmgr_client)
        dbmgr_client.set_msg_receiver(cmd)

        assert dbmgr_client.is_started
        res = await cmd.execute()
        assert res.success, res.text
