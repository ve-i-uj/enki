"""Generated module represents the entity "Test" of the file entities.xml"""

import collections
import io
import logging

from enki import kbetype, kbeclient, kbeentity, descr
from enki.misc import devonly

logger = logging.getLogger(__name__)


class _TestBaseEntityRemoteCall(kbeentity.BaseEntityRemoteCall):
    """Remote call to the BaseApp component of the entity."""

    def say(self, arg_0: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(0))  # entitycomponentPropertyID ??
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(27))
        io_obj.write(descr.deftype.ENTITY_FORBIDS_SPEC.kbetype.encode(arg_0))
        
        msg = kbeclient.Message(
            spec=descr.app.baseapp.onRemoteMethodCall,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)


class _TestCellEntityRemoteCall(kbeentity.BaseEntityRemoteCall):
    """Remote call to the CellApp component of the entity."""

    def hello(self, arg_0: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(0))  # entitycomponentPropertyID ??
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(26))
        io_obj.write(descr.deftype.ENTITY_FORBIDS_SPEC.kbetype.encode(arg_0))
        
        msg = kbeclient.Message(
            spec=descr.app.baseapp.onRemoteCallCellMethodFromClient,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)


class TestBase(kbeentity.Entity):
    CLS_ID = 3

    def __init__(self, entity_id: int, entity_mgr: kbeentity.IEntityMgr):
        super().__init__(entity_id, entity_mgr)
        self._cell = _TestCellEntityRemoteCall(entity=self)
        self._base = _TestBaseEntityRemoteCall(entity=self)

        self._set_property_names = set(['position', 'direction', 'state'])

        self.__position: kbetype.Vector3Data = descr.deftype.DIRECTION3D_SPEC.kbetype.default
        self.__direction: kbetype.Vector3Data = descr.deftype.DIRECTION3D_SPEC.kbetype.default
        self.__spaceID: int = descr.deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self.__own: int = descr.deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self.__state: int = descr.deftype.ENTITY_FORBIDS_SPEC.kbetype.default

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
    def own(self) -> int:
        return self.__own

    @property
    def state(self) -> int:
        return self.__state

    def set_state(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    def helloCB(self,
                entity_forbids_0: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
