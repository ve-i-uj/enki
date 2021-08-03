"""Generated module represents the entity "Account" of the file entities.xml"""

import collections
import io
import logging

from enki import kbetype, kbeclient, kbeentity, descr
from enki.misc import devonly

logger = logging.getLogger(__name__)


class _AccountBaseEntityRemoteCall(kbeentity.BaseEntityRemoteCall):
    """Remote call to the BaseApp component of the entity."""

    def req_get_avatars(self, arg_0: int, arg_1: str):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()        
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(0))  # entitycomponentPropertyID ??
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(2))
        io_obj.write(descr.deftype.AVATAR_UID_SPEC.kbetype.encode(arg_0)) 
        io_obj.write(descr.deftype.AVATAR_NAME_SPEC.kbetype.encode(arg_1)) 
        
        msg = kbeclient.Message(
            spec=descr.app.baseapp.onRemoteMethodCall,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)


class _AccountCellEntityRemoteCall(kbeentity.BaseEntityRemoteCall):
    """Remote call to the CellApp component of the entity."""

    def cellapp_method(self, arg_0: str, arg_1: kbetype.Array):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()        
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(0))  # entitycomponentPropertyID ??
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(1))
        io_obj.write(descr.deftype.STRING_SPEC.kbetype.encode(arg_0)) 
        io_obj.write(descr.deftype.AVATAR_INFO_LIST_SPEC.kbetype.encode(arg_1)) 
        
        msg = kbeclient.Message(
            spec=descr.app.baseapp.onRemoteCallCellMethodFromClient,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)


class AccountBase(kbeentity.Entity):
    CLS_ID = 1

    def __init__(self, entity_id: int, entity_mgr: kbeentity.IEntityMgr):
        super().__init__(entity_id, entity_mgr) 
        self._cell = _AccountCellEntityRemoteCall(entity=self)
        self._base = _AccountBaseEntityRemoteCall(entity=self)

        self._set_property_names = set(['position', 'direction', 'name'])

        self.__position: kbetype.Vector3Data = descr.deftype.VECTOR3_SPEC.kbetype.default
        self.__direction: kbetype.Vector3Data = descr.deftype.VECTOR3_SPEC.kbetype.default
        self.__spaceID: int = descr.deftype.UINT32_SPEC.kbetype.default
        self.__name: str = descr.deftype.AVATAR_NAME_SPEC.kbetype.default

    @property
    def position(self) -> kbetype.Vector3Data:
        return self.__position
    
    def set_position(self, old_value: kbetype.Vector3Data):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
    
    @property
    def direction(self) -> kbetype.Vector3Data:
        return self.__direction
    
    def set_direction(self, old_value: kbetype.Vector3Data):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
    
    @property
    def spaceID(self) -> int:
        return self.__spaceID
    
    @property
    def name(self) -> str:
        return self.__name
    
    def set_name(self, old_value: str):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
    
    def resp_get_avatars(self,
                         avatar_dbids: kbetype.PluginFixedDict,
                         array_27: kbetype.Array):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
