"""Тест на получение Supervisor'ом сообщений с нереализованными обработчиками."""

import asyncio
from enki.core import msgspec, utils
from enki.core.enkitype import AppAddr
from enki.command import RequestCommand
from enki.core.kbeenum import ComponentType
from enki.core.message import Message
from enki.net.client import TCPClient

from ._base import SupervisorTestCase



class NotImplementedTestCase(SupervisorTestCase):

    async def test_all(self):
        """Проверяем все не реализованные обработчики."""
        res = await self._app.start()
        assert res.success

        serializer = utils.get_serializer_for(ComponentType.MACHINE)

        for msg_spec in (msgspec.app.machine.queryLoad,
                         msgspec.app.machine.startserver,
                         msgspec.app.machine.stopserver,
                         msgspec.app.machine.killserver,
                         msgspec.app.machine.setflags,
                         msgspec.app.machine.reqKillServer):
            with self.subTest(msg_spec):
                msg = Message(msg_spec, tuple([b'']))
                data = serializer.serialize(msg)

                self._client = TCPClient(self._app.tcp_addr)
                res = await self._client.start()
                assert res.success

                success = await self._client.send(data)
                # Сообщение принято, так как его удалось отправить. А затем соединение
                # было закрыто. В лог вывелся варнинг.
                assert success
                await asyncio.sleep(0.1)
                assert not self._client.is_alive
