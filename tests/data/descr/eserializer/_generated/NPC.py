"""Generated module represents the entity "NPC" of the file entities.xml"""

from __future__ import annotations

import io
import logging
from functools import cached_property
from typing import Optional

from enki.core.enkitype import NoValue
from enki.misc import devonly
from enki.core import msgspec
from enki.core import kbetype
from enki.core.message import Message
from enki.app.clientapp.eserializer import EntityBaseRPCSerializer, EntityCellRPCSerializer, \
    IEntityRPCSerializer, EntityComponentRPCSerializer


from ... import deftype

logger = logging.getLogger(__name__)


class _NPCBaseRPCSerializer(EntityBaseRPCSerializer):
    """Serialize a remote call to the entity on a BaseApp."""


class _NPCCellRPCSerializer(EntityCellRPCSerializer):
    """Serialize a remote call to the entity on a CellApp."""


class NPCRPCSerializer(IEntityRPCSerializer):
    """The serializer RPC of the "NPC" entity."""

    ENTITY_CLS_ID: int = 6

    def __init__(self) -> None:
        super().__init__()
        self._cell = _NPCCellRPCSerializer()
        self._base = _NPCBaseRPCSerializer()


        self._components: dict[str, EntityComponentRPCSerializer] = {
        }

    def get_component_by_name(self, name: str) -> EntityComponentRPCSerializer:
        return self._components[name]

    @property
    def cell(self) -> _NPCCellRPCSerializer:
        return self._cell

    @property
    def base(self) -> _NPCBaseRPCSerializer:
        return self._base
