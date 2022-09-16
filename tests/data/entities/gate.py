"""The game logic of the "Gate" entity."""

from enki.interface import IEntityMgr

from tests.data import demo_descr


class Gate(demo_descr.entity.GateBase):

    def __init__(self, entity_id: int, entity_mgr: IEntityMgr):
        super().__init__(entity_id, entity_mgr)
