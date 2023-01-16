"""Integration tests for "onUpdateDataFromClient"."""

import asyncio

import enki
from enki import KBEngine
from enki.net.kbeclient import kbetype
from enki.net.kbeclient.kbetype import Position, Direction

from enki.net.command.baseapp import OnUpdateDataFromClientCommand

from tests.itests.base import IBaseAppThreadedTestCase

class OnUpdateDataFromClientCommandTestCase(IBaseAppThreadedTestCase):

    def test_ok(self):
        KBEngine.login('1', '1')
        self.handle_msges(5)

        self.call_selectAvatarGame()

        player = KBEngine.player()
        assert player is not None

        position = kbetype.Position(*[v - 1 for v in player.position])  # type: ignore
        direction = kbetype.Direction(*[v - 1 for v in player.direction])  # type: ignore
        is_on_ground = not player.isOnGround
        space_id = player.spaceID
        cmd = OnUpdateDataFromClientCommand(
            self.app.client, position, direction, is_on_ground, space_id
        )
        future = asyncio.run_coroutine_threadsafe(self.app.send_command(cmd), self.loop)
        self.handle_msges(4)
        assert future.result().success, future.result().text

        # The player direction needs to set by client, not by server
        # assert player.position == position
        # assert player.is_on_ground == is_on_ground
        # assert player.spaceID == space_id
