"""The game logic of the "Avatar" entity."""

from enki import descr
from enki.interface import IEntityMgr

from .components.test import Test
from .components.testnobase import TestNoBase


class Avatar(descr.entity.AvatarBase):

    def __init__(self, entity_id: int, entity_mgr: IEntityMgr):
        super().__init__(entity_id, entity_mgr)
        self._component1: Test = Test(self, own_attr_id=16)
        self._component2: Test = Test(self, own_attr_id=21)
        self._component3: TestNoBase = TestNoBase(self, own_attr_id=22)

    @property
    def component1(self) -> Test:
        return self._component1

    @property
    def component2(self) -> Test:
        return self._component2

    @property
    def component3(self) -> TestNoBase:
        return self._component3
