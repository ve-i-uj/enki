from __future__ import annotations

import io
import logging

from enki import kbetype, kbeclient, kbeentity, msgspec
from enki.misc import devonly
from enki.interface import IEntity

from .... import deftype
from .. import description

logger = logging.getLogger(__name__)


class TestNoBaseBase(kbeentity.EntityComponent):
    CLS_ID = 4
    DESCR = description.DESC_BY_UID[CLS_ID]

    def __init__(self, entity: IEntity, owner_attr_id: int):
        super().__init__(entity, owner_attr_id)
        self._position: kbetype.Position = kbetype.Position(0.0, 0.0, 0.0)
        self._direction: kbetype.Direction = kbetype.Direction(0.0, 0.0, 0.0)
        self._spaceID: int = deftype.ENTITY_UTYPE_SPEC.kbetype.default
        self._own: int = deftype.ENTITY_FORBIDS_SPEC.kbetype.default
        self._state: int = deftype.ENTITY_FORBIDS_SPEC.kbetype.default

    @property
    def position(self) -> kbetype.Position:
        return self._position

    def set_position(self, old_value: kbetype.Position):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    @property
    def direction(self) -> kbetype.Direction:
        return self._direction

    def set_direction(self, old_value: kbetype.Direction):
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

    def hello(self,
              entity_forbids_0: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(self._entity.id))
        io_obj.write(kbetype.UINT16.encode(self._owner_attr_id))  # entitycomponentPropertyID
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(29))
        msg = kbeclient.Message(
            spec=msgspec.app.baseapp.onRemoteCallCellMethodFromClient,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        self._entity.__remote_call__(msg)
