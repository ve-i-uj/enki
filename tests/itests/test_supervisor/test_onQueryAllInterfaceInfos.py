"""Тест на получение Supervisor'ом Machine::onBroadcastInterface ."""

from enki.app.appaddr import AppAddr
from enki.command.machine import OnQueryAllInterfaceInfosCommand


from ._base import SupervisorTestCase


class OnBroadcastInterfaceTestCase(SupervisorTestCase):

    async def test_about_self(self):
        """Приложение возвращает ответ о самом себе."""
        res = await self._supervisor_app.start()
        assert res.success

        assert res.success, res.text
        cmd = OnQueryAllInterfaceInfosCommand(
            addr=AppAddr('0.0.0.0', self._tcp_port),
            uid=0,
            username='123',
            finderRecvPort=0
        )
        resp = await cmd.execute()
        assert resp.success, resp.text

        info = resp.result.infos[0]
        assert info.external_address == self._supervisor_app.tcp_addr

