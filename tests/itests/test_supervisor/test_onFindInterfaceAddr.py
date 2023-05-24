"""Тест на получение Supervisor'ом Machine::onFindInterfaceAddr ."""

import asyncio
import socket

from enki.core import msgspec
from enki.core.enkitype import AppAddr
from enki.core.kbeenum import ComponentType
from enki.core.message import Message, MessageSerializer
from enki.handler.serverhandler.machinehandler import OnBroadcastInterfaceHandler, OnFindInterfaceAddrHandler, QueryComponentIDHandler
from enki.net.channel import UDPChannel
from enki.net.client import UDPClient
from enki.net.inet import IServerMsgReceiver
from enki.net import server
from enki.net.server import UDPMsgServer, UDPServer
from enki.command.machine import OnFindInterfaceAddrCommand, QueryComponentIDCommand

from tools import msgreader

from ._base import SupervisorTestCase


class OnFindInterfaceAddrTestCase(SupervisorTestCase):

    async def test_response(self):
        """
        На сообщнение Machine::onFindInterfaceAddr нужно отдать
        Machine::onFindInterfaceAddr без оболочки на UDP адрес.
        """
        res = await self._app.start()
        assert res.success

        serializer = MessageSerializer(msgspec.app.machine.SPEC_BY_ID)

        # Нужно логер зарегестрировать через сообщение
        onBroadcastInterface_hex_data = '08007100c76e0000726f6f74000a000000000005d4eb384f640100000000000000ffffffffffffffffffffffffac190003b9b1ac190003c56700bb000000000000000000000000201e010000000000000000000000000000000000000000000000000000000000d084000000000000ac190003504b'
        onBroadcastInterface_data = msgreader.normalize_wireshark_data(onBroadcastInterface_hex_data)
        msg, _ = self._machine_serializer.deserialize(memoryview(onBroadcastInterface_data))
        assert msg is not None
        res = OnBroadcastInterfaceHandler().handle(msg)
        assert res.result is not None
        # Нужно изменить адрес в реальных данных на тестовый и запомнить его
        res.result.callback_address = AppAddr('1.2.3.4', 56789)
        logger_addr = res.result.callback_address

        client = UDPClient(self._app.udp_addr)
        await client.send(
            serializer.serialize(Message(msgspec.app.machine.onBroadcastInterface,
                                         res.result.values())
                                 )
        )

        # Данные, которые отправляет DBMGR_TYPE, чтобы узнать адрес LOGGER_TYPE.
        hex_data = '01001f00b4200000726f6f74000100000000000cfb955f68640a000000ac1b00075107'
        data = msgreader.normalize_wireshark_data(hex_data)
        req_msg, _ = serializer.deserialize(memoryview(data))
        assert req_msg is not None
        req_res = OnFindInterfaceAddrHandler().handle(req_msg)
        req_pd = req_res.result
        # Данные для отправки взяты из реального взаимодействия, поэтому нужно
        # адрес колбэка подменить на тот, где сейчас в тесте запущено приложение
        req_pd.callback_address = AppAddr('0.0.0.0', server.get_free_port())
        assert req_pd is not None

        command = OnFindInterfaceAddrCommand(self._app.udp_addr, req_pd)
        res = await command.execute()
        assert res.success, res.text

        resp_pd = res.result
        assert resp_pd is not None
        assert resp_pd.component_type == req_pd.find_component_type
        # Проверить, что пришёл адрес именно зарегестрированного логера
        assert resp_pd.callback_address == logger_addr
