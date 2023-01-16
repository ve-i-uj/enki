"""Integration tests for "hello"."""

from enki.net.command.baseapp import HelloCommand

from tests.itests.base import IBaseAppMockedLayersTestCase


class HelloCommandTestCase(IBaseAppMockedLayersTestCase):

    async def test_ok(self):
        cmd = HelloCommand(
            kbe_version='2.5.10',
            script_version='0.1.0',
            encrypted_key=b'',
            client=self._app.client
        )
        res = await self._app.send_command(cmd)
        assert res.success, res.text
