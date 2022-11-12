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
    IEntityRPCSerializer, EntityComponentRPCSerializer

from enki.app.iapp import IApp, IAppEntityRPCSerializer, \
    IAppEntityComponentRPCSerializer


from ... import deftype

logger = logging.getLogger(__name__)


class _MonsterBaseRPCSerializer(EntityBaseRPCSerializer):
    """Serialize a remote call to the entity on a BaseApp."""

    def __init__(self, e_serializer: IEntityRPCSerializer) -> None:
        super().__init__(e_serializer)


class _MonsterCellRPCSerializer(EntityCellRPCSerializer):
    """Serialize a remote call to the entity on a CellApp."""

    def __init__(self, e_serializer: IEntityRPCSerializer) -> None:
        super().__init__(e_serializer)


class MonsterRPCSerializer(IAppEntityRPCSerializer):
    """The serializer RPC of the "Monster" entity."""

    def __init__(self, app: IApp) -> None:
        super().__init__(app)
        self._cell = _MonsterCellRPCSerializer(self)
        self._base = _MonsterBaseRPCSerializer(self)


        self._components: dict[str, IAppEntityComponentRPCSerializer] = {
        }

    @property
    def cell(self) -> _MonsterCellRPCSerializer:
        return self._cell

    @property
    def base(self) -> _MonsterBaseRPCSerializer:
        return self._base

    @property
    def ENTITY_CLS_ID(self) -> int:
        return 5
