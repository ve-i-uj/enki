"""Generated module represents the entity "Account" of the file entities.xml."""

from __future__ import annotations

import io
import logging
from typing import ClassVar

from descr.deftype import *
from enki import msgspec
from enki.apps.clientapp.entity_sub_system.ientity_serializer import (
    EntityBaseRPCSerializer,
    EntityCellRPCSerializer,
    IEntityComponentRPCSerializer,
    IEntityRPCSerializer,
)
from enki.kbetype import *
from enki.misc import devonly
from enki.msg.message import Message
from enki.novalue import NoValue

logger = logging.getLogger(__name__)


class _AccountBaseRPCSerializer(EntityBaseRPCSerializer):
    """Serialize a remote call to the entity on a BaseApp."""

    def reqAvatarList(self,
                      entity_id: KBEEntityId) -> Message:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(ENTITY_ID.encode(entity_id))
        io_obj.write(UINT16.encode(KBEUInt16(NoValue.NO_COMPONENT_PROPERTY_ID)))
        io_obj.write(ENTITY_METHOD_UID.encode(KBEUInt16(10001)))

        return Message.create(
            msgspec.baseapp.onRemoteMethodCall,
            (KBERowByteData(io_obj.getbuffer().tobytes()), )
        )

    def reqCreateAvatar(self,
                        entity_id: KBEEntityId,
                        uint8_0: KBEUInt8,
                        unicode_1: KBEUnicode) -> Message:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(ENTITY_ID.encode(entity_id))
        io_obj.write(UINT16.encode(KBEUInt16(NoValue.NO_COMPONENT_PROPERTY_ID)))
        io_obj.write(ENTITY_METHOD_UID.encode(KBEUInt16(10002)))

        io_obj.write(UINT8.encode(uint8_0))
        io_obj.write(UNICODE.encode(unicode_1))

        return Message.create(
            msgspec.baseapp.onRemoteMethodCall,
            (KBERowByteData(io_obj.getbuffer().tobytes()), )
        )

    def reqRemoveAvatar(self,
                        entity_id: KBEEntityId,
                        unicode_0: KBEUnicode) -> Message:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(ENTITY_ID.encode(entity_id))
        io_obj.write(UINT16.encode(KBEUInt16(NoValue.NO_COMPONENT_PROPERTY_ID)))
        io_obj.write(ENTITY_METHOD_UID.encode(KBEUInt16(1)))

        io_obj.write(UNICODE.encode(unicode_0))

        return Message.create(
            msgspec.baseapp.onRemoteMethodCall,
            (KBERowByteData(io_obj.getbuffer().tobytes()), )
        )

    def reqRemoveAvatarDBID(self,
                            entity_id: KBEEntityId,
                            uint64_0: KBEUInt64) -> Message:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(ENTITY_ID.encode(entity_id))
        io_obj.write(UINT16.encode(KBEUInt16(NoValue.NO_COMPONENT_PROPERTY_ID)))
        io_obj.write(ENTITY_METHOD_UID.encode(KBEUInt16(2)))

        io_obj.write(UINT64.encode(uint64_0))

        return Message.create(
            msgspec.baseapp.onRemoteMethodCall,
            (KBERowByteData(io_obj.getbuffer().tobytes()), )
        )

    def selectAvatarGame(self,
                         entity_id: KBEEntityId,
                         uint64_0: KBEUInt64) -> Message:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(ENTITY_ID.encode(entity_id))
        io_obj.write(UINT16.encode(KBEUInt16(NoValue.NO_COMPONENT_PROPERTY_ID)))
        io_obj.write(ENTITY_METHOD_UID.encode(KBEUInt16(10004)))

        io_obj.write(UINT64.encode(uint64_0))

        return Message.create(
            msgspec.baseapp.onRemoteMethodCall,
            (KBERowByteData(io_obj.getbuffer().tobytes()), )
        )


class _AccountCellRPCSerializer(EntityCellRPCSerializer):
    """Serialize a remote call to the entity on a CellApp."""


class AccountRPCSerializer(IEntityRPCSerializer):
    """The serializer RPC of the "Account" entity."""

    ENTITY_CLS_ID: ClassVar[int] = 1

    def __init__(self) -> None:
        super().__init__()
        self._cell = _AccountCellRPCSerializer()
        self._base = _AccountBaseRPCSerializer()


        self._components: dict[str, IEntityComponentRPCSerializer] = {
        }

    def get_component_by_name(self, name: str) -> IEntityComponentRPCSerializer:
        return self._components[name]

    @property
    def cell(self) -> _AccountCellRPCSerializer:
        return self._cell

    @property
    def base(self) -> _AccountBaseRPCSerializer:
        return self._base
