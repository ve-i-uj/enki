"""Integration tests for "reqCreateAccount"."""

from tests.itests.base import IntegrationLoginAppBaseTestCase

from enki.command.loginapp import ReqCreateAccountCommand


class ReqCreateAccountCommandestCase(IntegrationLoginAppBaseTestCase):

    async def test_ok(self):
        account_name = "itest"
        password = "1"

        cmd = ReqCreateAccountCommand(
            self.client, account_name, password, b"user-data"
        )
        self.client.set_msg_receiver(cmd)
        res = await cmd.execute()
        assert res.result is not None
