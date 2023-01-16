"""Generated module represents the entity "Test" of the file entities.xml"""

from __future__ import annotations

import io
import logging
from typing import Optional

from enki import devonly
from enki.net.kbeclient.kbetype import Position, Direction, FixedDict, Array, \
    Vector2, Vector3, Vector4
from enki.layer import KBEComponentEnum
from enki.app.appl import App
from enki.app.gameentity import EntityComponentBaseRemoteCall, \
    EntityComponentCellRemoteCall, GameEntityComponent, GameEntity

from .... import deftype

logger = logging.getLogger(__name__)


class _TestBaseRemoteCall(EntityComponentBaseRemoteCall):
    """Remote call to the BaseApp component of the entity."""

    def say(self,
            entity_forbids_0: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._e_component.owner.__call_component_remote_method__(
            KBEComponentEnum.BASE,
            self._e_component.owner_attr_id,
            'say',
            (entity_forbids_0, )
        )


class _TestCellRemoteCall(EntityComponentCellRemoteCall):
    """Remote call to the CellApp component of the entity."""

    def hello(self,
              entity_forbids_0: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._e_component.owner.__call_component_remote_method__(
            KBEComponentEnum.CELL,
            self._e_component.owner_attr_id,
            'hello',
            (entity_forbids_0, )
        )


class TestBase(GameEntityComponent):
    CLS_ID = 3

    def __init__(self, entity: GameEntity, owner_attr_id: int):
        super().__init__(entity, owner_attr_id)

        self._cell = _TestCellRemoteCall(self)
        self._base = _TestBaseRemoteCall(self)
        self._position: Position = Position()
        self._direction: Direction = Direction()
        self._spaceID: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._own: int = deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self._state: int = deftype.ENTITY_FORBIDS_SPEC.kbetype.default

    @property
    def cell(self) -> _TestCellRemoteCall:
        return self._cell

    @property
    def base(self) -> _TestBaseRemoteCall:
        return self._base

    @property
    def className(self) -> str:
        return 'Test'

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
    def spaceID(self) -> int:
        return self._spaceID

    @property
    def own(self) -> int:
        return self._own

    @property
    def state(self) -> int:
        return self._state

    def set_state(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    def helloCB(self,
                entity_forbids_0: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
