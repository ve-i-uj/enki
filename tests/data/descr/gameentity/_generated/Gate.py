"""Generated module represents the entity "Gate" of the file entities.xml"""

from __future__ import annotations

import io
import logging
from typing import Optional

from enki import devonly
from enki.net.kbeclient.kbetype import Position, Direction, FixedDict, Array, \
    Vector2, Vector3, Vector4
from enki.layer import KBEComponentEnum, INetLayer
from enki.app.appl import App
from enki.app.gameentity import EntityBaseRemoteCall, EntityCellRemoteCall, \
    GameEntityComponent, GameEntity

from ... import deftype

logger = logging.getLogger(__name__)


class _GateBaseRemoteCall(EntityBaseRemoteCall):
    """Remote call to the BaseApp component of the entity."""

    def __init__(self, entity: GateBase) -> None:
        super().__init__(entity)


class _GateCellRemoteCall(EntityCellRemoteCall):
    """Remote call to the CellApp component of the entity."""

    def __init__(self, entity: GateBase) -> None:
        super().__init__(entity)


class GateBase(GameEntity):
    CLS_ID = 7

    def __init__(self, entity_id, is_player: bool, layer: INetLayer):
        super().__init__(entity_id, is_player, layer)

        self._cell = _GateCellRemoteCall(entity=self)
        self._base = _GateBaseRemoteCall(entity=self)
        self._position: Position = Position()
        self._direction: Direction = Direction()
        self._spaceID: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._entityNO: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._modelID: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._modelScale: int = deftype.ENTITY_SUBSTATE_SPEC.kbetype.default
        self._name: str = deftype.UNICODE_SPEC.kbetype.default
        self._uid: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._utype: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default

        self._components: dict[str, GameEntityComponent] = {
        }
        self._component_by_owner_attr_id = {
            comp.owner_attr_id: comp for comp in self._components.values()
        }

    @property
    def cell(self) -> _GateCellRemoteCall:
        return self._cell

    @property
    def base(self) -> _GateBaseRemoteCall:
        return self._base

    @property
    def className(self) -> str:
        return 'Gate'

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
    def entityNO(self) -> int:
        return self._entityNO

    def set_entityNO(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def modelID(self) -> int:
        return self._modelID

    def set_modelID(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def modelScale(self) -> int:
        return self._modelScale

    def set_modelScale(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def name(self) -> str:
        return self._name

    def set_name(self, old_value: str):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def uid(self) -> int:
        return self._uid

    def set_uid(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def utype(self) -> int:
        return self._utype

    def set_utype(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
