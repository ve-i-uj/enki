"""Тесты клиентов KBEngine-сообщений."""

import asyncio
from asyncio import DatagramProtocol, Future

import pytest

from enki import msgspec
from enki.core import kbemath
from enki.kbeenum import ComponentType, ShutdownState
from enki.kbetype.decoders.custom_decoders import (
    COMPONENT_ID,
    COMPONENT_TYPE,
    SHUTDOWN_STATE,
    KBEComponentId,
    KBEComponentType,
    KBEShutdownState,
)
from enki.kbetype.pytypes.basic_data_types import (
    KBEBlob,
    KBEInt32,
    KBEString,
    KBEUInt16,
)
from enki.msg.message import Message
from enki.msg.msg_client import (
    RawRespTcpMsgClient,
    RawRespUdpMsgClient,
    TcpMsgClient,
    UdpMsgClient,
)
from enki.msg.msg_descr import CompenentMsgSpecs  # noqa: TC001
from enki.msg.msg_serializer import MessageSerializer
from enki.msgspec import (
    ClientappMsgSpecByID,
    LoginappMsgSpecByID,
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
        server, host, port, expected_responses, conn_closed_future = (
            tcp_msg_server
        )

        client = TcpMsgClient(
            Addr(host, port),
            LoginappMsgSpecByID,
            ClientappMsgSpecByID,
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
        data_1 = b"\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00"

        responses_data[:] = (data_1,)

        comp_msg_specs: CompenentMsgSpecs = {
            LoginappMsgSpecByID.component: LoginappMsgSpecByID,
            ClientappMsgSpecByID.component: ClientappMsgSpecByID,
        }
        client = TcpMsgClient(
            Addr(host, port),
            LoginappMsgSpecByID,
            ClientappMsgSpecByID,
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
        data_1 = b"\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00"
        # Client::onEntityEnterWorld + Client::onUpdatePropertys (x 2)
        data_2 = b"\xfb\x01\x06\x00\x81\x08\x00\x00\x02\x00\xff\x01\n\x00\xcb\x00\x00\x00\x00\x05d\x00\x00\x00\xff\x01\n\x00\xcb\x00\x00\x00\x00\x07d\x00\x00\x00"

        responses_data[:] = (data_1, data_2)

        comp_msg_specs: CompenentMsgSpecs = {
            LoginappMsgSpecByID.component: LoginappMsgSpecByID,
            ClientappMsgSpecByID.component: ClientappMsgSpecByID,
        }
        client = TcpMsgClient(
            Addr(host, port),
            LoginappMsgSpecByID,
            ClientappMsgSpecByID,
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
    def __init__(self, received_data: list[tuple[bytes, tuple[str, int]]]):
        self._received_data = received_data
        self._transport = None

    def connection_made(self, transport):
        self._transport = transport

    def datagram_received(self, data: bytes, addr: tuple[str, int]):
        self._received_data.append((data, addr))


@pytest.fixture
async def _udp_msg_server():
    """Фикстура UDP-сервера."""
    received_data: list[tuple[bytes, tuple[str, int]]] = []
    host, port = "0.0.0.0", get_free_port()

    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: _UDPMsgServerProtocol(received_data), local_addr=(host, port)
    )

    try:
        yield host, port, received_data, protocol
    finally:
        transport.close()


@pytest.fixture
async def _broadcast_udp_server():
    """Фикстура UDP-сервера для тестирования бродкаста."""
    received_data: list[tuple[bytes, tuple[str, int]]] = []
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
        host, port, received_data, transport = _udp_msg_server

        comp_msg_specs: CompenentMsgSpecs = {
            LoginappMsgSpecByID.component: LoginappMsgSpecByID,
            ClientappMsgSpecByID.component: ClientappMsgSpecByID,
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

        server_msg_data = received_data[0][0]
        received_msg, data_tail = MessageSerializer(
            LoginappMsgSpecByID
        ).deserialize(memoryview(server_msg_data))
        # До сервера дошло неповреждённое сообщение
        assert received_msg == sent_msg

    @pytest.mark.timeout(5)
    async def test_udp_broadcast_client_send_msg(self, _broadcast_udp_server):
        """Проверяем, что udp-клиент умеет отправлять сообщения по бродкасту."""
        host, port, received_data = _broadcast_udp_server

        comp_msg_specs: CompenentMsgSpecs = {
            LoginappMsgSpecByID.component: LoginappMsgSpecByID,
            ClientappMsgSpecByID.component: ClientappMsgSpecByID,
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

        server_msg_data = received_data[0][0]
        received_msg, data_tail = MessageSerializer(
            LoginappMsgSpecByID
        ).deserialize(memoryview(server_msg_data))
        # До сервера дошло неповреждённое сообщение
        assert received_msg == sent_msg


class TestRawRespTcpMsgClient:
    """Тесты tcp-клиента KBEngine-сообщений с сырым ответом."""

    @pytest.mark.timeout(5)
    async def test_tcp_client_connected(self, tcp_msg_server):
        """Проверяем, что tcp-клиент умеет подключаться и отправлять сообщения."""
        server, host, port, expected_responses, conn_closed_future = (
            tcp_msg_server
        )

        client = RawRespTcpMsgClient(
            Addr(host, port),
            msgspec.clientapp.onCreatedProxies,
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

        client = RawRespTcpMsgClient(
            Addr(host, port),
            msgspec.supervisor.onLookApp,
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

        await asyncio.sleep(0.2)

        resp_msgs = []
        # Символический таймаут, т.к. ответ уже отправлен
        async for resp_msg in client.wait_and_iterate_responses(0.1):
            resp_msgs.append(resp_msg)

        assert resp_msg is not None
        assert resp_msg.id == msgspec.supervisor.onLookApp.id
        assert resp_msg.name == "Supervisor::onLookApp"
        assert resp_msg.component == ComponentType.SUPERVISOR

        client.stop()
        assert not client.is_alive

    @pytest.mark.timeout(5)
    async def test_tcp_client_multi_responses(self, tcp_msg_server, subtests):
        """Ответное когда в данных несколько сообщений."""
        server, host, port, responses_data, conn_closed_future = tcp_msg_server

        # Данные ответных сообщений (три ответа на ::lookApp)
        data_1 = b"\x08\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01"
        data_2 = b"\x08\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01"
        data_3 = b"\x08\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01"

        responses_data[:] = (data_1, data_2, data_3)

        client = RawRespTcpMsgClient(
            Addr(host, port),
            msgspec.supervisor.onLookApp,
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

        await asyncio.sleep(0.2)

        # В ответ приходит три ответа на lookApp
        resp_msgs: list[Message] = []
        async for resp_msg in client.wait_and_iterate_responses(0.5):
            resp_msgs.append(resp_msg)  # noqa: PERF401

        assert len(resp_msgs) == 3
        for resp_msg in resp_msgs:
            with subtests.test(resp_msg):
                assert resp_msg.name == msgspec.supervisor.onLookApp.name

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

            client = RawRespTcpMsgClient(
                Addr(host, port),
                msgspec.supervisor.onLookApp,
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

            resp_msgs: list[Message] = []
            async for resp_msg in client.wait_and_iterate_responses(0.1):
                resp_msgs.append(resp_msg)  # noqa: PERF401

            assert not resp_msgs
        finally:
            if server is not None:
                server.close()

        client.stop()
        assert not client.is_alive

    @pytest.mark.timeout(5)
    async def test_send_msg_without_start(self):
        """Проверяем отправку сообщения без старта клиента."""
        client = RawRespTcpMsgClient(
            Addr("localhost", 12345),
            msgspec.supervisor.onLookApp,
        )

        msg = Message(
            msgspec.machine.lookApp.id,
            msgspec.machine.lookApp.name,
            msgspec.machine.lookApp.component_type,
            (),
        )

        success = await client.send_msg(msg)
        assert not success


# Ответ на Machine::onQueryAllInterfaceInfos
# [
#     b"\xe8\x03\x00\x00leto\x00\x08\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\xec\x0b\x00\x00\x00\x00\xe8e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
#     b"\xc7n\x00\x00root\x00\n\x00\x00\x00\x00\x00\x05\xd4\xeb8Od\x01\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xac\x19\x00\x03\xb9\xb1\xac\x19\x00\x03\xc5g\x00\xbb\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x1e\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd0\x84\x00\x00\x00\x00\x00\x00\xac\x19\x00\x03PK",
# ]


class TestRawRespUdpMsgClient:
    """Тесты tcp-клиента KBEngine-сообщений с сырым ответом."""

    @pytest.mark.timeout(5)
    async def test_send_msg(self, _udp_msg_server):
        """Проверяем, что клиент умеет отправлять сообщения."""
        host, port, received_data, transport = _udp_msg_server

        client = RawRespUdpMsgClient(
            Addr(host, port),
            msgspec.clientapp.onCreatedProxies,
        )

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

        await asyncio.sleep(0.2)

        assert len(received_data) == 1
        assert (
            received_data[0][0]
            == b"\x04\x00\x11\x002.5.10\x000.1.0\x00\x00\x00\x00\x00"
        )

    @pytest.mark.timeout(5)
    async def test_udp_client_responses(self, _udp_msg_server, subtests):
        """Проверяем, что tcp-клиент умеет получать ответ (будет несколько ответов)."""
        host, port, received_data, server_protocol = _udp_msg_server

        uid = KBEInt32(0)
        username = KBEString("123")
        # Ноль означает, что ответ нужно отправлять в тот же UDP-сокет
        cb_port = 0
        finderRecvPort = KBEUInt16(kbemath.port2int(cb_port))  # noqa: F821

        msg = Message.create(
            msgspec.machine.onQueryAllInterfaceInfos,
            values=(uid, username, finderRecvPort),
        )
        client = RawRespUdpMsgClient(
            Addr(host, port),
            msgspec.machine.onQueryAllInterfaceInfos,
        )
        success = await client.send_msg(msg)
        assert success

        await asyncio.sleep(0.2)

        # А теперь запишем ответ в транспорт на сервере в это же соединение

        # Ответ на Machine::onQueryAllInterfaceInfos
        resp_chunks = [
            b"\xe8\x03\x00\x00leto\x00\x08\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\xa4\xa7\x00\x00\x00\x00\xa5\x99\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            b"\xc7n\x00\x00root\x00\n\x00\x00\x00\x00\x00\x05\xd4\xeb8Od\x01\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xac\x19\x00\x03\xb9\xb1\xac\x19\x00\x03\xc5g\x00\xbb\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x1e\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd0\x84\x00\x00\x00\x00\x00\x00\xac\x19\x00\x03PK",
        ]
        client_addr = received_data[0][1]
        for chunk in resp_chunks:
            server_protocol._transport.sendto(chunk, client_addr)

        await asyncio.sleep(0.2)

        # Ждём ответы со стороны клиента

        resp_msgs = []
        # Символический таймаут, т.к. ответ уже отправлен
        async for resp_msg in client.wait_and_iterate_responses(0.1):
            resp_msgs.append(resp_msg)

        assert len(resp_msgs) == 2
        for resp_msg in resp_msgs:
            with subtests.test(resp_msg):
                assert (
                    resp_msg.name == msgspec.machine.onQueryAllInterfaceInfos.name
                )

    @pytest.mark.timeout(5)
    async def test_udp_client_response_timeout(self, _udp_msg_server):
        """Проверяем обработку таймаута при ожидании ответа.

        Не будет ответа от "сервера, поэтому таймаут сработает."
        """
        host, port, received_data, server_protocol = _udp_msg_server

        client = RawRespUdpMsgClient(
            Addr(host, port),
            msgspec.supervisor.onLookApp,
        )

        msg = Message(
            msgspec.machine.lookApp.id,
            msgspec.machine.lookApp.name,
            msgspec.machine.lookApp.component_type,
            (),
        )
        success = await client.send_msg(msg)
        assert success

        await asyncio.sleep(0.2)
        # Данные на сервер пришли а ответа нет
        assert received_data

        resp_msgs: list[Message] = []
        async for resp_msg in client.wait_and_iterate_responses(0.1):
            resp_msgs.append(resp_msg)  # noqa: PERF401

        assert not resp_msgs
