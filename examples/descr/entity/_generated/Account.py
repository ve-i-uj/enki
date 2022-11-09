"""Generated module represents the entity "Account" of the file entities.xml"""

from __future__ import annotations

import io
import logging
from typing import Optional

from enki.net.kbeclient import kbetype, kbeclient, kbeentity, msgspec
from enki import kbetype, kbeclient, kbeentity, msgspec
from enki.gedescr import EntityDesc
from enki.interface import IKBEClientEntityComponent
from enki.misc import devonly

from ... import deftype

from . import description

logger = logging.getLogger(__name__)


class _AccountBaseEntityRemoteCall(kbeentity.BaseEntityRemoteCall):
    """Remote call to the BaseApp component of the entity."""

    def __init__(self, entity: AccountBase) -> None:
        super().__init__(entity)
        # It's needed for IDE can recoginze the entity type
        self._entity: AccountBase = entity

    def reqAvatarList(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(0))  # entitycomponentPropertyID
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(10001))

        msg = kbeclient.Message(
            spec=msgspec.app.baseapp.onRemoteMethodCall,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)

    def reqCreateAvatar(self,
                        entity_substate_0: int,
                        unicode_1: str):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(0))  # entitycomponentPropertyID
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(10002))

        io_obj.write(deftype.ENTITY_SUBSTATE_SPEC.kbetype.encode(entity_substate_0))
        io_obj.write(deftype.UNICODE_SPEC.kbetype.encode(unicode_1))

        msg = kbeclient.Message(
            spec=msgspec.app.baseapp.onRemoteMethodCall,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)

    def reqRemoveAvatar(self,
                        unicode_0: str):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(0))  # entitycomponentPropertyID
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(1))

        io_obj.write(deftype.UNICODE_SPEC.kbetype.encode(unicode_0))

        msg = kbeclient.Message(
            spec=msgspec.app.baseapp.onRemoteMethodCall,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)

    def reqRemoveAvatarDBID(self,
                            uid_0: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(0))  # entitycomponentPropertyID
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(2))

        io_obj.write(deftype.UID_SPEC.kbetype.encode(uid_0))

        msg = kbeclient.Message(
            spec=msgspec.app.baseapp.onRemoteMethodCall,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)

    def selectAvatarGame(self,
                         uid_0: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(0))  # entitycomponentPropertyID
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(10004))

        io_obj.write(deftype.UID_SPEC.kbetype.encode(uid_0))

        msg = kbeclient.Message(
            spec=msgspec.app.baseapp.onRemoteMethodCall,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)


class _AccountCellEntityRemoteCall(kbeentity.BaseEntityRemoteCall):
    """Remote call to the CellApp component of the entity."""

    def __init__(self, entity: AccountBase) -> None:
        super().__init__(entity)
        # It's needed for IDE can recoginze the entity type
        self._entity: AccountBase = entity


class AccountBase(kbeentity.Entity):
    CLS_ID = 1
    DESCR = description.DESC_BY_UID[CLS_ID]

    def __init__(self, entity_id: int, entity_mgr: kbeentity.IEntityMgr):
        super().__init__(entity_id, entity_mgr)
        self._cell = _AccountCellEntityRemoteCall(entity=self)
        self._base = _AccountBaseEntityRemoteCall(entity=self)
        self._position: kbetype.Position = kbetype.Position()
        self._direction: kbetype.Direction = kbetype.Direction()
        self._spaceID: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._lastSelCharacter: int = deftype.UID_SPEC.kbetype.default
        self._isDestroyed: bool = False

        self._components: dict[str, IKBEClientEntityComponent] = {
        }

    @property
    def cell(self) -> _AccountCellEntityRemoteCall:
        return self._cell

    @property
    def base(self) -> _AccountBaseEntityRemoteCall:
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
    def lastSelCharacter(self) -> int:
        return self._lastSelCharacter

    def onCreateAvatarResult(self,
                             entity_substate_0: int,
                             avatar_infos_1: kbetype.PluginFixedDict):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    def onRemoveAvatar(self,
                       uid_0: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    def onReqAvatarList(self,
                        avatar_infos_list_0: kbetype.PluginFixedDict):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
