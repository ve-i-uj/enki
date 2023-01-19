"""Integration tests for "reqAccountResetPassword"."""

from enki.net.command.loginapp import ReqAccountResetPasswordCommand

from tests.itests.base import IntegrationLoginAppBaseTestCase


class ReqAccountNewPasswordCommandTestCase(IntegrationLoginAppBaseTestCase):

    async def test_ok(self):
        account_name = '1'
        cmd = ReqAccountResetPasswordCommand(
            self.client, account_name
        )
        self.client.set_msg_receiver(cmd)
        res = await cmd.execute()
        assert res.success, res.text
