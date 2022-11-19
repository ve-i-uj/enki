"""Generated module represents the entity component "TestNoBase"."""

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


class _TestNoBaseComponentBaseRPCSerializer(EntityComponentBaseRPCSerializer):
    """Serialize a remote call to the entity component on a BaseApp."""


class _TestNoBaseComponentCellRPCSerializer(EntityComponentCellRPCSerializer):
    """Serialize a remote call to the entity component on a CellApp."""

    def hello(self,
              entity_id: int,
              entity_forbids_0: int) -> Message:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(entity_id))
        io_obj.write(kbetype.UINT16.encode(self._ec_serializer.owner_attr_id))
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(29))

        io_obj.write(deftype.ENTITY_FORBIDS_SPEC.kbetype.encode(entity_forbids_0))

        msg = Message(
            spec=msgspec.app.baseapp.onRemoteCallCellMethodFromClient,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        return msg


class TestNoBaseComponentRPCSerializer(EntityComponentRPCSerializer):
    """The serializer RPC of the "TestNoBase" entity."""

    ENTITY_CLS_ID: int = 4

    def __init__(self, owner_attr_id: int) -> None:
        super().__init__(owner_attr_id)

        self._cell = _TestNoBaseComponentCellRPCSerializer(self)
        self._base = _TestNoBaseComponentBaseRPCSerializer(self)

    @property
    def cell(self) -> _TestNoBaseComponentCellRPCSerializer:
        return self._cell

    @property
    def base(self) -> _TestNoBaseComponentBaseRPCSerializer:
        return self._base
