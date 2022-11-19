"""Integration tests for "importClientSDK"."""

from enki.net.command.loginapp import ImportClientSDKCommand

from tests.itests.base import IntegrationLoginAppBaseTestCase


class ImportClientSDKCommandTestCase(IntegrationLoginAppBaseTestCase):

    async def test_ok(self):

        cmd = ImportClientSDKCommand(
            self.client, 'ue4', 1024, '', 0
        )
        self.client.set_msg_receiver(cmd)
        res = await cmd.execute()
        assert res.result is not None
