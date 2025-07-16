"""Тесты tcp и udp клиентов."""

import asyncio
from asyncio import DatagramProtocol

import pytest

from enki.net.addr import Addr
from enki.net.server import UDPServer, get_free_port, UDPServerOnReceiveDataCallback


class _UDPClientProtocol(DatagramProtocol):
    """Протокол для колбэков UDP-соединения."""

    def __init__(self, addr: Addr, data: bytes) -> None:
        """Конструктор.

        Args:
            addr (AppAddr): адрес энпоинта, которому отправятся данные по UDP
            data (bytes): данные для отправки

        """
        self._addr = addr
        self._data = data

    def connection_made(self, transport) -> None:
        transport.sendto(self._data, self._addr.to_tuple())


class TestUDPServer:
    """Тесты UDP сервера."""

    async def test_start_server(self):
        """Проверка, что сервер запускается."""
        received_data = []
        server_stopped = [False]

        def on_receive_data_cb(data: memoryview, addr: Addr):
            received_data.append(data)

        def on_end_receive_data_cb():
            server_stopped[0] = True

        server = UDPServer(
            Addr("0.0.0.0", get_free_port()),
            on_receive_data_cb=on_receive_data_cb,
            on_end_receive_data_cb=on_end_receive_data_cb,
        )

        assert not server.is_alive

        res = await server.start()
        assert res.success

        await asyncio.sleep(0.2)
        assert server.is_alive

        server.stop()
        await asyncio.sleep(0.2)
        assert not server.is_alive

        # Колбэк остановки был вызван
        assert server_stopped[0] is True
        # Сообщений не поступало
        assert not received_data

    async def test_server_received_data(self):
        """Проверка, что сервер принимает подключения."""
        received_data = []
        server_stopped = [False]

        def on_receive_data_cb(data: memoryview, addr: Addr):
            received_data.append(data)

        def on_end_receive_data_cb():
            server_stopped[0] = True

        server_addr = Addr("0.0.0.0", get_free_port())
        server = UDPServer(
            server_addr,
            on_receive_data_cb=on_receive_data_cb,
            on_end_receive_data_cb=on_end_receive_data_cb,
        )
        res = await server.start()
        assert res.success
        await asyncio.sleep(0.2)

        sent_data = b"test_data"

        loop = asyncio.get_running_loop()
        _transport, protocol = await loop.create_datagram_endpoint(
            lambda: _UDPClientProtocol(server_addr, sent_data),
            remote_addr=(server_addr.host, server_addr.port),
        )
        await asyncio.sleep(0.2)

        assert len(received_data) == 1
        assert received_data[0] == sent_data

        # Колбэк остановки не был вызван
        assert server_stopped[0] is False
        assert server.is_alive
