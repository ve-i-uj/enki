"""Data types for entities."""

import enum
from dataclasses import dataclass
from typing import List


@dataclass
class PropertyData:
    name: str
    default: str
    type_name: str


@dataclass
class MethodData:
    name: str
    arg_types: List[str]


@dataclass
class EntityData:
    name: str
    uid: int
    properties: List[PropertyData]
    client_methods: List[MethodData]
    base_methods: List[MethodData]
    cell_methods: List[MethodData]


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

    @classmethod
    def init_properties(cls):
        pass

    def __str__(self):
        return f'{self.__class__.__name__}(id=0)'
