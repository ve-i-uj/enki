"""Тесты tcp и udp клиентов."""

import asyncio
from asyncio import DatagramProtocol

import pytest

from enki.net.addr import Addr
from enki.net.conninfo import ConnInfo
from enki.net.server import TCPBackChannel, TCPServer, UDPServer, get_free_port


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

    @pytest.mark.timeout(5)
    async def test_start_stop_server(self):
        """Проверка, что сервер запускается."""
        received_data = []
        server_stopped = [False]

        class MyUDPServer(UDPServer):
            def on_receive_data_cb(self, data: memoryview, addr: Addr):
                received_data.append(data)

            def on_stop_receive_data(self):
                server_stopped[0] = True
                super().on_stop_receive_data()

        server = MyUDPServer(
            Addr("0.0.0.0", get_free_port()),
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

    @pytest.mark.timeout(5)
    async def test_server_received_data(self):
        """Проверка, что сервер принимает подключения."""
        received_data = []
        server_stopped = [False]

        class MyUDPServer(UDPServer):
            def on_receive_data(self, data: memoryview, addr: tuple[str, int]):
                received_data.append(data)

            def on_stop_receive_data(self):
                server_stopped[0] = True
                super().on_stop_receive_data()

        server_addr = Addr("0.0.0.0", get_free_port())
        server = MyUDPServer(
            server_addr,
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


class _UnderTestingTCPServer(TCPServer):
    """TCP сервер под тестирование (переопределены колбэки)."""

    def __init__(self, addr):
        super().__init__(addr)
        self.call_data_of_on_receive_client_data: list[
            tuple[memoryview, TCPBackChannel]
        ] = []
        self.call_data_of_on_end_receive_client_data = []

    def on_receive_client_data(
        self,
        data: memoryview,
        back_channel: TCPBackChannel,
    ) -> bool:
        self.call_data_of_on_receive_client_data.append((data, back_channel))
        return True

    def on_end_receive_client_data(self, conn_info: ConnInfo) -> None:
        self.call_data_of_on_end_receive_client_data.append(conn_info)


class TestTCPServer:
    """Тесты TCP сервера."""

    @pytest.mark.timeout(5)
    async def test_start_stop_server(self):
        """Проверяет, что сервер запускается."""
        server = _UnderTestingTCPServer(Addr("0.0.0.0", get_free_port()))
        assert not server.is_alive

        res = await server.start()
        assert res
        assert server.is_alive

        server.stop()
        await asyncio.sleep(0.2)

        assert not server.is_alive

    async def test_on_receive_client_data(self):
        """Соединение устанавливается и данные приходят в колбэк интерфейса."""
        server_host, server_port = "0.0.0.0", get_free_port()
        server = _UnderTestingTCPServer(Addr(server_host, server_port))
        res = await server.start()
        assert res.success

        # Теперь отправим что-нибудь tcp-клиентом

        reader, writer = await asyncio.open_connection(server_host, server_port)
        client_host, client_port = writer.transport.get_extra_info("sockname")

        data = b"some byte data"
        writer.write(data)
        await writer.drain()

        await asyncio.sleep(0.2)

        # На сервер пришли данные
        assert len(server.call_data_of_on_receive_client_data) == 1
        received_data, tcp_back_channel = (
            server.call_data_of_on_receive_client_data[0]
        )
        assert received_data == memoryview(data)

        # Канал обратной связи содержит нужную информацию
        assert isinstance(tcp_back_channel, TCPBackChannel)
        assert tcp_back_channel.connection_info.client_addr.to_tuple() == (
            client_host,
            client_port,
        )
        assert tcp_back_channel.connection_info.server_addr.to_tuple() == (
            server_host,
            server_port,
        )

    async def test_on_end_receive_client_data(self):
        """Соединение устанавливается и закрывается без отправки данных."""
        server_host, server_port = "0.0.0.0", get_free_port()
        server = _UnderTestingTCPServer(Addr(server_host, server_port))
        res = await server.start()
        assert res.success

        # Клиентское подключение
        reader, writer = await asyncio.open_connection(server_host, server_port)
        client_host, client_port = writer.transport.get_extra_info("sockname")

        # На сервер не пришли данные
        assert not server.call_data_of_on_receive_client_data

        # Закрываем соединение
        writer.close()
        await writer.wait_closed()

        await asyncio.sleep(0.2)

        # Есть срабатывание колбэка о том, что соединение закрыто. В колбэке
        # данные клиента.
        assert len(server.call_data_of_on_end_receive_client_data) == 1
        conn_info: ConnInfo = server.call_data_of_on_end_receive_client_data[0]
        assert conn_info.client_addr.to_tuple() == (
            client_host,
            client_port,
        )

    @pytest.mark.timeout(5)
    async def test_back_channel_send_data(self):
        """Соединение устанавливается и можно отправить ответ."""
        server_host, server_port = "0.0.0.0", get_free_port()
        server = _UnderTestingTCPServer(Addr(server_host, server_port))
        res = await server.start()
        assert res.success

        # Теперь отправим что-нибудь tcp-клиентом

        reader, writer = await asyncio.open_connection(server_host, server_port)
        client_host, client_port = writer.transport.get_extra_info("sockname")

        client_sent_data = b"some byte data"
        writer.write(client_sent_data)
        await writer.drain()

        await asyncio.sleep(0.2)

        # На сервер пришли данные
        assert len(server.call_data_of_on_receive_client_data) == 1
        server_received_data, tcp_back_channel = (
            server.call_data_of_on_receive_client_data[0]
        )
        assert server_received_data == memoryview(client_sent_data)

        # Канал обратной связи передан в колбэк. Используем его для отправки ответа
        assert isinstance(tcp_back_channel, TCPBackChannel)
        server_resp_data = b"response from the server"
        success = await tcp_back_channel.send_data(server_resp_data)
        assert success

        # Читаем ответ от сервера. Какие данные отправили в канал обратной
        # связи, те и пришли на клиент
        client_resp_data = await reader.read(1024)
        assert client_resp_data == server_resp_data

        # Закрываем клиентское соединение
        writer.close()
        await writer.wait_closed()

        await asyncio.sleep(0.2)

        # Есть срабатывание колбэка о том, что соединение закрыто. Канал
        # закрылся, данные нельзя отправить.
        assert len(server.call_data_of_on_end_receive_client_data) == 1
        assert await tcp_back_channel.send_data(server_resp_data) is False
