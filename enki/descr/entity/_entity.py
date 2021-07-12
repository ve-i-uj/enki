"""Data types for entities."""

from __future__ import annotations

import functools
from dataclasses import dataclass
from typing import List, Dict, ClassVar

from enki import interface

NO_ENTITY_CLS_ID = 0
NO_ENTITY_ID = 0


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


class _CellEntity:
    """Cell component methods of the entity."""
    pass


class _BaseEntity:
    """Base component methods of the entity."""
    pass


class Entity:
    """Base class for all entities."""
    CLS_ID: ClassVar = NO_ENTITY_CLS_ID  # The unique id of the entity class

    def __init__(self, entity_id: int):
        self._id = entity_id

        self._cell = _CellEntity()
        self._base = _BaseEntity()

    @property
    def cell(self) -> _CellEntity:
        return self._cell

    @property
    def base(self) -> _BaseEntity:
        return self._base

    def __update_properties__(self, properties: dict):
        pass

    def __str__(self):
        return f'{self.__class__.__name__}(id={self._id})'
