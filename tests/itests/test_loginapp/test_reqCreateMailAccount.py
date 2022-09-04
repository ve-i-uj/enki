"""Integration tests for "reqCreateMailAccount"."""

from enki.command.loginapp import ReqCreateMailAccountCommand

from tests.itests.base import IntegrationLoginAppBaseTestCase


class ReqCreateMailAccountCommandTestCase(IntegrationLoginAppBaseTestCase):

    async def test_ok(self):
        account_name = 'itest'
        password = '1'

        cmd = ReqCreateMailAccountCommand(
            self.client, account_name, password, b'user-data'
        )
        self.client.set_msg_receiver(cmd)
        res = await cmd.execute()
        assert res.result is not None
