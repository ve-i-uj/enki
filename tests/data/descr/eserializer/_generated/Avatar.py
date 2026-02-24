"""Generated module represents the entity "Avatar" of the file entities.xml."""

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

from .components.Test import TestComponentRPCSerializer
from .components.TestNoBase import TestNoBaseComponentRPCSerializer

logger = logging.getLogger(__name__)


class _AvatarBaseRPCSerializer(EntityBaseRPCSerializer):
    """Serialize a remote call to the entity on a BaseApp."""


class _AvatarCellRPCSerializer(EntityCellRPCSerializer):
    """Serialize a remote call to the entity on a CellApp."""

    def dialog(self,
               entity_id: KBEEntityId,
               int32_0: KBEInt32,
               uint32_1: KBEUInt32) -> Message:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(ENTITY_ID.encode(entity_id))
        io_obj.write(UINT16.encode(KBEUInt16(NoValue.NO_COMPONENT_PROPERTY_ID)))
        io_obj.write(ENTITY_METHOD_UID.encode(KBEUInt16(11003)))

        io_obj.write(INT32.encode(int32_0))
        io_obj.write(UINT32.encode(uint32_1))

        return Message.create(
            msgspec.baseapp.onRemoteCallCellMethodFromClient,
            (KBERowByteData(io_obj.getbuffer().tobytes()), )
        )

    def jump(self,
             entity_id: KBEEntityId) -> Message:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(ENTITY_ID.encode(entity_id))
        io_obj.write(UINT16.encode(KBEUInt16(NoValue.NO_COMPONENT_PROPERTY_ID)))
        io_obj.write(ENTITY_METHOD_UID.encode(KBEUInt16(5)))

        return Message.create(
            msgspec.baseapp.onRemoteCallCellMethodFromClient,
            (KBERowByteData(io_obj.getbuffer().tobytes()), )
        )

    def relive(self,
               entity_id: KBEEntityId,
               uint8_0: KBEUInt8) -> Message:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(ENTITY_ID.encode(entity_id))
        io_obj.write(UINT16.encode(KBEUInt16(NoValue.NO_COMPONENT_PROPERTY_ID)))
        io_obj.write(ENTITY_METHOD_UID.encode(KBEUInt16(4)))

        io_obj.write(UINT8.encode(uint8_0))

        return Message.create(
            msgspec.baseapp.onRemoteCallCellMethodFromClient,
            (KBERowByteData(io_obj.getbuffer().tobytes()), )
        )

    def requestPull(self,
                    entity_id: KBEEntityId) -> Message:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(ENTITY_ID.encode(entity_id))
        io_obj.write(UINT16.encode(KBEUInt16(NoValue.NO_COMPONENT_PROPERTY_ID)))
        io_obj.write(ENTITY_METHOD_UID.encode(KBEUInt16(11)))

        return Message.create(
            msgspec.baseapp.onRemoteCallCellMethodFromClient,
            (KBERowByteData(io_obj.getbuffer().tobytes()), )
        )

    def useTargetSkill(self,
                       entity_id: KBEEntityId,
                       int32_0: KBEInt32,
                       int32_1: KBEInt32) -> Message:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(ENTITY_ID.encode(entity_id))
        io_obj.write(UINT16.encode(KBEUInt16(NoValue.NO_COMPONENT_PROPERTY_ID)))
        io_obj.write(ENTITY_METHOD_UID.encode(KBEUInt16(11001)))

        io_obj.write(INT32.encode(int32_0))
        io_obj.write(INT32.encode(int32_1))

        return Message.create(
            msgspec.baseapp.onRemoteCallCellMethodFromClient,
            (KBERowByteData(io_obj.getbuffer().tobytes()), )
        )


class AvatarRPCSerializer(IEntityRPCSerializer):
    """The serializer RPC of the "Avatar" entity."""

    ENTITY_CLS_ID: ClassVar[int] = 2

    def __init__(self) -> None:
        super().__init__()
        self._cell = _AvatarCellRPCSerializer()
        self._base = _AvatarBaseRPCSerializer()

        self._component1 = TestComponentRPCSerializer(owner_attr_id=KBEUInt16(16))
        self._component2 = TestComponentRPCSerializer(owner_attr_id=KBEUInt16(21))
        self._component3 = TestNoBaseComponentRPCSerializer(owner_attr_id=KBEUInt16(22))

        self._components: dict[str, IEntityComponentRPCSerializer] = {
            "component1": self._component1,
            "component2": self._component2,
            "component3": self._component3,
        }

    def get_component_by_name(self, name: str) -> IEntityComponentRPCSerializer:
        return self._components[name]

    @property
    def cell(self) -> _AvatarCellRPCSerializer:
        return self._cell

    @property
    def base(self) -> _AvatarBaseRPCSerializer:
        return self._base

    @property
    def component1(self) -> TestComponentRPCSerializer:
        return self._component1

    @property
    def component2(self) -> TestComponentRPCSerializer:
        return self._component2

    @property
    def component3(self) -> TestNoBaseComponentRPCSerializer:
        return self._component3
