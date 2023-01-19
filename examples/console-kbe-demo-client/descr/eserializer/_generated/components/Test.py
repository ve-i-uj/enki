"""Generated module represents the entity component "Test"."""

from __future__ import annotations

import io
import logging
from functools import cached_property
from typing import Optional

from enki.misc import devonly
from enki.net import msgspec
from enki.net.kbeclient import kbetype, Message
from enki.net.netentity import EntityComponentBaseRPCSerializer, \
    EntityComponentCellRPCSerializer, EntityComponentRPCSerializer

from .... import deftype

logger = logging.getLogger(__name__)


class _TestComponentBaseRPCSerializer(EntityComponentBaseRPCSerializer):
    """Serialize a remote call to the entity component on a BaseApp."""

    def say(self,
            entity_id: int,
            entity_forbids_0: int) -> Message:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(entity_id))
        io_obj.write(kbetype.UINT16.encode(self._ec_serializer.owner_attr_id))
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(27))

        io_obj.write(deftype.ENTITY_FORBIDS_SPEC.kbetype.encode(entity_forbids_0))

        msg = Message(
            spec=msgspec.app.baseapp.onRemoteMethodCall,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        return msg


class _TestComponentCellRPCSerializer(EntityComponentCellRPCSerializer):
    """Serialize a remote call to the entity component on a CellApp."""

    def hello(self,
              entity_id: int,
              entity_forbids_0: int) -> Message:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(entity_id))
        io_obj.write(kbetype.UINT16.encode(self._ec_serializer.owner_attr_id))
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(26))

        io_obj.write(deftype.ENTITY_FORBIDS_SPEC.kbetype.encode(entity_forbids_0))

        msg = Message(
            spec=msgspec.app.baseapp.onRemoteCallCellMethodFromClient,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        return msg


class TestComponentRPCSerializer(EntityComponentRPCSerializer):
    """The serializer RPC of the "Test" entity."""

    ENTITY_CLS_ID: int = 3

    def __init__(self, owner_attr_id: int) -> None:
        super().__init__(owner_attr_id)

        self._cell = _TestComponentCellRPCSerializer(self)
        self._base = _TestComponentBaseRPCSerializer(self)

    @property
    def cell(self) -> _TestComponentCellRPCSerializer:
        return self._cell

    @property
    def base(self) -> _TestComponentBaseRPCSerializer:
        return self._base
