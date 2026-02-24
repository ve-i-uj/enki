"""Integration tests for "hello"."""

from enki.command.baseapp import BaseappHelloCommand


class TestHelloCommandTestCase:

    async def test_ok(self):
        cmd = BaseappHelloCommand(
            kbe_version="2.5.10",
            script_version="0.1.0",
            encrypted_key=b"",
            client=self._app.client,
        )
        res = await self._app.send_command(cmd)
        assert res.success, res.text
