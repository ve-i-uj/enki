"""Generated module represents the entity "Gate" of the file entities.xml"""

from __future__ import annotations

import io
import logging

from enki import kbetype, kbeclient, kbeentity, descr
from enki.misc import devonly


logger = logging.getLogger(__name__)


class _GateBaseEntityRemoteCall(kbeentity.BaseEntityRemoteCall):
    """Remote call to the BaseApp component of the entity."""

    def __init__(self, entity: GateBase) -> None:
        super().__init__(entity)
        # It's needed for IDE can recoginze the entity type
        self._entity: GateBase = entity


class _GateCellEntityRemoteCall(kbeentity.BaseEntityRemoteCall):
    """Remote call to the CellApp component of the entity."""

    def __init__(self, entity: GateBase) -> None:
        super().__init__(entity)
        # It's needed for IDE can recoginze the entity type
        self._entity: GateBase = entity


class GateBase(kbeentity.Entity):
    CLS_ID = 7

    def __init__(self, entity_id: int, entity_mgr: kbeentity.IEntityMgr):
        super().__init__(entity_id, entity_mgr)
        self._cell = _GateCellEntityRemoteCall(entity=self)
        self._base = _GateBaseEntityRemoteCall(entity=self)
        self._position: kbetype.Vector3Data = descr.deftype.DIRECTION3D_SPEC.kbetype.default
        self._direction: kbetype.Vector3Data = descr.deftype.DIRECTION3D_SPEC.kbetype.default
        self._spaceID: int = descr.deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._entityNO: int = descr.deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._modelID: int = descr.deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._modelScale: int = descr.deftype.ENTITY_SUBSTATE_SPEC.kbetype.default
        self._name: str = descr.deftype.UNICODE_SPEC.kbetype.default
        self._uid: int = descr.deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._utype: int = descr.deftype.ENTITY_UTYPE_SPEC.kbetype.default

    @property
    def cell(self) -> _GateCellEntityRemoteCall:
        return self._cell

    @property
    def base(self) -> _GateBaseEntityRemoteCall:
        return self._base

    @property
    def position(self) -> kbetype.Vector3Data:
        return self._position

    def set_position(self, old_value: kbetype.Vector3Data):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def direction(self) -> kbetype.Vector3Data:
        return self._direction

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
