"""Тесты клиентов KBEngine-сообщений."""

import asyncio
from asyncio import DatagramProtocol

import pytest

from enki.kbeenum import ComponentType
from enki.kbetype.basic_data_types import KBEBlob, KBEString
from enki.msg import msgspec
from enki.msg.imsg import IServerMsgReceiver
from enki.msg.message import Message
from enki.msg.msg_server import (
    TCPMsgBackChannel,
    TCPMsgServer,
    UDPMsgBackChannel,
    UDPMsgServer,
)
from enki.msg.msg_descr import CompenentMsgSpecs  # noqa: TC001
from enki.msg.msg_serializer import MessageSerializer
from enki.msg.msgspec import ClienappMsgSpecByID, LoginappMsgSpecByID
from enki.net.addr import Addr
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
            ClienappMsgSpecByID.component: ClienappMsgSpecByID,
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
            ClienappMsgSpecByID.component: ClienappMsgSpecByID,
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
