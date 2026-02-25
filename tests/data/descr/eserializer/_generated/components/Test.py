"""Generated module represents the entity component "Test"."""

from __future__ import annotations

import io
import logging

from enki.misc import devonly
from enki import msgspec
from enki.kbetype import *
from enki.msg.message import Message
from enki.apps.clientapp.entity_sub_system.ientity_serializer import (
    IEntityComponentRPCSerializer,
    EntityComponentBaseRPCSerializer,
    EntityComponentCellRPCSerializer,
)

from ....deftype import *

logger = logging.getLogger(__name__)


class _TestComponentBaseRPCSerializer(EntityComponentBaseRPCSerializer):
    """Serialize a remote call to the entity component on a BaseApp."""

    def say(self,
            entity_id: KBEEntityId,
            int32_0: KBEInt32) -> Message:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(ENTITY_ID.encode(entity_id))
        io_obj.write(UINT16.encode(self._ec_serializer.owner_attr_id))
        io_obj.write(ENTITY_METHOD_UID.encode(KBEUInt16(27)))

        io_obj.write(INT32.encode(int32_0))

        msg = Message.create(
            msgspec.baseapp.onRemoteMethodCall,
            (KBERowByteData(io_obj.getbuffer().tobytes()), )
        )
        return msg


class _TestComponentCellRPCSerializer(EntityComponentCellRPCSerializer):
    """Serialize a remote call to the entity component on a CellApp."""

    def hello(self,
              entity_id: KBEEntityId,
              int32_0: KBEInt32) -> Message:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(ENTITY_ID.encode(entity_id))
        io_obj.write(UINT16.encode(self._ec_serializer.owner_attr_id))
        io_obj.write(ENTITY_METHOD_UID.encode(KBEUInt16(26)))

        io_obj.write(INT32.encode(int32_0))

        msg = Message.create(
            msgspec.baseapp.onRemoteCallCellMethodFromClient,
            (KBERowByteData(io_obj.getbuffer().tobytes()), )
        )
        return msg


class TestComponentRPCSerializer(IEntityComponentRPCSerializer):
    """The serializer RPC of the "Test" entity."""

    ENTITY_CLS_ID: int = 3

    def __init__(self, owner_attr_id: KBEUInt16) -> None:
        super().__init__(owner_attr_id)

        self._cell = _TestComponentCellRPCSerializer(self)
        self._base = _TestComponentBaseRPCSerializer(self)

    @property
    def cell(self) -> _TestComponentCellRPCSerializer:
        return self._cell

    @property
    def base(self) -> _TestComponentBaseRPCSerializer:
        return self._base
