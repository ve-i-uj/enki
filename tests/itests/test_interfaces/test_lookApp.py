"""Integration tests for "QueryLoad"."""

import asynctest

from enki.core import msgspec
from enki.core.enkitype import AppAddr
from enki.command.interfaces import InterfacesLookAppCommand
from enki.net.client import StreamClient

import unittest


# TODO: [2023-05-13 15:03 burov_alexey@mail.ru]:
# Этот тест будет иметь смысл, когда компонент Интерефейсес будет запускаться
# в отдельном контейнере. Тогда его порт будет всегда фиксирован. Сейчас у
# него диапазон портов и порт выбирается динамически из диапозона.
@unittest.skip('The Interfaces port is dynamic now')
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
