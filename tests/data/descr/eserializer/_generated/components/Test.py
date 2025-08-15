"""Generated module represents the entity component "Test"."""

from __future__ import annotations

import io
import logging

from descr import deftype
from enki import msgspec
from enki.apps.clientapp.eserializer import (
    EntityComponentBaseRPCSerializer,
    EntityComponentCellRPCSerializer,
    EntityComponentRPCSerializer,
)
from enki.misc import devonly
from enki.msg.message import Message

logger = logging.getLogger(__name__)


class _TestComponentBaseRPCSerializer(EntityComponentBaseRPCSerializer):
    """Serialize a remote call to the entity component on a BaseApp."""

    def say(self, entity_id: int, entity_forbids_0: int) -> Message:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(ENTITY_ID.encode(entity_id))
        io_obj.write(UINT16.encode(self._ec_serializer.owner_attr_id))
        io_obj.write(ENTITY_METHOD_UID.encode(27))

        io_obj.write(deftype.ENTITY_FORBIDS_SPEC.encode(entity_forbids_0))

        return Message(
            spec=msgspec.baseapp.onRemoteMethodCall,
            fields=(io_obj.getbuffer().tobytes(),),
        )


class _TestComponentCellRPCSerializer(EntityComponentCellRPCSerializer):
    """Serialize a remote call to the entity component on a CellApp."""

    def hello(self, entity_id: int, entity_forbids_0: int) -> Message:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(ENTITY_ID.encode(entity_id))
        io_obj.write(UINT16.encode(self._ec_serializer.owner_attr_id))
        io_obj.write(ENTITY_METHOD_UID.encode(26))

        io_obj.write(deftype.ENTITY_FORBIDS_SPEC.encode(entity_forbids_0))

        return Message(
            spec=msgspec.baseapp.onRemoteCallCellMethodFromClient,
            fields=(io_obj.getbuffer().tobytes(),),
        )


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
