"""Integration tests for "reqAccountNewPassword"."""

from enki.net.command.baseapp import ReqAccountNewPasswordCommand

from tests.itests.base import IntegrationBaseAppBaseTestCase

class ReqAccountNewPasswordCommandTestCase(IntegrationBaseAppBaseTestCase):

    async def test_ok(self):
        entity_id = self._gama_layer.get_game_state().get_player_id()
        old_pwd = '1'
        new_pwd = '1'
        cmd = ReqAccountNewPasswordCommand(
            self._app.client, entity_id, old_pwd, new_pwd  # type: ignore
        )
        res = await self.app.send_command(cmd)
        assert res.success, res.text
