"""Generated module represents the entity "NPC" of the file entities.xml"""

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

    @property
    def cell(self) -> _NPCCellRPCSerializer:
        return self._cell

    @property
    def base(self) -> _NPCBaseRPCSerializer:
        return self._base
