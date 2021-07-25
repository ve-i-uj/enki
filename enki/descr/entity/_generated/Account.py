"""Generated module represents the entity "Account" of the file entities.xml"""

import collections
import io
import logging

from enki import kbetype, kbeclient, kbeentity, descr
from enki.misc import devonly

logger = logging.getLogger(__name__)


class _AccountBaseEntityRemoteCall(kbeentity.BaseEntityRemoteCall):
    """Remote call to the BaseApp component of the entity."""

    def req_test_base_method(self, arg_0: str):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()        
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(0))  # entitycomponentPropertyID ??
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(2))
        io_obj.write(descr.deftype.AVATAR_NAME_SPEC.kbetype.encode(arg_0))
        msg = kbeclient.Message(
            spec=descr.app.baseapp.onRemoteMethodCall,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)
        

class _AccountCellEntityRemoteCall(kbeentity.BaseEntityRemoteCall):
    """Remote call to the CellApp component of the entity."""

    def req_test_cell_method(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        

class AccountBase(kbeentity.Entity):
    CLS_ID = 1

    def __init__(self, entity_id: int, entity_mgr: kbeentity.IEntityMgr):
        super().__init__(entity_id, entity_mgr) 
        self._cell = _AccountCellEntityRemoteCall(entity=self)
        self._base = _AccountBaseEntityRemoteCall(entity=self)

        self.__position: kbetype.Vector3Data = descr.deftype.VECTOR3_SPEC.kbetype.default
        self.__direction: kbetype.Vector3Data = descr.deftype.VECTOR3_SPEC.kbetype.default
        self.__spaceID: int = descr.deftype.UINT32_SPEC.kbetype.default
        self.__test_alias_DBID: int = descr.deftype.DBID_SPEC.kbetype.default
        self.__test_type_ARRAY_of_FIXED_DICT: kbetype.Array = descr.deftype.AVATAR_INFO_LIST_SPEC.kbetype.default
        self.__test_type_FIXED_DICT: kbetype.PluginFixedDict = descr.deftype.AVATAR_INFO_SPEC.kbetype.default
        self.__test_type_VECTOR2: kbetype.Vector2Data = descr.deftype.VECTOR2_SPEC.kbetype.default
        self.__test_type_VECTOR3: kbetype.Vector3Data = descr.deftype.VECTOR3_SPEC.kbetype.default
        self.__test_type_VECTOR4: kbetype.Vector4Data = descr.deftype.VECTOR4_SPEC.kbetype.default

    @property
    def position(self) -> kbetype.Vector3Data:
        return self.__position

    @property
    def direction(self) -> kbetype.Vector3Data:
        return self.__direction

    @property
    def spaceID(self) -> int:
        return self.__spaceID

    @property
    def test_alias_DBID(self) -> int:
        return self.__test_alias_DBID

    @property
    def test_type_ARRAY_of_FIXED_DICT(self) -> kbetype.Array:
        return self.__test_type_ARRAY_of_FIXED_DICT

    @property
    def test_type_FIXED_DICT(self) -> kbetype.PluginFixedDict:
        return self.__test_type_FIXED_DICT

    @property
    def test_type_VECTOR2(self) -> kbetype.Vector2Data:
        return self.__test_type_VECTOR2

    @property
    def test_type_VECTOR3(self) -> kbetype.Vector3Data:
        return self.__test_type_VECTOR3

    @property
    def test_type_VECTOR4(self) -> kbetype.Vector4Data:
        return self.__test_type_VECTOR4

    def resp_get_avatars(self,
                         avatar_dbids: kbetype.PluginFixedDict,
                         array_27: kbetype.Array):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
