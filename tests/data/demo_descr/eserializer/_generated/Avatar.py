"""Generated module represents the entity "Avatar" of the file entities.xml"""

from __future__ import annotations

import io
import logging
from functools import cached_property
from typing import Optional

from enki import settings
from enki.misc import devonly
from enki.net import msgspec
from enki.net.kbeclient import kbetype, Message
from enki.net.netentity import EntityBaseRPCSerializer, EntityCellRPCSerializer, \
    IEntityRPCSerializer, EntityComponentRPCSerializer, IEntityRPCSerializer

from .components.Test import TestComponentRPCSerializer
from .components.TestNoBase import TestNoBaseComponentRPCSerializer

from ... import deftype

logger = logging.getLogger(__name__)


class _AvatarBaseRPCSerializer(EntityBaseRPCSerializer):
    """Serialize a remote call to the entity on a BaseApp."""


class _AvatarCellRPCSerializer(EntityCellRPCSerializer):
    """Serialize a remote call to the entity on a CellApp."""

    def dialog(self,
               entity_id: int,
               entity_forbids_0: int,
               entity_utype_1: int) -> Message:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(entity_id))
        io_obj.write(kbetype.UINT16.encode(settings.NO_COMPONENT_PROPERTY_ID))
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(11003))

        io_obj.write(deftype.ENTITY_FORBIDS_SPEC.kbetype.encode(entity_forbids_0))
        io_obj.write(deftype.ENTITY_UTYPE_SPEC.kbetype.encode(entity_utype_1))

        msg = Message(
            spec=msgspec.app.baseapp.onRemoteCallCellMethodFromClient,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        return msg

    def jump(self,
             entity_id: int) -> Message:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(entity_id))
        io_obj.write(kbetype.UINT16.encode(settings.NO_COMPONENT_PROPERTY_ID))
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(5))

        msg = Message(
            spec=msgspec.app.baseapp.onRemoteCallCellMethodFromClient,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        return msg

    def relive(self,
               entity_id: int,
               entity_substate_0: int) -> Message:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(entity_id))
        io_obj.write(kbetype.UINT16.encode(settings.NO_COMPONENT_PROPERTY_ID))
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(4))

        io_obj.write(deftype.ENTITY_SUBSTATE_SPEC.kbetype.encode(entity_substate_0))

        msg = Message(
            spec=msgspec.app.baseapp.onRemoteCallCellMethodFromClient,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        return msg

    def requestPull(self,
                    entity_id: int) -> Message:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(entity_id))
        io_obj.write(kbetype.UINT16.encode(settings.NO_COMPONENT_PROPERTY_ID))
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(11))

        msg = Message(
            spec=msgspec.app.baseapp.onRemoteCallCellMethodFromClient,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        return msg

    def useTargetSkill(self,
                       entity_id: int,
                       entity_forbids_0: int,
                       entity_forbids_1: int) -> Message:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(entity_id))
        io_obj.write(kbetype.UINT16.encode(settings.NO_COMPONENT_PROPERTY_ID))
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(11001))

        io_obj.write(deftype.ENTITY_FORBIDS_SPEC.kbetype.encode(entity_forbids_0))
        io_obj.write(deftype.ENTITY_FORBIDS_SPEC.kbetype.encode(entity_forbids_1))

        msg = Message(
            spec=msgspec.app.baseapp.onRemoteCallCellMethodFromClient,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        return msg


class AvatarRPCSerializer(IEntityRPCSerializer):
    """The serializer RPC of the "Avatar" entity."""

    ENTITY_CLS_ID: int = 2

    def __init__(self) -> None:
        super().__init__()
        self._cell = _AvatarCellRPCSerializer()
        self._base = _AvatarBaseRPCSerializer()

        self._component1 = TestComponentRPCSerializer(owner_attr_id=16)
        self._component2 = TestComponentRPCSerializer(owner_attr_id=21)
        self._component3 = TestNoBaseComponentRPCSerializer(owner_attr_id=22)

        self._components: dict[str, EntityComponentRPCSerializer] = {
            'component1': self._component1,
            'component2': self._component2,
            'component3': self._component3,
        }

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
