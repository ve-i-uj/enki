"""Generated module represents the entity "Account" of the file entities.xml"""

import collections
import io
import logging

from enki import kbetype, kbeclient, kbeentity, descr
from enki.misc import devonly

logger = logging.getLogger(__name__)


class _AccountBaseEntityRemoteCall(kbeentity.BaseEntityRemoteCall):
    """Remote call to the BaseApp component of the entity."""

    def reqAvatarList(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(0))  # entitycomponentPropertyID ??
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(10001))
        
        msg = kbeclient.Message(
            spec=descr.app.baseapp.onRemoteMethodCall,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)

    def reqCreateAvatar(self, arg_0: int, arg_1: str):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(0))  # entitycomponentPropertyID ??
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(10002))
        io_obj.write(descr.deftype.ENTITY_SUBSTATE_SPEC.kbetype.encode(arg_0))
        io_obj.write(descr.deftype.UNICODE_SPEC.kbetype.encode(arg_1))
        
        msg = kbeclient.Message(
            spec=descr.app.baseapp.onRemoteMethodCall,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)

    def reqRemoveAvatar(self, arg_0: str):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(0))  # entitycomponentPropertyID ??
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(1))
        io_obj.write(descr.deftype.UNICODE_SPEC.kbetype.encode(arg_0))
        
        msg = kbeclient.Message(
            spec=descr.app.baseapp.onRemoteMethodCall,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)

    def reqRemoveAvatarDBID(self, arg_0: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(0))  # entitycomponentPropertyID ??
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(2))
        io_obj.write(descr.deftype.UID_SPEC.kbetype.encode(arg_0))
        
        msg = kbeclient.Message(
            spec=descr.app.baseapp.onRemoteMethodCall,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)

    def selectAvatarGame(self, arg_0: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(0))  # entitycomponentPropertyID ??
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(10004))
        io_obj.write(descr.deftype.UID_SPEC.kbetype.encode(arg_0))
        
        msg = kbeclient.Message(
            spec=descr.app.baseapp.onRemoteMethodCall,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)


class _AccountCellEntityRemoteCall(kbeentity.BaseEntityRemoteCall):
    """Remote call to the CellApp component of the entity."""


class AccountBase(kbeentity.Entity):
    CLS_ID = 1

    def __init__(self, entity_id: int, entity_mgr: kbeentity.IEntityMgr):
        super().__init__(entity_id, entity_mgr)
        self._cell = _AccountCellEntityRemoteCall(entity=self)
        self._base = _AccountBaseEntityRemoteCall(entity=self)

        self._set_property_names = set(['position', 'direction'])

        self._position: kbetype.Vector3Data = descr.deftype.DIRECTION3D_SPEC.kbetype.default
        self._direction: kbetype.Vector3Data = descr.deftype.DIRECTION3D_SPEC.kbetype.default
        self._spaceID: int = descr.deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._lastSelCharacter: int = descr.deftype.UID_SPEC.kbetype.default

    @property
    def cell(self) -> _AccountCellEntityRemoteCall:
        return self._cell

    @property
    def base(self) -> _AccountBaseEntityRemoteCall:
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
