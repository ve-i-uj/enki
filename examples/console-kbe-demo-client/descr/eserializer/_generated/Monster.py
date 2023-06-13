"""Generated module represents the entity "Monster" of the file entities.xml"""

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


class _MonsterBaseRPCSerializer(EntityBaseRPCSerializer):
    """Serialize a remote call to the entity on a BaseApp."""


class _MonsterCellRPCSerializer(EntityCellRPCSerializer):
    """Serialize a remote call to the entity on a CellApp."""


class MonsterRPCSerializer(IEntityRPCSerializer):
    """The serializer RPC of the "Monster" entity."""

    ENTITY_CLS_ID: int = 5

    def __init__(self) -> None:
        super().__init__()
        self._cell = _MonsterCellRPCSerializer()
        self._base = _MonsterBaseRPCSerializer()


        self._components: dict[str, EntityComponentRPCSerializer] = {
        }

    def get_component_by_name(self, name: str) -> EntityComponentRPCSerializer:
        return self._components[name]

    @property
    def cell(self) -> _MonsterCellRPCSerializer:
        return self._cell

    @property
    def base(self) -> _MonsterBaseRPCSerializer:
        return self._base
