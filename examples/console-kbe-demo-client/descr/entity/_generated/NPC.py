"""Generated module represents the entity "NPC" of the file entities.xml"""

from __future__ import annotations

import io
import logging
from typing import Optional

from enki import kbeclient, msgspec
from enki.net import netentity
from enki.gedescr import EntityDesc
from enki.interface import IKBEClientEntityComponent
from enki import devonly
from enki.net.kbeclient import kbetype

from ... import deftype

from . import description

logger = logging.getLogger(__name__)


class _NPCBaseEntityRemoteCall(netentity.BaseEntityRemoteCall):
    """Remote call to the BaseApp component of the entity."""

    def __init__(self, entity: NPCBase) -> None:
        super().__init__(entity)
        # It's needed for IDE can recoginze the entity type
        self._entity: NPCBase = entity


class _NPCCellEntityRemoteCall(netentity.BaseEntityRemoteCall):
    """Remote call to the CellApp component of the entity."""

    def __init__(self, entity: NPCBase) -> None:
        super().__init__(entity)
        # It's needed for IDE can recoginze the entity type
        self._entity: NPCBase = entity


class NPCBase(netentity.Entity):
    CLS_ID = 6
    DESCR = description.DESC_BY_UID[CLS_ID]

    def __init__(self, entity_id: int, entity_mgr: netentity.IEntityMgr):
        super().__init__(entity_id, entity_mgr)
        self._cell = _NPCCellEntityRemoteCall(entity=self)
        self._base = _NPCBaseEntityRemoteCall(entity=self)
        self._position: kbetype.Vector3Data = deftype.DIRECTION3D_SPEC.kbetype.default
        self._direction: kbetype.Vector3Data = deftype.DIRECTION3D_SPEC.kbetype.default
        self._spaceID: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._entityNO: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._modelID: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._modelScale: int = deftype.ENTITY_SUBSTATE_SPEC.kbetype.default
        self._moveSpeed: int = deftype.ENTITY_SUBSTATE_SPEC.kbetype.default
        self._name: str = deftype.UNICODE_SPEC.kbetype.default
        self._uid: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._utype: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._isDestroyed: bool = False

        self._components: dict[str, IKBEClientEntityComponent] = {
        }

    @property
    def cell(self) -> _NPCCellEntityRemoteCall:
        return self._cell

    @property
    def base(self) -> _NPCBaseEntityRemoteCall:
        return self._base

    @property
    def position(self) -> kbetype.Position:
        return kbetype.Position.from_vector(self._position)

    def set_position(self, old_value: kbetype.Vector3Data):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def direction(self) -> kbetype.Direction:
        return kbetype.Direction.from_vector(self._direction)

    def set_direction(self, old_value: kbetype.Vector3Data):
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
    def uid(self) -> int:
        return self._uid

    def set_uid(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def utype(self) -> int:
        return self._utype

    def set_utype(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
