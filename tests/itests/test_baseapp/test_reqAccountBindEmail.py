"""Integration tests for "reqAccountNewPassword"."""

from enki.net.command.baseapp import ReqAccountBindEmailCommand

from tests.itests.base import IntegrationBaseAppBaseTestCase

class ReqAccountBindEmailCommandTestCase(IntegrationBaseAppBaseTestCase):

    async def test_ok(self):
        entity_id = list(self._gama_layer._entities.keys())[0]
        password = '1'
        email = 'itests@tpc.org'
        cmd = ReqAccountBindEmailCommand(
            self._app.client, entity_id, password, email
        )
        res = await self.app.send_command(cmd)
        assert res.success, res.text
