from __future__ import annotations

import io
import logging

from enki import kbetype, kbeclient, kbeentity, descr
from enki.misc import devonly
from enki.interface import IEntity

logger = logging.getLogger(__name__)


class TestBase(kbeentity.EntityComponent):

    def __init__(self, entity: IEntity, own_attr_id: int):
        super().__init__(entity, own_attr_id)
        self._position: kbetype.Vector3Data = descr.deftype.DIRECTION3D_SPEC.kbetype.default
        self._direction: kbetype.Vector3Data = descr.deftype.DIRECTION3D_SPEC.kbetype.default
        self._spaceID: int = descr.deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._own: int = descr.deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self._state: int = descr.deftype.ENTITY_FORBIDS_SPEC.kbetype.default

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
    def own(self) -> int:
        return self._own

    @property
    def state(self) -> int:
        return self._state

    def set_state(self, old_value: int):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    def helloCB(self,
                entity_forbids_0: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())

    def say(self,
            entity_forbids_0: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(self._owner_attr_id))  # entitycomponentPropertyID
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(27))
        msg = kbeclient.Message(
            spec=descr.app.baseapp.onRemoteMethodCall,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)

    def hello(self,
              entity_forbids_0: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(self._owner_attr_id))  # entitycomponentPropertyID
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(26))
        msg = kbeclient.Message(
            spec=descr.app.baseapp.onRemoteCallCellMethodFromClient,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)
