"""Generated module represents the entity "Monster" of the file entities.xml"""

from __future__ import annotations

import io
import logging
from typing import Optional

from enki.misc import devonly
from enki.core.kbetype import Position, Direction, FixedDict, Array, \
    Vector2, Vector3, Vector4
from enki.app.clientapp.layer.ilayer import KBEComponentEnum, INetLayer
from enki.app.clientapp.appl import App
from enki.app.clientapp.gameentity import EntityBaseRemoteCall, EntityCellRemoteCall, \
    GameEntityComponent, GameEntity

from ... import deftype

logger = logging.getLogger(__name__)


class _MonsterBaseRemoteCall(EntityBaseRemoteCall):
    """Remote call to the BaseApp component of the entity."""

    def __init__(self, entity: MonsterBase) -> None:
        super().__init__(entity)


class _MonsterCellRemoteCall(EntityCellRemoteCall):
    """Remote call to the CellApp component of the entity."""

    def __init__(self, entity: MonsterBase) -> None:
        super().__init__(entity)


class MonsterBase(GameEntity):
    CLS_ID = 5

    def __init__(self, entity_id, is_player: bool, layer: INetLayer):
        super().__init__(entity_id, is_player, layer)

        self._cell = _MonsterCellRemoteCall(entity=self)
        self._base = _MonsterBaseRemoteCall(entity=self)
        self._position: Position = Position()
        self._direction: Direction = Direction()
        self._spaceID: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._HP: int = deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self._HP_Max: int = deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self._MP: int = deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self._MP_Max: int = deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self._entityNO: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._forbids: int = deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self._modelID: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._modelScale: int = deftype.ENTITY_SUBSTATE_SPEC.kbetype.default
        self._moveSpeed: int = deftype.ENTITY_SUBSTATE_SPEC.kbetype.default
        self._name: str = deftype.UNICODE_SPEC.kbetype.default
        self._state: int = deftype.ENTITY_STATE_SPEC.kbetype.default
        self._subState: int = deftype.ENTITY_SUBSTATE_SPEC.kbetype.default
        self._uid: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._utype: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default

        self._components: dict[str, GameEntityComponent] = {
        }
        self._component_by_owner_attr_id = {
            comp.owner_attr_id: comp for comp in self._components.values()
        }

    @property
    def cell(self) -> _MonsterCellRemoteCall:
        return self._cell

    @property
    def base(self) -> _MonsterBaseRemoteCall:
        return self._base

    @property
    def className(self) -> str:
        return 'Monster'

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
    def HP(self) -> int:
        return self._HP

    def set_HP(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def HP_Max(self) -> int:
        return self._HP_Max

    def set_HP_Max(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def MP(self) -> int:
        return self._MP

    def set_MP(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def MP_Max(self) -> int:
        return self._MP_Max

    def set_MP_Max(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def entityNO(self) -> int:
        return self._entityNO

    def set_entityNO(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def forbids(self) -> int:
        return self._forbids

    def set_forbids(self, old_value: int):
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
    def moveSpeed(self) -> int:
        return self._moveSpeed

    def set_moveSpeed(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def name(self) -> str:
        return self._name

    def set_name(self, old_value: str):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def state(self) -> int:
        return self._state

    def set_state(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def subState(self) -> int:
        return self._subState

    def set_subState(self, old_value: int):
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

    def recvDamage(self,
                   entity_forbids_0: int,
                   entity_forbids_1: int,
                   entity_forbids_2: int,
                   entity_forbids_3: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
