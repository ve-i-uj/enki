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
    IEntityRPCSerializer, EntityComponentRPCSerializer

from enki.app.iapp import IApp, IAppEntityRPCSerializer, \
    IAppEntityComponentRPCSerializer


from ... import deftype

logger = logging.getLogger(__name__)


class _NPCBaseRPCSerializer(EntityBaseRPCSerializer):
    """Serialize a remote call to the entity on a BaseApp."""

    def __init__(self, e_serializer: IEntityRPCSerializer) -> None:
        super().__init__(e_serializer)


class _NPCCellRPCSerializer(EntityCellRPCSerializer):
    """Serialize a remote call to the entity on a CellApp."""

    def __init__(self, e_serializer: IEntityRPCSerializer) -> None:
        super().__init__(e_serializer)


class NPCRPCSerializer(IAppEntityRPCSerializer):
    """The serializer RPC of the "NPC" entity."""

    def __init__(self, app: IApp) -> None:
        super().__init__(app)
        self._cell = _NPCCellRPCSerializer(self)
        self._base = _NPCBaseRPCSerializer(self)


        self._components: dict[str, IAppEntityComponentRPCSerializer] = {
        }

    @property
    def cell(self) -> _NPCCellRPCSerializer:
        return self._cell

    @property
    def base(self) -> _NPCBaseRPCSerializer:
        return self._base

    @property
    def ENTITY_CLS_ID(self) -> int:
        return 6
