"""Тесты на Supervisor::onStopComponent."""

from asyncio import StreamReader, StreamWriter
import asyncio
import logging
from enki.command.machine import OnFindInterfaceAddrUDPCommand, OnQueryAllInterfaceInfosCommand

from enki.core import msgspec, utils
from enki.core.enkitype import AppAddr
from enki.command import RequestCommand
from enki.core.kbeenum import ComponentType
from enki.core.message import Message
from enki.handler.serverhandler.machinehandler import OnBroadcastInterfaceHandler, OnFindInterfaceAddrHandler
from enki.misc import devonly
from enki.net import server
from enki.net.client import TCPClient, UDPClient
from enki.net.inet import IChannel, IServerMsgReceiver
from enki.net.server import TCPServer
from tools import msgreader

from ._base import SupervisorTestCase

logger = logging.getLogger(__name__)


class OnStopComponentestCase(SupervisorTestCase):

    async def test_ok(self):
        """Состояние должно измениться."""
        res = await self._app.start()
        assert res.success

        machine_serializer = utils.get_serializer_for(ComponentType.MACHINE)

        # Сперва сымитируем компонент. Это будет просто tcp сервер.

        class ServerMsgReceiver(IServerMsgReceiver):
            async def on_receive_msg(self, msg: Message, channel: IChannel):
                logger.debug('[%s] %s', self, devonly.func_args_values())

        supervisor_addr = self._app.tcp_addr

        class MockApp(TCPServer):
            mock_app_connected = False

            async def handle_connection(self, reader: StreamReader, writer: StreamWriter):
                addr = writer.get_extra_info('peername')
                assert AppAddr(addr[0], addr[1]) == supervisor_addr
                self.__class__.mock_app_connected = True

        app_mock = MockApp(
            AppAddr('0.0.0.0', server.get_free_port()),
            msgspec.app.machine.SPEC_BY_ID,
            ServerMsgReceiver()
        )
        res = await app_mock.start()
        assert res.success

        # Нужно компонент зарегестрировать через сообщение
        onBroadcastInterface_hex_data = '08007100c76e0000726f6f74000a000000000005d4eb384f640100000000000000ffffffffffffffffffffffffac190003b9b1ac190003c56700bb000000000000000000000000201e010000000000000000000000000000000000000000000000000000000000d084000000000000ac190003504b'
        onBroadcastInterface_data = msgreader.normalize_wireshark_data(onBroadcastInterface_hex_data)
        msg, _ = machine_serializer.deserialize(memoryview(onBroadcastInterface_data))
        assert msg is not None
        res = OnBroadcastInterfaceHandler().handle(msg)
        assert res.result is not None

        component_id = res.result.componentID

        # Нужно изменить адрес из реальных данных на тестовый запущенного мока
        res.result.callback_address = app_mock.addr

        # Регестрируем мок компонент
        client = UDPClient(self._app.udp_addr)
        success = await client.send(
            machine_serializer.serialize(Message(msgspec.app.machine.onBroadcastInterface,
                                                 res.result.values())))
        assert success

        # Запросим зарегистрированный компонент, чтобы проверить, что он есть
        hex_data = '01001f00b4200000726f6f74000100000000000cfb955f68640a000000ac1b00075107'
        data = msgreader.normalize_wireshark_data(hex_data)
        req_msg, _ = machine_serializer.deserialize(memoryview(data))
        assert req_msg is not None
        req_res = OnFindInterfaceAddrHandler().handle(req_msg)
        req_pd = req_res.result
        # Данные для отправки взяты из реального взаимодействия, поэтому нужно
        # адрес колбэка подменить на тот, где сейчас в тесте запущено приложение
        req_pd.callback_address = app_mock.addr
        assert req_pd is not None

        # Запрос, что компонент есть
        cmd = OnFindInterfaceAddrUDPCommand(self._app.udp_addr, req_pd)
        res = await cmd.execute()
        assert res.success, res.text

        # Дальше уведомляем, что компоненту отправлено сообщение на остановку

        serializer = utils.get_serializer_for(ComponentType.SUPERVISOR)

        msg = Message(msgspec.app.supervisor.onStopComponent, tuple([component_id]))
        data = serializer.serialize(msg)

        self._client = TCPClient(self._app.tcp_addr)
        res = await self._client.start()
        assert res.success

        success = await self._client.send(data)
        # Сообщение принято, так как его удалось отправить. А затем соединение было закрыто.
        assert success

        await asyncio.sleep(0.1)
        assert not self._client.is_alive

        # Компонент пропал из списка зарегестрированных

        cmd = OnFindInterfaceAddrUDPCommand(self._app.udp_addr, req_pd)
        res = await cmd.execute()
        assert res.success, res.text
        assert res.result is not None
        assert res.result.component_type == ComponentType.UNKNOWN_COMPONENT

        await app_mock.stop()


    async def test_twice(self):
        """Тест на повторную отправку onStopComponent.

        Ничего не должно поменять.
        """
        await self.test_ok()

        cmd = OnQueryAllInterfaceInfosCommand(self._app.tcp_addr)
        res = await cmd.execute()
        assert res.success, res.text
        # Т.е. только сам Supervisor
        assert len(res.result.infos) == 1
