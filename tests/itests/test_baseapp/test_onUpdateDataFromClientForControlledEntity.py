"""Integration tests for "onUpdateDataFromClientForControlledEntity"."""

import asyncio

from enki.core import kbetype
from enki.command.baseapp import OnUpdateDataFromClientForControlledEntityCommand
from enki.app import clientapp
from enki.app.clientapp import KBEngine, settings

from tests.itests.base import IBaseAppThreadedTestCase

class OnUpdateDataFromClientCommandTestCase(IBaseAppThreadedTestCase):
    # TODO: [2023-01-16 22:14 burov_alexey@mail.ru]:
    # Тоже условно проходящий тест, т.к. в логах вот такая штука
    # Cellapp::onUpdateDataFromClientForControlledEntity: not found entity 256!

    def test_ok(self):
        KBEngine.login('1', '1')
        clientapp.sync_layers(settings.SECOND * 2)

        self.call_selectAvatarGame()

        player = KBEngine.player()
        assert player is not None
        # entitites = {
        #     e.id: e for e in self.app._entity_helper._entities.values()
        #     if e is not player and e.className() == 'Account'
        # }
        # assert entitites
        # entity = list(entitites.values())[0]
        position = kbetype.Position(*[v + 1 for v in player.position])  # type: ignore
        direction = kbetype.Direction(*[v + 1 for v in player.direction])  # type: ignore
        is_on_ground = not player.isOnGround
        space_id = player.spaceID
        cmd = OnUpdateDataFromClientForControlledEntityCommand(
            self.app.client, player.id, position, direction, is_on_ground, space_id
        )
        future = asyncio.run_coroutine_threadsafe(self.app.send_command(cmd), self.loop)
        clientapp.sync_layers(settings.SECOND * 2)
        assert future.result().success, future.result().text

        # assert player.position == position
