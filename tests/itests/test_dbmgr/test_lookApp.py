"""Integration tests for "QueryLoad"."""

import socket

import asynctest

from enki.core import kbeenum
from enki.core import msgspec
from enki.core.enkitype import AppAddr
from enki.command.dbmgr import DBMgrLookAppCommand
from enki.command.machine import OnQueryAllInterfaceInfosCommand
from enki.net.client import StreamClient

import unittest

# TODO: [2023-05-13 15:03 burov_alexey@mail.ru]:
# Этот тест будет иметь смысл, когда компонент Интерефейсес будет запускаться
# в отдельном контейнере. Тогда его порт будет всегда фиксирован. Сейчас у
# него диапазон портов и порт выбирается динамически из диапозона.
@unittest.skip('The DBMgr port is dynamic now')
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

        assert dbmgr_client.is_alive
        res = await cmd.execute()
        assert res.success, res.text
