"""Generated module represents the entity "Monster" of the file entities.xml"""

from __future__ import annotations

import logging

from enki.misc import devonly
from enki.kbetype import *
from enki.apps.clientapp.layer.ilayer import KBEComponentEnum, INetLayer
from enki.apps.clientapp.gameentity import EntityBaseRemoteCall, EntityCellRemoteCall, \
    GameEntityComponent, GameEntity

from ...deftype import *

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
        self._spaceID: KBEUInt32 = KBEUInt32(0)
        self._HP: KBEInt32 = KBEInt32(0)
        self._HP_Max: KBEInt32 = KBEInt32(0)
        self._MP: KBEInt32 = KBEInt32(0)
        self._MP_Max: KBEInt32 = KBEInt32(0)
        self._entityNO: KBEUInt32 = KBEUInt32(0)
        self._forbids: KBEInt32 = KBEInt32(0)
        self._modelID: KBEUInt32 = KBEUInt32(0)
        self._modelScale: KBEUInt8 = KBEUInt8(0)
        self._moveSpeed: KBEUInt8 = KBEUInt8(0)
        self._name: KBEUnicode = KBEUnicode()
        self._state: KBEInt8 = KBEInt8(0)
        self._subState: KBEUInt8 = KBEUInt8(0)
        self._uid: KBEUInt32 = KBEUInt32(0)
        self._utype: KBEUInt32 = KBEUInt32(0)

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
    def spaceID(self) -> KBEUInt32:
        return self._spaceID

    @property
    def HP(self) -> KBEInt32:
        return self._HP

    def set_HP(self, old_value: KBEInt32):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def HP_Max(self) -> KBEInt32:
        return self._HP_Max

    def set_HP_Max(self, old_value: KBEInt32):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def MP(self) -> KBEInt32:
        return self._MP

    def set_MP(self, old_value: KBEInt32):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def MP_Max(self) -> KBEInt32:
        return self._MP_Max

    def set_MP_Max(self, old_value: KBEInt32):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def entityNO(self) -> KBEUInt32:
        return self._entityNO

    def set_entityNO(self, old_value: KBEUInt32):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def forbids(self) -> KBEInt32:
        return self._forbids

    def set_forbids(self, old_value: KBEInt32):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def modelID(self) -> KBEUInt32:
        return self._modelID

    def set_modelID(self, old_value: KBEUInt32):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def modelScale(self) -> KBEUInt8:
        return self._modelScale

    def set_modelScale(self, old_value: KBEUInt8):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def moveSpeed(self) -> KBEUInt8:
        return self._moveSpeed

    def set_moveSpeed(self, old_value: KBEUInt8):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def name(self) -> KBEUnicode:
        return self._name

    def set_name(self, old_value: KBEUnicode):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def state(self) -> KBEInt8:
        return self._state

    def set_state(self, old_value: KBEInt8):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def subState(self) -> KBEUInt8:
        return self._subState

    def set_subState(self, old_value: KBEUInt8):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def uid(self) -> KBEUInt32:
        return self._uid

    def set_uid(self, old_value: KBEUInt32):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def utype(self) -> KBEUInt32:
        return self._utype

    def set_utype(self, old_value: KBEUInt32):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    def recvDamage(self,
                   int32_0: KBEInt32,
                   int32_1: KBEInt32,
                   int32_2: KBEInt32,
                   int32_3: KBEInt32):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
