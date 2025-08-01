"""Тесты клиентов KBEngine-сообщений."""

import asyncio

import pytest

from enki import settings
from enki.kbeenum import ComponentType
from enki.kbetype.pytypes.basic_data_types import KBEInt32, KBEString
from enki import msgspec
from enki.msg.imsg import IMsgBackChannel, IServerMsgReceiver
from enki.msg.message import Message
from enki.msg.msg_descr import CompenentMsgSpecs  # noqa: TC001
from enki.msg.msg_server import (
    TCPMsgBackChannel,
    TCPMsgServer,
    UDPMsgBackChannel,
    UDPMsgServer,
)
from enki.msgspec import ClientappMsgSpecByID, LoginappMsgSpecByID
from enki.net.addr import Addr, Port
from enki.net.server import get_free_port


class TestTcpMsgServer:
    """Тесты tcp-сервера KBEngine-сообщений."""

    @pytest.mark.timeout(5)
    async def test_start_stop_server(self):
        """Проверяет, что сервер запускается."""

        class ServerMsgReceiver(IServerMsgReceiver):
            def on_receive_msg(
                self, msg: Message, back_channel: TCPMsgBackChannel
            ) -> None:
                pass

        msg_receiver = ServerMsgReceiver()
        comp_msg_specs: CompenentMsgSpecs = {
            ClientappMsgSpecByID.component: ClientappMsgSpecByID,
        }

        server = TCPMsgServer(
            Addr("0.0.0.0", get_free_port()),
            LoginappMsgSpecByID,
            msg_receiver,
            comp_msg_specs,
        )
        assert not server.is_alive

        res = await server.start()
        assert res
        assert server.is_alive

        server.stop()
        await asyncio.sleep(0.2)

        assert not server.is_alive

    @pytest.mark.timeout(5)
    async def test_on_receive_msg(self):
        """Проверка, что сервер получает сообщения."""
        received_msgs = []

        class ServerMsgReceiver(IServerMsgReceiver):
            def on_receive_msg(
                self, msg: Message, back_channel: TCPMsgBackChannel
            ) -> None:
                received_msgs.append((msg, back_channel))

        msg_receiver = ServerMsgReceiver()
        comp_msg_specs: CompenentMsgSpecs = {
            ClientappMsgSpecByID.component: ClientappMsgSpecByID,
        }

        server = TCPMsgServer(
            Addr("0.0.0.0", get_free_port()),
            LoginappMsgSpecByID,
            msg_receiver,
            comp_msg_specs,
        )
        res = await server.start()
        assert res

        # Теперь отправим что-нибудь tcp-клиентом

        server_host, server_port = server.served_addr.to_tuple()
        reader, writer = await asyncio.open_connection(server_host, server_port)
        client_host, client_port = writer.transport.get_extra_info("sockname")

        # Это "Loginapp::hello"
        sent_data = b"\x04\x00\x11\x002.5.10\x000.1.0\x00\x00\x00\x00\x00"
        writer.write(sent_data)
        await writer.drain()

        await asyncio.sleep(0.2)

        # На сервер пришло сообщение
        assert len(received_msgs) == 1
        msg, tcp_msg_back_channel = received_msgs[0]
        assert isinstance(msg, Message)
        assert isinstance(tcp_msg_back_channel, TCPMsgBackChannel)
        assert msg.id == msgspec.loginapp.hello.id

        # Канал обратной связи содержит нужную информацию
        assert tcp_msg_back_channel.conn_info.client_addr.to_tuple() == (
            client_host,
            client_port,
        )
        assert tcp_msg_back_channel.conn_info.server_addr.to_tuple() == (
            server_host,
            server_port,
        )

    @pytest.mark.timeout(5)
    async def test_back_channel_send_msg(self):
        """Проверка отправки ответного сообщения."""
        received_msgs = []

        class ServerMsgReceiver(IServerMsgReceiver):
            def on_receive_msg(
                self, msg: Message, back_channel: TCPMsgBackChannel
            ) -> None:
                received_msgs.append((msg, back_channel))

        msg_receiver = ServerMsgReceiver()
        comp_msg_specs: CompenentMsgSpecs = {
            ClientappMsgSpecByID.component: ClientappMsgSpecByID,
        }

        server = TCPMsgServer(
            Addr("0.0.0.0", get_free_port()),
            LoginappMsgSpecByID,
            msg_receiver,
            comp_msg_specs,
        )
        res = await server.start()
        assert res

        # Теперь отправим что-нибудь tcp-клиентом

        server_host, server_port = server.served_addr.to_tuple()
        reader, writer = await asyncio.open_connection(server_host, server_port)
        client_host, client_port = writer.transport.get_extra_info("sockname")

        # Это "Loginapp::hello"
        sent_data = b"\x04\x00\x11\x002.5.10\x000.1.0\x00\x00\x00\x00\x00"
        writer.write(sent_data)
        await writer.drain()

        await asyncio.sleep(0.2)

        # На сервер пришло сообщение
        assert len(received_msgs) == 1
        msg, tcp_msg_back_channel = received_msgs[0]
        assert isinstance(msg, Message)
        assert isinstance(tcp_msg_back_channel, TCPMsgBackChannel)

        # Подготовим ответ на это сообщение
        values = (
            KBEString("STRING_1"),
            KBEString("STRING_2"),
            KBEString("STRING_3"),
            KBEString("STRING_4"),
            KBEInt32(1),
        )
        server_resp_msg = Message(
            msgspec.clientapp.onHelloCB.id,
            msgspec.clientapp.onHelloCB.name,
            msgspec.clientapp.onHelloCB.component_type,
            values,
        )

        # Отправка ответного сообщения в канал
        success = await tcp_msg_back_channel.send_msg(server_resp_msg)
        assert success

        # Читаем ответ от сервера. Какие данные отправили в канал обратной
        # связи, те и пришли на клиент
        # Это сериализованный Client::onHelloCB
        server_resp_msg_data = b"\t\x02(\x00STRING_1\x00STRING_2\x00STRING_3\x00STRING_4\x00\x01\x00\x00\x00"
        client_resp_data = await reader.read(1024)
        assert client_resp_data == server_resp_msg_data

        # Закрываем клиентское соединение
        writer.close()
        await writer.wait_closed()
        await asyncio.sleep(0.2)

    @pytest.mark.timeout(5)
    async def test_on_receive_msg_in_two_chunks(self):
        """Проверка, что сервер получает сообщение, если оно приходит в двух пакетах."""
        received_msgs = []

        class ServerMsgReceiver(IServerMsgReceiver):
            def on_receive_msg(
                self, msg: Message, back_channel: TCPMsgBackChannel
            ) -> None:
                received_msgs.append((msg, back_channel))

        msg_receiver = ServerMsgReceiver()
        comp_msg_specs: CompenentMsgSpecs = {
            ClientappMsgSpecByID.component: ClientappMsgSpecByID,
        }

        server = TCPMsgServer(
            Addr("0.0.0.0", get_free_port()),
            LoginappMsgSpecByID,
            msg_receiver,
            comp_msg_specs,
        )
        res = await server.start()
        assert res

        # Теперь уменьшим размер вычитывемых сервером данных и получим
        # сообщение, отправленное двумя пакетами
        sent_data_1 = b"\x04\x00\x11\x002.5.10"
        sent_data_2 = b"\x000.1.0\x00\x00\x00\x00\x00"
        server._TCP_CHUNK_SIZE = len(sent_data_1)

        server_host, server_port = server.served_addr.to_tuple()
        reader, writer = await asyncio.open_connection(server_host, server_port)
        client_host, client_port = writer.transport.get_extra_info("sockname")

        # Отправляем первый чанк
        writer.write(sent_data_1)
        await writer.drain()
        await asyncio.sleep(0.2)

        # Отправляем второй чанк
        writer.write(sent_data_2)
        await writer.drain()
        await asyncio.sleep(0.2)

        # На сервер пришло сообщение
        assert len(received_msgs) == 1
        msg, tcp_msg_back_channel = received_msgs[0]
        assert isinstance(msg, Message)
        assert isinstance(tcp_msg_back_channel, TCPMsgBackChannel)
        assert msg.id == msgspec.loginapp.hello.id

        # Канал обратной связи содержит нужную информацию
        assert tcp_msg_back_channel.conn_info.client_addr.to_tuple() == (
            client_host,
            client_port,
        )
        assert tcp_msg_back_channel.conn_info.server_addr.to_tuple() == (
            server_host,
            server_port,
        )


class TestUdpMsgServer:
    """Тесты udp-сервера KBEngine-сообщений."""

    @pytest.mark.timeout(5)
    async def test_start_stop_server(self):
        """Проверяет, что сервер запускается."""

        class ServerMsgReceiver(IServerMsgReceiver):
            def on_receive_msg(
                self, msg: Message, back_channel: UDPMsgBackChannel
            ) -> None:
                pass

        msg_receiver = ServerMsgReceiver()
        comp_msg_specs: CompenentMsgSpecs = {
            ClientappMsgSpecByID.component: ClientappMsgSpecByID,
        }

        server = UDPMsgServer(
            Addr("0.0.0.0", get_free_port()),
            ComponentType.LOGINAPP,
            msg_receiver,
        )
        assert not server.is_alive

        res = await server.start()
        assert res
        assert server.is_alive

        server.stop()
        await asyncio.sleep(0.2)

        assert not server.is_alive

    @pytest.mark.timeout(5)
    async def test_on_receive_msg(self):
        """Проверка, что сервер получает сообщения."""
        received_msgs = []

        class ServerMsgReceiver(IServerMsgReceiver):
            def on_receive_msg(
                self, msg: Message, back_channel: UDPMsgBackChannel
            ) -> None:
                received_msgs.append((msg, back_channel))

        msg_receiver = ServerMsgReceiver()
        comp_msg_specs: CompenentMsgSpecs = {
            ClientappMsgSpecByID.component: ClientappMsgSpecByID,
        }

        server = UDPMsgServer(
            Addr("0.0.0.0", Port(get_free_port())),
            ComponentType.LOGINAPP,
            msg_receiver,
        )
        res = await server.start()
        assert res

        # Теперь отправим что-нибудь udp-клиентом

        server_host, server_port = server.served_addr.to_tuple()

        loop = asyncio.get_running_loop()

        # Создаем UDP-клиент
        transport, protocol = await loop.create_datagram_endpoint(
            asyncio.DatagramProtocol, remote_addr=(server_host, server_port)
        )
        client_host, client_port = transport.get_extra_info("sockname")

        # Это "Loginapp::hello"
        sent_data = b"\x04\x00\x11\x002.5.10\x000.1.0\x00\x00\x00\x00\x00"
        transport.sendto(sent_data)
        transport.close()

        await asyncio.sleep(0.2)

        # На сервер пришло сообщение
        assert len(received_msgs) == 1
        msg, tcp_msg_back_channel = received_msgs[0]
        assert isinstance(msg, Message)
        assert isinstance(tcp_msg_back_channel, UDPMsgBackChannel)
        assert msg.id == msgspec.loginapp.hello.id

        # Канал обратной связи содержит нужную информацию
        assert tcp_msg_back_channel.conn_info.client_addr.to_tuple() == (
            client_host,
            client_port,
        )
        assert tcp_msg_back_channel.conn_info.server_addr.to_tuple() == (
            server_host,
            server_port,
        )

    @pytest.mark.timeout(5)
    async def test_back_channel_send_msg(self):
        """Проверка отправки ответного сообщения через канал обратной связи.

        По обратной связи можно только отправить udp сообщение на тот же
        клиентский сокет.
        """
        received_msgs = []

        class ServerMsgReceiver(IServerMsgReceiver):
            def on_receive_msg(
                self, msg: Message, back_channel: UDPMsgBackChannel
            ) -> None:
                # Нужно сразу ответ отправлять, т.к. у UDP канал закроется после
                # выхода из колбэка
                received_msgs.append((msg, back_channel))

                async def send_to_addr(udp_msg_back_channel):
                    # Отправка сообщения через канал обратной связи
                    assert isinstance(udp_msg_back_channel, UDPMsgBackChannel)

                    # Подготовим ответ на это сообщение
                    values = (
                        KBEString("STRING_1"),
                        KBEString("STRING_2"),
                        KBEString("STRING_3"),
                        KBEString("STRING_4"),
                        KBEInt32(1),
                    )
                    server_resp_msg = Message(
                        msgspec.clientapp.onHelloCB.id,
                        msgspec.clientapp.onHelloCB.name,
                        msgspec.clientapp.onHelloCB.component_type,
                        values,
                    )

                    # Отправка ответного сообщения в канал, но другому адресу
                    success = await back_channel.send_msg(
                        server_resp_msg,
                    )
                    assert success
                    await asyncio.sleep(0.2)

                # Колбэк на приём синхронный. Но нужна задача на асинхронную
                # отправку
                asyncio.create_task(send_to_addr(back_channel))

        msg_receiver = ServerMsgReceiver()
        comp_msg_specs: CompenentMsgSpecs = {
            ClientappMsgSpecByID.component: ClientappMsgSpecByID,
        }

        server = UDPMsgServer(
            Addr("0.0.0.0", Port(get_free_port())),
            ComponentType.LOGINAPP,
            msg_receiver,
        )
        res = await server.start()
        assert res

        # Второй udp-сервер для приёма ответного сообщения

        other_server_receive_msgs_data = []

        class UDPProtocol(asyncio.DatagramProtocol):
            def datagram_received(self, data, addr):
                # Второй UDP сервер получил сообщение, которое переслали
                other_server_receive_msgs_data.append(data)

        # Теперь отправим что-нибудь udp-клиентом

        server_host, server_port = server.served_addr.to_tuple()
        # Создаем UDP-клиент
        loop = asyncio.get_running_loop()
        client_transport, protocol = await loop.create_datagram_endpoint(
            UDPProtocol, remote_addr=(server_host, server_port)
        )
        # Это "Loginapp::hello"
        sent_data = b"\x04\x00\x11\x002.5.10\x000.1.0\x00\x00\x00\x00\x00"
        client_transport.sendto(sent_data)

        await asyncio.sleep(0.2)

        # Дальше идёт пересыл в "обработчике" оригинального UDP-сервера
        await asyncio.sleep(0.2)

        # Смотрим отправились ли данные на другой сервер
        assert len(other_server_receive_msgs_data) == 1
        client_transport.close()

        # Это сериализованный Client::onHelloCB
        server_resp_msg_data = b"\t\x02(\x00STRING_1\x00STRING_2\x00STRING_3\x00STRING_4\x00\x01\x00\x00\x00"
        assert other_server_receive_msgs_data[0] == server_resp_msg_data
