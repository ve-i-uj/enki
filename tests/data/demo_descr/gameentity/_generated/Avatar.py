"""Generated module represents the entity "Avatar" of the file entities.xml"""

from __future__ import annotations

import io
import logging
from typing import Optional

from enki import kbetype, kbeclient, kbeentity, msgspec
from enki.gedescr import EntityDesc
from enki.interface import IKBEClientEntityComponent
from enki.misc import devonly

from .components.Test import TestBase
from .components.TestNoBase import TestNoBaseBase
from . import deftype

from . import description

logger = logging.getLogger(__name__)


class _AvatarBaseEntityRemoteCall(kbeentity.BaseEntityRemoteCall):
    """Remote call to the BaseApp component of the entity."""

    def __init__(self, entity: AvatarBase) -> None:
        super().__init__(entity)
        # It's needed for IDE can recoginze the entity type
        self._entity: AvatarBase = entity

    @property
    def component1(self) -> TestBase:
        return self._entity.component1

    @property
    def component2(self) -> TestBase:
        return self._entity.component2

    @property
    def component3(self) -> TestNoBaseBase:
        return self._entity.component3


class _AvatarCellEntityRemoteCall(kbeentity.BaseEntityRemoteCall):
    """Remote call to the CellApp component of the entity."""

    def __init__(self, entity: AvatarBase) -> None:
        super().__init__(entity)
        # It's needed for IDE can recoginze the entity type
        self._entity: AvatarBase = entity

    @property
    def component1(self) -> TestBase:
        return self._entity.component1

    @property
    def component2(self) -> TestBase:
        return self._entity.component2

    @property
    def component3(self) -> TestNoBaseBase:
        return self._entity.component3

    def dialog(self,
               entity_id: int,
               entity_forbids_0: int,
               entity_utype_1: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(0))  # entitycomponentPropertyID
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(11003))

        io_obj.write(deftype.ENTITY_FORBIDS_SPEC.kbetype.encode(entity_forbids_0))
        io_obj.write(deftype.ENTITY_UTYPE_SPEC.kbetype.encode(entity_utype_1))

        msg = kbeclient.Message(
            spec=msgspec.app.baseapp.onRemoteCallCellMethodFromClient,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)

    def jump(self,
             entity_id: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(0))  # entitycomponentPropertyID
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(5))

        msg = kbeclient.Message(
            spec=msgspec.app.baseapp.onRemoteCallCellMethodFromClient,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)

    def relive(self,
               entity_id: int,
               entity_substate_0: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(0))  # entitycomponentPropertyID
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(4))

        io_obj.write(deftype.ENTITY_SUBSTATE_SPEC.kbetype.encode(entity_substate_0))

        msg = kbeclient.Message(
            spec=msgspec.app.baseapp.onRemoteCallCellMethodFromClient,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)

    def requestPull(self,
                    entity_id: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(0))  # entitycomponentPropertyID
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(11))

        msg = kbeclient.Message(
            spec=msgspec.app.baseapp.onRemoteCallCellMethodFromClient,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)

    def useTargetSkill(self,
                       entity_id: int,
                       entity_forbids_0: int,
                       entity_forbids_1: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(0))  # entitycomponentPropertyID
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(11001))

        io_obj.write(deftype.ENTITY_FORBIDS_SPEC.kbetype.encode(entity_forbids_0))
        io_obj.write(deftype.ENTITY_FORBIDS_SPEC.kbetype.encode(entity_forbids_1))

        msg = kbeclient.Message(
            spec=msgspec.app.baseapp.onRemoteCallCellMethodFromClient,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)


class AvatarBase(kbeentity.Entity):
    CLS_ID = 2
    DESCR = description.DESC_BY_UID[CLS_ID]

    def __init__(self, entity_id: int, entity_mgr: kbeentity.IEntityMgr):
        super().__init__(entity_id, entity_mgr)
        self._cell = _AvatarCellEntityRemoteCall(entity=self)
        self._base = _AvatarBaseEntityRemoteCall(entity=self)
        self._position: kbetype.Position = kbetype.Position()
        self._direction: kbetype.Direction = kbetype.Direction()
        self._spaceID: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._HP: int = deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self._HP_Max: int = deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self._MP: int = deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self._MP_Max: int = deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self._component1: TestBase = TestBase(self, own_attr_id=16)
        self._component2: TestBase = TestBase(self, own_attr_id=21)
        self._component3: TestNoBaseBase = TestNoBaseBase(self, own_attr_id=22)
        self._forbids: int = deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self._level: int = deftype.UINT16_SPEC.kbetype.default
        self._modelID: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._modelScale: int = deftype.ENTITY_SUBSTATE_SPEC.kbetype.default
        self._moveSpeed: int = deftype.ENTITY_SUBSTATE_SPEC.kbetype.default
        self._name: str = deftype.UNICODE_SPEC.kbetype.default
        self._own_val: int = deftype.UINT16_SPEC.kbetype.default
        self._spaceUType: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._state: int = deftype.ENTITY_STATE_SPEC.kbetype.default
        self._subState: int = deftype.ENTITY_SUBSTATE_SPEC.kbetype.default
        self._uid: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._utype: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._isDestroyed: bool = False

        self._components: dict[str, IKBEClientEntityComponent] = {
            'component1': self._component1,
            'component2': self._component2,
            'component3': self._component3,
        }

    @property
    def cell(self) -> _AvatarCellEntityRemoteCall:
        return self._cell

    @property
    def base(self) -> _AvatarBaseEntityRemoteCall:
        return self._base

    @property
    def position(self) -> kbetype.Position:
        return kbetype.Position.from_vector(self._position)

    def set_position(self, old_value: kbetype.Position):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def direction(self) -> kbetype.Direction:
        return kbetype.Direction.from_vector(self._direction)

    def set_direction(self, old_value: kbetype.Direction):
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
    def component1(self) -> TestBase:
        return self._component1

    @property
    def component2(self) -> TestBase:
        return self._component2

    @property
    def component3(self) -> TestNoBaseBase:
        return self._component3

    @property
    def forbids(self) -> int:
        return self._forbids

    def set_forbids(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def level(self) -> int:
        return self._level

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
    def own_val(self) -> int:
        return self._own_val

    def set_own_val(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def spaceUType(self) -> int:
        return self._spaceUType

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

    def dialog_addOption(self,
                         entity_id: int,
                         entity_substate_0: int,
                         entity_utype_1: int,
                         unicode_2: str,
                         entity_forbids_3: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    def dialog_close(self,
                     entity_id: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    def dialog_setText(self,
                       entity_id: int,
                       unicode_0: str,
                       entity_substate_1: int,
                       entity_utype_2: int,
                       unicode_3: str):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    def onAddSkill(self,
                   entity_id: int,
                   entity_forbids_0: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    def onJump(self,
               entity_id: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    def onRemoveSkill(self,
                      entity_id: int,
                      entity_forbids_0: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    def recvDamage(self,
                   entity_id: int,
                   entity_forbids_0: int,
                   entity_forbids_1: int,
                   entity_forbids_2: int,
                   entity_forbids_3: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
