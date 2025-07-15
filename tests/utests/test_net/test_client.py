"""Тесты tcp и udp клиентов."""

import asyncio
from asyncio import DatagramProtocol

import pytest

from enki.net.addr import Addr
from enki.net.client import TCPClient, UDPClient
from enki.net.server import get_free_port


@pytest.fixture
async def tcp_server():
    """Фикстура UDP-сервера."""
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


class TestTCPClient:
    """Тесты TCP-клиента."""

    @pytest.mark.timeout(5)
    async def test_tcp_client_connect(self, tcp_server):
        """Проверка подключения клиента к tcp-серверу.

        Просто пробуем подключиться.
        """
        server, host, port, responses = tcp_server

        server_resps = []
        close_cd_is_called = [False]

        def on_receive_data_cb(data: bytes):
            server_resps.append(data)

        def on_end_receive_data_cb():
            close_cd_is_called[0] = True

        client = TCPClient(Addr(host, port), on_receive_data_cb, on_end_receive_data_cb)

        res = await client.start()
        assert res.success

        # Сервер примет подключение и закроет его после получения хоть чего.
        success = await client.send_data(b"123")
        assert success

        await asyncio.sleep(0.1)
        assert not client.is_alive

        # Колбэк сработал на закрытие соединения сервером
        assert close_cd_is_called[0] is True
        # Данные не отправлялись, поэтому и не получались
        assert not server_resps

    @pytest.mark.timeout(5)
    async def test_tcp_client_receive_responces(self, tcp_server):
        """Проверяем, что tcp-клиент умеет принимать ответы."""
        data_1 = b"\xff\x01\x0e\x00\x7f\x08\x00\x00\x00\x04\x02\x00\x00\x00\x00\x00\x00\x00\x00\x02\x7f\x08\x00\x00\xff\x01 \x00\x80\x08\x00\x00\x00\x08\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x00\x00\x00\t\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x00\x00\xf8\x01\x13\x00\x00\x00\x07\x00\xdd\x10\xffb\x80\x08\x00\x00Avatar\x00\xff\x01\xb1\x00\x80\x08\x00\x00\x00\x03\x01\x00\x00\x00\x00\x01\x81\xe5@D\x83\x00SC3#BD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04d\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x06d\x00\x00\x00\x00\x07\x00\x00\x00\x00\x00\x08\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x02\x00\x08\x04\xe9\x03\x00\x00\x08\x05\xc8\x01\x00\x00\x00\n\x07\x00\x00\x00\x80\x08\x00\x00\x04\x00\x02\x00\n\x04\xe9\x03\x00\x00\n\x05x\x03\x00\x00\x00\x0b\x00\x00\x00\x00\x00\x0c\x01\x00\x00\r\x81J]\x05\x00\x0e\x01\x00\x0f<\x00\x10\x07\x00\x00\x00Damkina\x00\x11\x00\x00\x00\x12\x01\x00\x00\x00\x00\x13\x00\x00\x14\x00\x00\x15\x00\x00\x00\x00\x00\x16\x00\x00\x00\x00\xfa\x01\n\x00\x80\x08\x00\x00\n\x01\t\x03\x00\x00\xff\x01 \x00\x80\x08\x00\x00\x00\x01\x81\xe5@D\x83\x00SC3#BD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfb\x01\x06\x00\x80\x08\x00\x00\x02\x00\xff\x01\n\x00\x80\x08\x00\x00\x00\x05d\x00\x00\x00\xff\x01\n\x00\x80\x08\x00\x00\x00\x07d\x00\x00\x00"
        data_2 = b"\xfa\x01\n\x00\x80\x08\x00\x00\x08\x01o\x00\x00\x00\xfa\x01\n\x00\x80\x08\x00\x00\x08\x01o\x00\x00\x00\xfa\x01\n\x00\x80\x08\x00\x00\n\x01x\x03\x00\x00A\x00\x1f\x00\x01\x00\x00\x00_mapping\x00spaces/xinshoucun\x00\x0c\x00\x1c\x00\x80\x08\x00\x00\x81\xe5@D\x83\x00SC3#BD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfd\x01\t\x00\x80\x08\x00\x00\x01\x00\x00\x00\x00"
        data_3 = b"\r\x00\x81\xe5@D\x83\x00SC3#BD\xff\x01t\x00\x04\x00\x00\x00\x00\x01\xd1\xd6KD|2SC\xd1\xa6AD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00;\xadi?\x00\x04d\x00\x00\x00\x00\x05d\x00\x00\x00\x00\x06d\x00\x00\x00\x00\x07d\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\n\xe901\x01\x00\x0b\n\x00\x0c2\x00\r\x0c\x00\x00\x00\xe8\x89\xbe\xe5\x85\x8b\xe6\x96\xaf\xe7\x90\x83\x00\x0e\x00\x00\x0f\x00\x00\x10\xe901\x01\x00\x11\x01\x00\x00\x00\xfb\x01\x06\x00\x04\x00\x00\x00\x05\x00\xff\x01S\x00\x01\x00\x00\x00\x00\x01\x8e\x01DDM\xf3RCq\x91CD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\xa0\xc40\xc0\x00\x04\x00\x00\x00\x00\x00\x05i\x9a\x98\x00\x00\x06\x0f\x00\x072\x00\x08\x0f\x00\x00\x00\xe6\x96\xb0\xe6\x89\x8b\xe6\x8e\xa5\xe5\xbe\x85\xe5\x91\x98\x00\ti\x9a\x98\x00\x00\n\x01\x00\x00\x00\xfb\x01\x06\x00\x01\x00\x00\x00\x06\x00"
        data_4 = b"\x1d\x00\r\x00\x00B\xc6KD3\xc2AD\xf4<\x0b\xbf"
        data_5 = b"\x1d\x00\r\x00\x00\xb3\xb5KD\x95\xddAD\xf4<\x0b\xbf"

        server, host, port, expected_responses = tcp_server
        expected_responses[:] = (data_1, data_2, data_3, data_4, data_5)

        server_resps = []
        close_cd_is_called = [False]

        def on_receive_data_cb(data: bytes):
            server_resps.append(data)

        def on_end_receive_data_cb():
            close_cd_is_called[0] = True

        client = TCPClient(Addr(host, port), on_receive_data_cb, on_end_receive_data_cb)

        res = await client.start()
        assert res.success

        success = await client.send_data(b"123")
        assert success

        await asyncio.sleep(1)
        assert client.is_alive

        assert b"".join(server_resps) == b"".join(expected_responses)
        assert close_cd_is_called[0] is False

        # Срабатывание колбэка окончания получения данных. Закрыто клиеном.
        client.stop()
        await asyncio.sleep(0.2)
        assert close_cd_is_called[0] is True


class UDPServerProtocol(DatagramProtocol):
    def __init__(self, received_data: list[bytes]):
        self._received_data = received_data
        self._transport = None

    def connection_made(self, transport):
        self._transport = transport

    def datagram_received(self, data: bytes, addr: tuple[str, int]):
        self._received_data.append(data)


@pytest.fixture
async def udp_server():
    """Фикстура UDP-сервера."""
    received_data: list[bytes] = []
    host, port = "0.0.0.0", get_free_port()

    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPServerProtocol(received_data), local_addr=(host, port)
    )

    try:
        yield host, port, received_data
    finally:
        transport.close()


class TestUDPClient:
    """Тесты UDP-клиента."""

    @pytest.mark.timeout(5)
    async def test_udp_client_send_data(self, udp_server):
        """Проверка отправки данных udp-клиентом."""
        host, port, received_data = udp_server

        client = UDPClient(Addr(host, port))

        # Client::onCreatedProxies
        data = b"\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00"
        success = await client.send_data(data)
        assert success

        # Подождём, когда данные дойдут
        await asyncio.sleep(1)

        assert received_data == [data]
