"""The game logic of the "NPC" entity."""

from enki.app.clientapp.layer.ilayer import INetLayer

import descr


class NPC(descr.gameentity.NPCBase):

    def __init__(self, entity_id, is_player: bool, layer: INetLayer):
        super().__init__(entity_id, is_player, layer)
