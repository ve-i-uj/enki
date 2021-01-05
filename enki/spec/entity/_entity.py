"""Data type for entities."""

import enum
from dataclasses import dataclass
from typing import List

from enki import kbetype


class DistributionFlag(enum.Enum):
    ED_FLAG_UNKNOWN = 0x00000000
    ED_FLAG_CELL_PUBLIC = 0x00000001
    ED_FLAG_CELL_PRIVATE = 0x00000002
    ED_FLAG_ALL_CLIENTS = 0x00000004
    ED_FLAG_CELL_PUBLIC_AND_OWN = 0x00000008
    ED_FLAG_OWN_CLIENT = 0x00000010
    ED_FLAG_BASE_AND_CLIENT = 0x00000020
    ED_FLAG_BASE = 0x00000040
    ED_FLAG_OTHER_CLIENTS = 0x00000080


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

    def __str__(self):
        return f'{self.__class__.__name__}(id=0)'
