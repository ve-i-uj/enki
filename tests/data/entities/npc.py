"""The game logic of the "NPC" entity."""

from enki.apps.clientapp.layer.ilayer import INetLayer
from tests.data import descr


class NPC(descr.gameentity.NPCBase):
    def __init__(self, entity_id, is_player: bool, layer: INetLayer) -> None:
        super().__init__(entity_id, is_player, layer)
