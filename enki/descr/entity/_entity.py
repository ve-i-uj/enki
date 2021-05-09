"""Data types for entities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict

from enki import interface


@dataclass
class PropertyDesc:
    uid: int  # unique identifier of the property
    name: str  # name of the property
    kbetype: interface.IKBEType  # decoder / encoder


@dataclass
class MethodDesc:
    name: str
    arg_types: List[str]


@dataclass
class EntityDesc:
    name: str
    uid: int
    cls: Entity
    property_desc_by_id: Dict[int, PropertyDesc]
    client_methods: List[MethodDesc]
    base_methods: List[MethodDesc]
    cell_methods: List[MethodDesc]


class Entity:
    """Base class for all entities."""
    ID = 0

    class _Cell:
        """Cell component methods of the entity."""
        pass

    class _Base:
        """Base component methods of the entity."""
        pass

    def __init__(self):
        self.cell = self._Cell()
        self.base = self._Base()

    def __update_properties__(self, properties: Dict):
        pass

    def __str__(self):
        return f'{self.__class__.__name__}(id=0)'
