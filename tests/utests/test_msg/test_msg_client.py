"""Тесты клиентов KBEngine-сообщений."""

import asyncio

import pytest

from enki.kbetype.basic_data_types import KBEBlob, KBEString
from enki.msg import msgspec
from enki.msg.message import Message
from enki.msg.msg_client import TcpMsgClient
from enki.msg.msg_descr import CompenentMsgSpecs
from enki.msg.msgspec import ClienappMsgSpecByID, LoginappMsgSpecByID
from enki.net.addr import Addr
from enki.net.server import get_free_port


@pytest.fixture
async def tcp_msg_server():
    """Фикстура TCP-сервера для KBEngine-сообщений."""
    responses: list[bytes] = []

    async def handle_client(reader, writer):
        while True:
            data = await reader.read(1024)
            if not data:
                break

            if not responses:
                break

            for response in responses:
                writer.write(response)
                await writer.drain()

        writer.close()

    host, port = "0.0.0.0", get_free_port()
    server = await asyncio.start_server(handle_client, host, port)

    try:
        yield server, host, port, responses
    finally:
        server.close()


class TestTcpMsgClient:
    """Тесты tcp-клиета KBEngine-сообщений."""

    @pytest.mark.timeout(5)
    async def test_tcp_client_receive_responces(self, tcp_msg_server):
        """Проверяем, что tcp-клиент умеет подключаться и отправлять сообщения."""
        server, host, port, expected_responses = tcp_msg_server

        comp_msg_specs: CompenentMsgSpecs = {
            LoginappMsgSpecByID.component: LoginappMsgSpecByID,
            ClienappMsgSpecByID.component: ClienappMsgSpecByID,
        }
        client = TcpMsgClient(
            Addr(host, port),
            ClienappMsgSpecByID,
            comp_msg_specs,
        )

        res = await client.start()
        assert res.success

        kbe_version = KBEString("2.5.10")
        script_version = KBEString("0.1.0")
        encrypted_key = KBEBlob(b"")

        msg = Message(
            msgspec.loginapp.hello.id,
            msgspec.loginapp.hello.name,
            msgspec.loginapp.hello.component_type,
            (kbe_version, script_version, encrypted_key),
        )
        success = await client.send_msg(msg)
        assert success

        # После получения сообщения "сервер" закроет соединение. Нужно немного
        # подождать, чтобы клиент узнал об этом.
        await asyncio.sleep(1)

        assert not client.is_alive
