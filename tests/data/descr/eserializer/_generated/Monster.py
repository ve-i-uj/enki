"""Generated module represents the entity "Monster" of the file entities.xml"""

from __future__ import annotations

import io
import logging
from typing import Optional, ClassVar


from enki.misc import devonly
from enki import msgspec
from enki.kbetype import *
from enki.msg.message import Message
from enki.apps.clientapp.entity_sub_system.ientity_serializer import (
    EntityBaseRPCSerializer, 
    EntityCellRPCSerializer,
    IEntityRPCSerializer, 
    IEntityComponentRPCSerializer
)
from enki.novalue import NoValue


from ...deftype import *

logger = logging.getLogger(__name__)


class _MonsterBaseRPCSerializer(EntityBaseRPCSerializer):
    """Serialize a remote call to the entity on a BaseApp."""


class _MonsterCellRPCSerializer(EntityCellRPCSerializer):
    """Serialize a remote call to the entity on a CellApp."""


class MonsterRPCSerializer(IEntityRPCSerializer):
    """The serializer RPC of the "Monster" entity."""

    ENTITY_CLS_ID: ClassVar[int] = 5

    def __init__(self) -> None:
        super().__init__()
        self._cell = _MonsterCellRPCSerializer()
        self._base = _MonsterBaseRPCSerializer()


        self._components: dict[str, IEntityComponentRPCSerializer] = {
        }

    def get_component_by_name(self, name: str) -> IEntityComponentRPCSerializer:
        return self._components[name]

    @property
    def cell(self) -> _MonsterCellRPCSerializer:
        return self._cell

    @property
    def base(self) -> _MonsterBaseRPCSerializer:
        return self._base
