"""Integration tests for "reqAccountNewPassword"."""

from enki.net.command.baseapp import ReqAccountBindEmailCommand

from tests.itests.base import IBaseAppMockedLayersTestCase

class ReqAccountBindEmailCommandTestCase(IBaseAppMockedLayersTestCase):

    async def test_ok(self):
        player_id = self._app.get_relogin_data()[1]
        password = '1'
        email = 'itests@tpc.org'
        cmd = ReqAccountBindEmailCommand(
            self._app.client, player_id, password, email
        )
        res = await self._app.send_command(cmd)
        assert res.success, res.text
