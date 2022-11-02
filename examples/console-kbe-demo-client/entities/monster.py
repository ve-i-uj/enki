"""The game logic of the "Monster" entity."""

from enki.interface import IEntityMgr

from tests.data import demo_descr


class Monster(demo_descr.entity.MonsterBase):

    def __init__(self, entity_id: int, entity_mgr: IEntityMgr):
        super().__init__(entity_id, entity_mgr)
