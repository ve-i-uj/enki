"""Integration tests for "reqAccountNewPassword"."""

from enki import KBEngine
from enki.net.command.baseapp import ReqAccountNewPasswordCommand

from tests.itests.base import IBaseAppMockedLayersTestCase


class ReqAccountNewPasswordCommandTestCase(IBaseAppMockedLayersTestCase):

    async def test_ok(self):
        player_id = self._app.get_relogin_data()[1]

        old_pwd = '1'
        new_pwd = '1'
        cmd = ReqAccountNewPasswordCommand(
            self._app.client, player_id, old_pwd, new_pwd
        )
        res = await self._app.send_command(cmd)
        assert res.success, res.text
