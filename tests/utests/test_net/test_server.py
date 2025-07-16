"""Тесты tcp и udp клиентов."""

import asyncio
from asyncio import DatagramProtocol

import pytest

from enki.net.addr import Addr
from enki.net.server import UDPServer, get_free_port, UDPServerOnReceiveDataCallback


class TestUDPServer:
    """Тесты UDP сервера."""

    async def test_start_server(self):
        """Проверка, что сервер запускается и принимает подключения."""
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
