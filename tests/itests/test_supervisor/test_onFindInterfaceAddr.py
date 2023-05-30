"""Тест на получение Supervisor'ом Machine::onFindInterfaceAddr ."""

import asyncio
import multiprocessing
import socket
import time

from enki.core import msgspec, utils
from enki.core.enkitype import AppAddr
from enki.core.kbeenum import ComponentType
from enki.core.message import Message, MessageSerializer
from enki.handler.serverhandler.machinehandler import OnBroadcastInterfaceHandler, OnBroadcastInterfaceParsedData, OnFindInterfaceAddrHandler, OnFindInterfaceAddrParsedData, QueryComponentIDHandler
from enki.net.channel import UDPChannel
from enki.net.client import UDPClient
from enki.net.inet import IServerMsgReceiver
from enki.net import server
from enki.net.server import UDPMsgServer, UDPServer
from enki.command.machine import OnFindInterfaceAddrTCPCommand, OnFindInterfaceAddrUDPCommand, QueryComponentIDCommand

from tools import msgreader

from ._base import SupervisorTestCase


class OnFindInterfaceAddrTestCase(SupervisorTestCase):

    async def test_find_Logger(self):
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
                                         res.result.values())))

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

        cmd = OnFindInterfaceAddrUDPCommand(self._app.udp_addr, req_pd)
        res = await cmd.execute()
        assert res.success, res.text

        resp_pd = res.result
        assert resp_pd is not None
        assert resp_pd.component_type == req_pd.find_component_type
        # Проверить, что пришёл адрес именно зарегестрированного логера
        assert resp_pd.callback_address == logger_addr

    async def test_find_Baseapps(self):
        """Запрос на Baseapp'ы.

        Baseapp'оп регестрируется несколько, в ответе тоже должно их быть несколько.

        Запрос на Супервизор делается по TCP, т.к. по UDP можно принять только
        одно ответное сообщение (об одном компоненте). Ответ отправляется без обёртки
        в сообщение, поэтому длина сообщения не известна во время получения.
        При нескольких компонентах понять, что отправлено несколько сообщений
        (о нескольких компонентах) можно только, если они приходят чанками, а
        это подразумевает TCP соединение: каждый чанк - это информация об
        одном компоненте, закрытие соединения - это конец передачи.
        """

        # Если в одной и той же loop запустить и сервер и клиент, то данные
        # отправленные сервером в два чанка придут в клиент одним чанком из
        # буфера. Поэтому сделаю две петли в разных процессах, так придёт два
        # чанка с отдельным сообщением в каждом.
        def run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def start():
                await self._app.start()
                await asyncio.sleep(10)

            loop.run_until_complete(start())

        proc = multiprocessing.Process(target=run)
        proc.daemon = True
        proc.start()
        # Нужно немного времени, чтобы процесс раскрутился
        time.sleep(2)

        # Создаются данные, которые будут отправлены для регистрации Бэйзапов
        baseapp_info_1 = OnBroadcastInterfaceParsedData.get_empty()
        baseapp_info_1.componentType = ComponentType.BASEAPP.value
        baseapp_info_1.componentID = self._app.generate_component_id()
        baseapp_info_1.callback_address = AppAddr('1.0.0.0', server.get_free_port())

        baseapp_info_2 = OnBroadcastInterfaceParsedData.get_empty()
        baseapp_info_2.componentType = ComponentType.BASEAPP.value
        baseapp_info_2.componentID = self._app.generate_component_id()
        baseapp_info_2.callback_address = AppAddr('2.0.0.0', server.get_free_port())

        # Данные для регистрации Бэйзапов отправляются в Супервизор
        serializer = utils.get_serializer_for(ComponentType.MACHINE)
        client = UDPClient(self._app.udp_addr)
        msg_1 = Message(
            msgspec.app.machine.onBroadcastInterface,
            baseapp_info_1.values()
        )
        data_1 = serializer.serialize(msg_1)
        await client.send(data_1)
        msg_2 = Message(
            msgspec.app.machine.onBroadcastInterface,
            baseapp_info_2.values()
        )
        data_2 = serializer.serialize(msg_2)
        await client.send(data_2)

        # Теперь запрос на зарегестрированные Baseapp'ы
        req_pd = OnFindInterfaceAddrParsedData(
            1000, 'root', ComponentType.UNKNOWN_COMPONENT, self._app.generate_component_id(),
            ComponentType.BASEAPP, 0, 0
        )
        cmd = OnFindInterfaceAddrTCPCommand(self._app.tcp_addr, req_pd)
        res = await cmd.execute()
        assert res.success, res.text

        resp_pd = res.result
        # Получили два зарегестрированных Baseapp'а
        assert len(resp_pd.infos) == 2
        assert resp_pd.infos[0].component_type == ComponentType.BASEAPP
        assert resp_pd.infos[1].component_type == ComponentType.BASEAPP

        proc.kill()
