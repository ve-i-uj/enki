"""The game logic of the "NPC" entity."""

from enki.interface import IEntityMgr

from tests.data import demo_descr


class NPC(demo_descr.entity.NPCBase):

    def __init__(self, entity_id: int, entity_mgr: IEntityMgr):
        super().__init__(entity_id, entity_mgr)
