"""The game logic of the "NPC" entity."""

from enki import descr
from enki.interface import IEntityMgr


class NPC(descr.entity.NPCBase):

    def __init__(self, entity_id: int, entity_mgr: IEntityMgr):
        super().__init__(entity_id, entity_mgr)
