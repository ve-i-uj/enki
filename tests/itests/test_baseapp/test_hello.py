"""Integration tests for "hello"."""

from enki.command.baseapp import HelloCommand

from tests.itests.base import IntegrationBaseAppBaseTestCase


class HelloCommandTestCase(IntegrationBaseAppBaseTestCase):

    async def setUp(self) -> None:
        await super().setUp()

    async def test_ok(self):
        cmd = HelloCommand(
            kbe_version='2.5.10',
            script_version='0.1.0',
            encrypted_key=b'',
            client=self._app.client
        )
        res = await self.app.send_command(cmd)
        assert res.success, res.text
