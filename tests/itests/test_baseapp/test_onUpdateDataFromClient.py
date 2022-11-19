"""Integration tests for "onUpdateDataFromClient"."""

import asyncio
from enki.net.kbeclient import kbetype
from enki.net.kbeclient.kbetype import Position, Direction

from enki.net.command.baseapp import OnUpdateDataFromClientCommand

from tests.itests.base import IntegrationBaseAppBaseTestCase

class OnUpdateDataFromClientCommandTestCase(IntegrationBaseAppBaseTestCase):

    async def test_ok(self):
        await self.call_selectAvatarGame()

        player = list(self._gama_layer._entities.values())[0]

        position = kbetype.Position(*[v - 1 for v in player.position])  # type: ignore
        direction = kbetype.Direction(*[v - 1 for v in player.direction])  # type: ignore
        is_on_ground = not player.isOnGround
        space_id = player.spaceID
        cmd = OnUpdateDataFromClientCommand(
            self._app.client, position, direction, is_on_ground, space_id
        )
        await asyncio.sleep(4)
        res = await self.app.send_command(cmd)
        assert res
        await asyncio.sleep(4)
        player = list(self._gama_layer._entities.values())[0]
        assert player.position == position
        # The player direction needs to set by clien, not by server
        # assert player.is_on_ground == is_on_ground
        assert player.spaceID == space_id
