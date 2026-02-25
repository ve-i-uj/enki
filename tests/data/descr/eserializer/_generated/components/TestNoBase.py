"""Generated module represents the entity component "TestNoBase"."""

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


class _TestNoBaseComponentBaseRPCSerializer(EntityComponentBaseRPCSerializer):
    """Serialize a remote call to the entity component on a BaseApp."""


class _TestNoBaseComponentCellRPCSerializer(EntityComponentCellRPCSerializer):
    """Serialize a remote call to the entity component on a CellApp."""

    def hello(self,
              entity_id: KBEEntityId,
              int32_0: KBEInt32) -> Message:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(ENTITY_ID.encode(entity_id))
        io_obj.write(UINT16.encode(self._ec_serializer.owner_attr_id))
        io_obj.write(ENTITY_METHOD_UID.encode(KBEUInt16(29)))

        io_obj.write(INT32.encode(int32_0))

        msg = Message.create(
            msgspec.baseapp.onRemoteCallCellMethodFromClient,
            (KBERowByteData(io_obj.getbuffer().tobytes()), )
        )
        return msg


class TestNoBaseComponentRPCSerializer(IEntityComponentRPCSerializer):
    """The serializer RPC of the "TestNoBase" entity."""

    ENTITY_CLS_ID: int = 4

    def __init__(self, owner_attr_id: KBEUInt16) -> None:
        super().__init__(owner_attr_id)

        self._cell = _TestNoBaseComponentCellRPCSerializer(self)
        self._base = _TestNoBaseComponentBaseRPCSerializer(self)

    @property
    def cell(self) -> _TestNoBaseComponentCellRPCSerializer:
        return self._cell

    @property
    def base(self) -> _TestNoBaseComponentBaseRPCSerializer:
        return self._base
