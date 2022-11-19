"""Generated module represents the entity "Account" of the file entities.xml"""

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


from ... import deftype

logger = logging.getLogger(__name__)


class _AccountBaseRPCSerializer(EntityBaseRPCSerializer):
    """Serialize a remote call to the entity on a BaseApp."""

    def reqAvatarList(self,
                      entity_id: int) -> Message:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(entity_id))
        io_obj.write(kbetype.UINT16.encode(settings.NO_COMPONENT_PROPERTY_ID))
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(10001))

        msg = Message(
            spec=msgspec.app.baseapp.onRemoteMethodCall,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        return msg

    def reqCreateAvatar(self,
                        entity_id: int,
                        entity_substate_0: int,
                        unicode_1: str) -> Message:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(entity_id))
        io_obj.write(kbetype.UINT16.encode(settings.NO_COMPONENT_PROPERTY_ID))
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(10002))

        io_obj.write(deftype.ENTITY_SUBSTATE_SPEC.kbetype.encode(entity_substate_0))
        io_obj.write(deftype.UNICODE_SPEC.kbetype.encode(unicode_1))

        msg = Message(
            spec=msgspec.app.baseapp.onRemoteMethodCall,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        return msg

    def reqRemoveAvatar(self,
                        entity_id: int,
                        unicode_0: str) -> Message:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(entity_id))
        io_obj.write(kbetype.UINT16.encode(settings.NO_COMPONENT_PROPERTY_ID))
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(1))

        io_obj.write(deftype.UNICODE_SPEC.kbetype.encode(unicode_0))

        msg = Message(
            spec=msgspec.app.baseapp.onRemoteMethodCall,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        return msg

    def reqRemoveAvatarDBID(self,
                            entity_id: int,
                            uid_0: int) -> Message:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(entity_id))
        io_obj.write(kbetype.UINT16.encode(settings.NO_COMPONENT_PROPERTY_ID))
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(2))

        io_obj.write(deftype.UID_SPEC.kbetype.encode(uid_0))

        msg = Message(
            spec=msgspec.app.baseapp.onRemoteMethodCall,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        return msg

    def selectAvatarGame(self,
                         entity_id: int,
                         uid_0: int) -> Message:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(entity_id))
        io_obj.write(kbetype.UINT16.encode(settings.NO_COMPONENT_PROPERTY_ID))
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(10004))

        io_obj.write(deftype.UID_SPEC.kbetype.encode(uid_0))

        msg = Message(
            spec=msgspec.app.baseapp.onRemoteMethodCall,
            fields=(io_obj.getbuffer().tobytes(), )
        )
        return msg


class _AccountCellRPCSerializer(EntityCellRPCSerializer):
    """Serialize a remote call to the entity on a CellApp."""


class AccountRPCSerializer(IEntityRPCSerializer):
    """The serializer RPC of the "Account" entity."""

    ENTITY_CLS_ID: int = 1

    def __init__(self) -> None:
        super().__init__()
        self._cell = _AccountCellRPCSerializer()
        self._base = _AccountBaseRPCSerializer()


        self._components: dict[str, EntityComponentRPCSerializer] = {
        }

    @property
    def cell(self) -> _AccountCellRPCSerializer:
        return self._cell

    @property
    def base(self) -> _AccountBaseRPCSerializer:
        return self._base
