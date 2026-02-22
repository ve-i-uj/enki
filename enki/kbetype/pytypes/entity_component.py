from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import TYPE_CHECKING

from enki.kbetype.ikbetype import IKBEType

if TYPE_CHECKING:
    from enki.kbetype.pytypes.basic_data_types import (
        KBEInt32,
        KBEUInt16,
        KBEUInt32,
    )


@dataclass
class EntityComponentData(IKBEType):
    component_type: KBEUInt32
    owner_id: KBEInt32
    component_ent_id: KBEUInt16
    count: KBEUInt16
    entity_component_property_id: int | None = None
    name: str | None = None
    properties: dict = dataclasses.field(default_factory=dict)
