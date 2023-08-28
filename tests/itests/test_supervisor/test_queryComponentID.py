"""Тест на получение Supervisor'ом Machine::onBroadcastInterface ."""

import asyncio
import socket

from enki.core import kbetype, msgspec
from enki.core.enkitype import AppAddr
from enki.core.message import Message, MessageSerializer
from enki.handler.serverhandler.machinehandler import QueryComponentIDHandler
from enki.net.server import UDPMsgServer, UDPServer
from enki.net import server
from enki.command.machine import QueryComponentIDCommand

from tools import msgreader

from ._base import SupervisorTestCase


class QueryComponentIDTestCase(SupervisorTestCase):

    async def test_response_to_queryComponentID(self):
        """На сообщнение Machine::queryComponentID нужно отдать новый id компонента."""
        res = await self._app.start()
        assert res.success

        serializer = MessageSerializer(msgspec.app.machine.SPEC_BY_ID)

        # В этим данных ожидается, что ответ придёт на порт 40087. Данные
        # взяты от Интерфейсес к Машине.
        hex_data = '09001a000d0000000000000000000000859200009c97675400004d060000'
        data = msgreader.normalize_wireshark_data(hex_data)
        req_msg, _ = serializer.deserialize(memoryview(data))
        assert req_msg is not None
        req_res = QueryComponentIDHandler().handle(req_msg)
        req_pd = req_res.result
        assert req_pd is not None
        req_pd.callback_port = server.get_free_port()
        data = serializer.serialize(
            Message(msgspec.app.machine.queryComponentID, req_pd.values())
        )

        # Открываем порт сервер (как-будто на сторое Интерфейсес) и ждём ответа
        future = asyncio.get_event_loop().create_future()

        class OneShotUDPServer(UDPServer):

            async def on_receive_data(self, data: memoryview, addr: AppAddr):
                future.set_result(data.tobytes())

        udp_server = OneShotUDPServer(AppAddr('0.0.0.0', req_pd.callback_port))
        res = await udp_server.start()
        assert res.success, res.text

        udp_client_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        udp_client_sock.sendto(data, ('0.0.0.0', self._udp_port))

        await future
        resp_data: bytes = future.result()

        msg, _ = serializer.deserialize_only_data(
            resp_data, msgspec.app.machine.queryComponentID
        )
        assert msg is not None
        assert msg.id == msgspec.app.machine.queryComponentID.id

        res = QueryComponentIDHandler().handle(msg)
        assert res.success, res.text
        resp_pd = res.result
        assert resp_pd is not None
        # Это ответ тому же компоненту, что и запрашивал id
        assert resp_pd.component_type == req_pd.component_type
        # Id компонента был ноль, вернулся не ноль (т.е. Supervisor присвоил id)
        assert req_pd.componentID == 0
        assert resp_pd.componentID != 0

    async def test_request_queryComponentID_by_command(self):
        """Запрос Machine::queryComponentID командой."""
        res = await self._app.start()
        assert res.success

        serializer = MessageSerializer(msgspec.app.machine.SPEC_BY_ID)

        # В этим данных ожидается, что ответ придёт на порт 40087. Данные
        # взяты от Интерфейсес к Машине.
        hex_data = '09001a000d0000000000000000000000859200009c97675400004d060000'
        data = msgreader.normalize_wireshark_data(hex_data)
        req_msg, _ = serializer.deserialize(memoryview(data))
        assert req_msg is not None
        req_res = QueryComponentIDHandler().handle(req_msg)
        req_pd = req_res.result
        assert req_pd is not None
        command = QueryComponentIDCommand(self._app.udp_addr, req_pd)
        res = await command.execute()
        assert res.success, res.text
        resp_pd = res.result
        assert resp_pd is not None
        # Это ответ тому же компоненту, что и запрашивал id
        assert resp_pd.component_type == req_pd.component_type
        # Id компонента был ноль, вернулся не ноль (т.е. Supervisor присвоил id)
        assert req_pd.componentID == 0
        assert resp_pd.componentID != 0
