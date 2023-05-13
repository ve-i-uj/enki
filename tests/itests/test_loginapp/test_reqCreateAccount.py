"""Integration tests for "reqCreateAccount"."""

from enki.command.loginapp import ReqCreateAccountCommand

from tests.itests.base import IntegrationLoginAppBaseTestCase


class ReqCreateAccountCommandestCase(IntegrationLoginAppBaseTestCase):

    async def test_ok(self):
        account_name = 'itest'
        password = '1'

        cmd = ReqCreateAccountCommand(
            self.client, account_name, password, b'user-data'
        )
        self.client.set_msg_receiver(cmd)
        res = await cmd.execute()
        assert res.result is not None
