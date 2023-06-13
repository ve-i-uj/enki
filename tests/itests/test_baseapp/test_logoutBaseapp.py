"""Integration tests for "hello"."""

import asyncio
from enki import settings

from enki.command.baseapp import LogoutBaseappCommand

from tests.itests.base import IBaseAppMockedLayersTestCase


class LogoutBaseappCommandTestCase(IBaseAppMockedLayersTestCase):

    async def test_ok(self):
        rnd_uuid, entity_id = self._app.get_relogin_data()
        cmd = LogoutBaseappCommand(
            client=self._app.client,
            rnd_uuid=rnd_uuid,
            entity_id=entity_id
        )
        res = await self._app.send_command(cmd)
        assert res.success, res.text
        await asyncio.sleep(1)
        assert not self._app.is_connected
