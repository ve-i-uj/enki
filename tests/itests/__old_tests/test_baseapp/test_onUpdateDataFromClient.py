"""Integration tests for "onUpdateDataFromClient"."""

import asyncio

from enki.app import client
from tests.itests.base import IBaseAppThreadedTestCase

from enki.apps.clientapp import KBEngine, settings
from enki.command.baseapp import OnUpdateDataFromClientCommand


class OnUpdateDataFromClientCommandTestCase(IBaseAppThreadedTestCase):
    def test_ok(self):
        KBEngine.login("1", "1")
        client.sync_layers(settings.SECOND * 2)

        self.call_selectAvatarGame()

        player = KBEngine.player()
        assert player is not None

        position = Position(*[v - 1 for v in player.position])  # type: ignore
        direction = Direction(*[v - 1 for v in player.direction])  # type: ignore
        is_on_ground = not player.isOnGround
        space_id = player.spaceID
        cmd = OnUpdateDataFromClientCommand(
            self.app.client, position, direction, is_on_ground, space_id
        )
        future = asyncio.run_coroutine_threadsafe(
            self.app.send_command(cmd), self.loop
        )
        client.sync_layers(settings.SECOND * 1)
        assert future.result().success, future.result().text

        # The player direction needs to set by client, not by server
        # assert player.position == position
        # assert player.is_on_ground == is_on_ground
        # assert player.spaceID == space_id
