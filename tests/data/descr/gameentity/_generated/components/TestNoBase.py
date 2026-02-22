"""Generated module represents the entity "TestNoBase" of the file entities.xml"""

from __future__ import annotations

import logging

from enki.misc import devonly
from enki.kbetype import *
from enki.apps.clientapp.layer.ilayer import KBEComponentEnum
from enki.apps.clientapp.gameentity import (
    EntityComponentBaseRemoteCall,
    EntityComponentCellRemoteCall,
    GameEntityComponent,
    GameEntity,
)

from ....deftype import *

logger = logging.getLogger(__name__)


class _TestNoBaseBaseRemoteCall(EntityComponentBaseRemoteCall):
    """Remote call to the BaseApp component of the entity."""


class _TestNoBaseCellRemoteCall(EntityComponentCellRemoteCall):
    """Remote call to the CellApp component of the entity."""

    def hello(self,
              int32_0: KBEInt32):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._e_component.owner.__call_component_remote_method__(
            KBEComponentEnum.CELL,
            self._e_component.owner_attr_id,
            'hello',
            (int32_0, )
        )


class TestNoBaseBase(GameEntityComponent):
    CLS_ID = 4

    def __init__(self, entity: GameEntity, owner_attr_id: int):
        super().__init__(entity, owner_attr_id)

        self._cell = _TestNoBaseCellRemoteCall(self)
        self._base = _TestNoBaseBaseRemoteCall(self)
        self._position: Position = Position()
        self._direction: Direction = Direction()
        self._spaceID: KBEUInt32 = KBEUInt32(0)
        self._own: KBEInt32 = KBEInt32(0)
        self._state: KBEInt32 = KBEInt32(0)

    @property
    def cell(self) -> _TestNoBaseCellRemoteCall:
        return self._cell

    @property
    def base(self) -> _TestNoBaseBaseRemoteCall:
        return self._base

    @property
    def className(self) -> str:
        return 'TestNoBase'

    @property
    def position(self) -> Position:
        return self._position

    def set_position(self, old_value: Position):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def direction(self) -> Direction:
        return self._direction

    def set_direction(self, old_value: Direction):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def spaceID(self) -> KBEUInt32:
        return self._spaceID

    @property
    def own(self) -> KBEInt32:
        return self._own

    @property
    def state(self) -> KBEInt32:
        return self._state

    def set_state(self, old_value: KBEInt32):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    def helloCB(self,
                int32_0: KBEInt32):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
