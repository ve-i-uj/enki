"""Generated module represents the entity "Monster" of the file entities.xml"""

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

    @property
    def cell(self) -> _MonsterCellRPCSerializer:
        return self._cell

    @property
    def base(self) -> _MonsterBaseRPCSerializer:
        return self._base
