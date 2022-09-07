"""Integration tests for "hello"."""

import asyncio

from enki.command.baseapp import LogoutBaseappCommand

from tests.itests.base import IntegrationBaseAppBaseTestCase


class LogoutBaseappCommandTestCase(IntegrationBaseAppBaseTestCase):

    async def test_ok(self):
        rnd_uuid, entity_id = self.app.get_relogin_data()
        cmd = LogoutBaseappCommand(
            client=self.app.client,
            rnd_uuid=rnd_uuid,
            entity_id=entity_id
        )
        assert self.app.is_connected
        await self.app.send_command(cmd)
        await asyncio.sleep(1)
        assert not self.app.is_connected
