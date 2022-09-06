"""Integration tests for "onUpdateDataFromClientForControlledEntity"."""

import asyncio
from enki import kbetype
from enki.command.baseapp import OnUpdateDataFromClientForControlledEntityCommand

from tests.itests.base import IntegrationBaseAppBaseTestCase

class OnUpdateDataFromClientCommandTestCase(IntegrationBaseAppBaseTestCase):

    async def test_ok(self):
        await self.call_selectAvatarGame()
        player = self.app._entity_mgr.get_player()
        # entitites = {
        #     e.id: e for e in self.app._entity_mgr._entities.values()
        #     if e is not player and e.className() == 'Account'
        # }
        # assert entitites
        # entity = list(entitites.values())[0]
        position = kbetype.Position(*[v + 1 for v in player.position])  # type: ignore
        direction = kbetype.Direction(*[v + 1 for v in player.direction])  # type: ignore
        is_on_ground = not player.is_on_ground
        space_id = player.spaceID
        cmd = OnUpdateDataFromClientForControlledEntityCommand(
            self._app.client, player.id, position, direction, is_on_ground, space_id
        )
        res = await self.app.send_command(cmd)
        assert res
        await asyncio.sleep(2)
        player = self.app._entity_mgr.get_player()
        assert player.position == position
