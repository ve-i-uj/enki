"""The game logic of the "Monster" entity."""

from enki.apps.clientapp.layer.ilayer import INetLayer
from tests.data import descr


class Monster(descr.gameentity.MonsterBase):
    def __init__(self, entity_id, is_player: bool, layer: INetLayer) -> None:
        super().__init__(entity_id, is_player, layer)
