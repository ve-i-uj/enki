"""The game logic of the "Monster" entity."""

import descr

from enki.apps.clientapp.layer.ilayer import INetLayer


class Monster(descr.gameentity.MonsterBase):
    def __init__(self, entity_id, is_player: bool, layer: INetLayer):
        super().__init__(entity_id, is_player, layer)
