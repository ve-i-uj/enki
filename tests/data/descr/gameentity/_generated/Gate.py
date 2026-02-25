"""Generated module represents the entity "Gate" of the file entities.xml"""

from __future__ import annotations

import logging

from enki.misc import devonly
from enki.kbetype import *
from enki.apps.clientapp.layer.ilayer import KBEComponentEnum, INetLayer
from enki.apps.clientapp.gameentity import (
    ClientEntityBaseRemoteCall,
    ClientEntityCellRemoteCall,
    ClientGameEntityComponent,
    ClientGameEntity,
)

from ...deftype import *

logger = logging.getLogger(__name__)


class _GateBaseRemoteCall(ClientEntityBaseRemoteCall):
    """Remote call to the BaseApp component of the entity."""

    def __init__(self, entity: GateBase) -> None:
        super().__init__(entity)


class _GateCellRemoteCall(ClientEntityCellRemoteCall):
    """Remote call to the CellApp component of the entity."""

    def __init__(self, entity: GateBase) -> None:
        super().__init__(entity)


class GateBase(ClientGameEntity):
    CLS_ID = 7

    def __init__(self, entity_id, is_player: bool, layer: INetLayer):
        super().__init__(entity_id, is_player, layer)

        self._cell = _GateCellRemoteCall(entity=self)
        self._base = _GateBaseRemoteCall(entity=self)
        self._position: Position = Position()
        self._direction: Direction = Direction()
        self._spaceID: KBEUInt32 = KBEUInt32(0)
        self._entityNO: KBEUInt32 = KBEUInt32(0)
        self._modelID: KBEUInt32 = KBEUInt32(0)
        self._modelScale: KBEUInt8 = KBEUInt8(0)
        self._name: KBEUnicode = KBEUnicode()
        self._uid: KBEUInt32 = KBEUInt32(0)
        self._utype: KBEUInt32 = KBEUInt32(0)

        self._components: dict[str, ClientGameEntityComponent] = {
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
    def spaceID(self) -> KBEUInt32:
        return self._spaceID

    @property
    def entityNO(self) -> KBEUInt32:
        return self._entityNO

    def set_entityNO(self, old_value: KBEUInt32):
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
    def name(self) -> KBEUnicode:
        return self._name

    def set_name(self, old_value: KBEUnicode):
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
