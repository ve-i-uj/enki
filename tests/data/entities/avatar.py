"""The game logic of the "Avatar" entity."""

from enki.layer import INetLayer
from enki.net.kbeclient.kbetype import FixedDict
from enki.app.appl import App

from .components.test import Test
from .components.testnobase import TestNoBase

from tests.data import demo_descr


class Avatar(demo_descr.gameentity.AvatarBase):

    def __init__(self, entity_id, is_player: bool, layer: INetLayer):
        super().__init__(entity_id, is_player, layer)

        self._component1: Test = Test(self, owner_attr_id=16)
        self._component2: Test = Test(self, owner_attr_id=21)
        self._component3: TestNoBase = TestNoBase(self, owner_attr_id=22)

    @property
    def component1(self) -> Test:
        return self._component1

    @property
    def component2(self) -> Test:
        return self._component2

    @property
    def component3(self) -> TestNoBase:
        return self._component3
