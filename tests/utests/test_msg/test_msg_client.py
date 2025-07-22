"""Тесты клиентов KBEngine-сообщений."""

import asyncio
from asyncio import DatagramProtocol, Future

import pytest

from enki.kbeenum import ComponentType, ShutdownState
from enki.kbetype.basic_data_types import KBEBlob, KBEString
from enki.kbetype.decoders.custom_decoders import (
    COMPONENT_ID,
    COMPONENT_TYPE,
    SHUTDOWN_STATE,
    KBEComponentId,
    KBEComponentType,
    KBEShutdownState,
)
from enki.msg import msgspec
from enki.msg.message import Message
from enki.msg.msg_client import StreamRespTcpMsgClient, TcpMsgClient, UdpMsgClient
from enki.msg.msg_descr import CompenentMsgSpecs  # noqa: TC001
from enki.msg.msg_serializer import MessageSerializer
from enki.msg.msgspec import (
    ClienappMsgSpecByID,
    LoginappMsgSpecByID,
    MachineMsgSpecByID,
    SupervisorMsgSpecByID,
)
from enki.net.addr import Addr
from enki.net.server import get_free_port


@pytest.fixture
async def tcp_msg_server():
    """Фикстура TCP-сервера для KBEngine-сообщений."""
    responses: list[bytes] = []
    conn_closed_future: Future[None] = Future()

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
        await writer.wait_closed()
        conn_closed_future.set_result(None)

    host, port = "0.0.0.0", get_free_port()
    server = await asyncio.start_server(handle_client, host, port)

    try:
        yield server, host, port, responses, conn_closed_future
    finally:
        server.close()


class TestTcpMsgClient:
    """Тесты tcp-клиета KBEngine-сообщений."""

    @pytest.mark.timeout(5)
    async def test_tcp_client_connected(self, tcp_msg_server):
        """Проверяем, что tcp-клиент умеет подключаться и отправлять сообщения."""
        server, host, port, expected_responses, conn_closed_future = tcp_msg_server

        client = TcpMsgClient(
            Addr(host, port),
            LoginappMsgSpecByID,
            ClienappMsgSpecByID,
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
        await conn_closed_future

        assert not client.is_alive

    @pytest.mark.timeout(5)
    async def test_tcp_client_response(self, tcp_msg_server):
        """Проверяем, что tcp-клиент умеет получать ответ."""
        server, host, port, responses_data, conn_closed_future = tcp_msg_server

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
            LoginappMsgSpecByID,
            ClienappMsgSpecByID,
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
        server, host, port, responses_data, conn_closed_future = tcp_msg_server

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
            LoginappMsgSpecByID,
            ClienappMsgSpecByID,
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


class _UDPMsgServerProtocol(DatagramProtocol):
    def __init__(self, received_data: list[bytes]):
        self._received_data = received_data
        self._transport = None

    def connection_made(self, transport):
        self._transport = transport

    def datagram_received(self, data: bytes, addr: tuple[str, int]):
        self._received_data.append(data)


@pytest.fixture
async def _udp_msg_server():
    """Фикстура UDP-сервера."""
    received_data: list[bytes] = []
    host, port = "0.0.0.0", get_free_port()

    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: _UDPMsgServerProtocol(received_data), local_addr=(host, port)
    )

    try:
        yield host, port, received_data
    finally:
        transport.close()


@pytest.fixture
async def _broadcast_udp_server():
    """Фикстура UDP-сервера для тестирования бродкаста."""
    received_data: list[bytes] = []
    host, port = "0.0.0.0", get_free_port()

    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: _UDPMsgServerProtocol(received_data),
        local_addr=(host, port),
        allow_broadcast=True,
    )

    try:
        yield host, port, received_data
    finally:
        transport.close()


class TestUDPMsgClient:
    """Тесты udp-клиета KBEngine-сообщений."""

    @pytest.mark.timeout(5)
    async def test_udp_client_send_msg(self, _udp_msg_server):
        """Проверяем, что udp-клиент умеет отправлять сообщения."""
        host, port, received_data = _udp_msg_server

        comp_msg_specs: CompenentMsgSpecs = {
            LoginappMsgSpecByID.component: LoginappMsgSpecByID,
            ClienappMsgSpecByID.component: ClienappMsgSpecByID,
        }
        client = UdpMsgClient(
            Addr(host, port),
            comp_msg_specs,
        )

        # Просто для проверки отправляется по udp Loginapp::hello. В логике
        # движка такого поведения нет.
        kbe_version = KBEString("2.5.10")
        script_version = KBEString("0.1.0")
        encrypted_key = KBEBlob(b"")

        sent_msg = Message(
            msgspec.loginapp.hello.id,
            msgspec.loginapp.hello.name,
            msgspec.loginapp.hello.component_type,
            (kbe_version, script_version, encrypted_key),
        )
        success = await client.send_msg(sent_msg)
        assert success

        # Ждём получения на сервере и проверяем результат
        await asyncio.sleep(0.2)
        assert received_data

        server_msg_data = received_data[0]
        received_msg, data_tail = MessageSerializer(LoginappMsgSpecByID).deserialize(
            memoryview(server_msg_data)
        )
        # До сервера дошло неповреждённое сообщение
        assert received_msg == sent_msg

    @pytest.mark.timeout(5)
    async def test_udp_broadcast_client_send_msg(self, _broadcast_udp_server):
        """Проверяем, что udp-клиент умеет отправлять сообщения по бродкасту."""
        host, port, received_data = _broadcast_udp_server

        comp_msg_specs: CompenentMsgSpecs = {
            LoginappMsgSpecByID.component: LoginappMsgSpecByID,
            ClienappMsgSpecByID.component: ClienappMsgSpecByID,
        }
        client = UdpMsgClient(
            Addr("255.255.255.255", port),
            comp_msg_specs,
            broadcast=True,
        )

        # Просто для проверки отправляется по udp Loginapp::hello. В логике
        # движка такого поведения нет.
        kbe_version = KBEString("2.5.10")
        script_version = KBEString("0.1.0")
        encrypted_key = KBEBlob(b"")

        sent_msg = Message(
            msgspec.loginapp.hello.id,
            msgspec.loginapp.hello.name,
            msgspec.loginapp.hello.component_type,
            (kbe_version, script_version, encrypted_key),
        )
        success = await client.send_msg(sent_msg)
        assert success

        # Ждём получения на сервере и проверяем результат
        await asyncio.sleep(0.2)
        assert received_data

        server_msg_data = received_data[0]
        received_msg, data_tail = MessageSerializer(LoginappMsgSpecByID).deserialize(
            memoryview(server_msg_data)
        )
        # До сервера дошло неповреждённое сообщение
        assert received_msg == sent_msg


class TestStreamRespTcpMsgClient:
    """Тесты tcp-клиента KBEngine-сообщений с сырым ответом."""

    @pytest.mark.timeout(5)
    async def test_tcp_client_connected(self, tcp_msg_server):
        """Проверяем, что tcp-клиент умеет подключаться и отправлять сообщения."""
        server, host, port, expected_responses, conn_closed_future = tcp_msg_server

        client = StreamRespTcpMsgClient(
            Addr(host, port),
            msgspec.clientapp.onCreatedProxies,
            LoginappMsgSpecByID,
            ClienappMsgSpecByID,
        )

        assert not client.is_alive
        res = await client.start()
        assert res.success
        assert client.is_alive

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
        await conn_closed_future

        assert not client.is_alive

    @pytest.mark.timeout(5)
    async def test_tcp_client_response(self, tcp_msg_server):
        """Проверяем, что tcp-клиент умеет получать ответ."""
        server, host, port, responses_data, conn_closed_future = tcp_msg_server

        # Данные ответного сообщения (стрима без id сообщения и его длины)
        component_type = KBEComponentType(ComponentType.SUPERVISOR.value)
        component_id = KBEComponentId(1)
        shutdown_state = KBEShutdownState(ShutdownState.RUNNING.value)

        data = (
            COMPONENT_TYPE.encode(component_type)
            + COMPONENT_ID.encode(component_id)
            + SHUTDOWN_STATE.encode(shutdown_state)
        )
        responses_data[:] = [data]

        client = StreamRespTcpMsgClient(
            Addr(host, port),
            msgspec.supervisor.onLookApp,
            MachineMsgSpecByID,
            SupervisorMsgSpecByID,
        )

        res = await client.start()
        assert res.success

        msg = Message(
            msgspec.machine.lookApp.id,
            msgspec.machine.lookApp.name,
            msgspec.machine.lookApp.component_type,
            (),
        )
        success = await client.send_msg(msg)
        assert success

        resp_msg = await client.waiting_for_response(120)
        assert resp_msg is not None
        assert resp_msg.id == msgspec.supervisor.onLookApp.id
        assert resp_msg.name == "Supervisor::onLookApp"
        assert resp_msg.component == ComponentType.SUPERVISOR

        client.stop()
        assert not client.is_alive

    @pytest.mark.timeout(5)
    async def test_tcp_client_multi_responses(self, tcp_msg_server):
        """Ответное сообщение не будет получено, если в ответе больше данных, чем нужно."""
        server, host, port, responses_data, conn_closed_future = tcp_msg_server

        # Данные ответных сообщений
        data_1 = (
            b"\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00"
        )
        data_2 = b"\xfb\x01\x06\x00\x81\x08\x00\x00\x02\x00\xff\x01\n\x00\xcb\x00\x00\x00\x00\x05d\x00\x00\x00\xff\x01\n\x00\xcb\x00\x00\x00\x00\x07d\x00\x00\x00"

        responses_data[:] = (data_1, data_2)

        client = StreamRespTcpMsgClient(
            Addr(host, port),
            msgspec.supervisor.onLookApp,
            MachineMsgSpecByID,
            SupervisorMsgSpecByID,
        )

        res = await client.start()
        assert res.success

        msg = Message(
            msgspec.machine.lookApp.id,
            msgspec.machine.lookApp.name,
            msgspec.machine.lookApp.component_type,
            (),
        )
        success = await client.send_msg(msg)
        assert success

        # Ждём ответное сообщение
        resp_msg = await client.waiting_for_response(120)
        assert resp_msg is None

        client.stop()
        assert not client.is_alive

    @pytest.mark.timeout(5)
    async def test_tcp_client_response_timeout(self):
        """Проверяем обработку таймаута при ожидании ответа.

        Не будет ответа от "сервера, поэтому таймаут сработает."
        """
        server_future: Future[None] = Future()

        async def handle_client(reader, writer):
            await server_future

        host, port = "0.0.0.0", get_free_port()
        server = None
        try:
            server = await asyncio.start_server(handle_client, host, port)

            client = StreamRespTcpMsgClient(
                Addr(host, port),
                msgspec.supervisor.onLookApp,
                MachineMsgSpecByID,
                SupervisorMsgSpecByID,
            )

            res = await client.start()
            assert res.success

            msg = Message(
                msgspec.machine.lookApp.id,
                msgspec.machine.lookApp.name,
                msgspec.machine.lookApp.component_type,
                (),
            )
            success = await client.send_msg(msg)
            assert success

            # Ждём ответ с коротким таймаутом
            resp_msg = await client.waiting_for_response(0.1)
            assert resp_msg is None
        finally:
            if server is not None:
                server.close()

        client.stop()
        assert not client.is_alive

    @pytest.mark.timeout(5)
    async def test_send_msg_without_start(self):
        """Проверяем отправку сообщения без старта клиента."""
        client = StreamRespTcpMsgClient(
            Addr("localhost", 12345),
            msgspec.supervisor.onLookApp,
            MachineMsgSpecByID,
            SupervisorMsgSpecByID,
        )

        msg = Message(
            msgspec.machine.lookApp.id,
            msgspec.machine.lookApp.name,
            msgspec.machine.lookApp.component_type,
            (),
        )

        success = await client.send_msg(msg)
        assert not success
