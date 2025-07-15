"""Тесты клиентов KBEngine-сообщений."""

import asyncio

import pytest

from enki.kbeenum import ComponentType
from enki.kbetype.basic_data_types import KBEBlob, KBEString
from enki.msg import msgspec
from enki.msg.message import Message
from enki.msg.msg_client import TcpMsgClient
from enki.msg.msg_descr import CompenentMsgSpecs  # noqa: TC001
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

            for resp in responses:
                writer.write(resp)
                await writer.drain()
            responses.clear()

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
    async def test_tcp_client_connected(self, tcp_msg_server):
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

    @pytest.mark.timeout(5)
    async def test_tcp_client_response(self, tcp_msg_server):
        """Проверяем, что tcp-клиент умеет получать ответ."""
        server, host, port, responses_data = tcp_msg_server

        # В ответ придут данные наугад, т.к. пока непонятно, что присылается в
        # ответ на hello (сейчас это Client::onCreatedProxies)
        data_1 = (
            b"\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00"
        )

        responses_data[:] = (data_1,)

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

        resp_msg = await client.waiting_for_response(120)
        assert resp_msg is not None
        assert resp_msg.id == msgspec.clientapp.onCreatedProxies.id
        assert resp_msg.name == "Client::onCreatedProxies"
        assert resp_msg.component == ComponentType.CLIENT

        client.stop()
        assert not client.is_alive

    @pytest.mark.timeout(5)
    async def test_tcp_client_multi_responses(self, tcp_msg_server):
        """Проверяем, что tcp-клиент умеет получать ответы (ответа будет 4)."""
        server, host, port, responses_data = tcp_msg_server

        # В ответ придут данные наугад, т.к. пока непонятно, что присылается в
        # ответ на hello (сейчас это Client::onCreatedProxies)
        data_1 = (
            b"\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00"
        )
        # Client::onEntityEnterWorld + Client::onUpdatePropertys (x 2)
        data_2 = b"\xfb\x01\x06\x00\x81\x08\x00\x00\x02\x00\xff\x01\n\x00\xcb\x00\x00\x00\x00\x05d\x00\x00\x00\xff\x01\n\x00\xcb\x00\x00\x00\x00\x07d\x00\x00\x00"

        responses_data[:] = (data_1, data_2)

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

        # Ждём первое сообщение. Сперва только оно
        resp_msg_1 = await client.waiting_for_response(120)
        assert resp_msg_1 is not None
        assert resp_msg_1.id == msgspec.clientapp.onCreatedProxies.id
        assert resp_msg_1.name == "Client::onCreatedProxies"
        assert resp_msg_1.component == ComponentType.CLIENT

        resp_msg_2 = await client.waiting_for_response(120)
        assert resp_msg_2 is not None
        assert resp_msg_2.id == msgspec.clientapp.onEntityEnterWorld.id
        assert resp_msg_2.name == "Client::onEntityEnterWorld"
        assert resp_msg_2.component == ComponentType.CLIENT

        resp_msg_3 = await client.waiting_for_response(120)
        assert resp_msg_3 is not None
        assert resp_msg_3.id == msgspec.clientapp.onUpdatePropertys.id
        assert resp_msg_3.name == "Client::onUpdatePropertys"
        assert resp_msg_3.component == ComponentType.CLIENT

        resp_msg_4 = await client.waiting_for_response(120)
        assert resp_msg_4 is not None
        assert resp_msg_4.id == msgspec.clientapp.onUpdatePropertys.id
        assert resp_msg_4.name == "Client::onUpdatePropertys"
        assert resp_msg_4.component == ComponentType.CLIENT

        client.stop()
        assert not client.is_alive
