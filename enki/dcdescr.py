"""Data classes to describe all generated code.

Data class description --> dcdescr .
"""

from __future__ import annotations
import enum
import logging
from dataclasses import dataclass
from typing import Dict, Optional

from enki import kbetype, kbeenum
from enki.interface import IEntity

logger = logging.getLogger(__name__)


@dataclass
class DataTypeDescr:
    """Specification of type from the file 'types.xml'."""
    id: int
    base_type_name: str
    name: str
    # decoder / encoder of kbe type_spec
    kbetype: kbetype.IKBEType

    # FIXED_DICT data
    module_name: Optional[str] = None
    pairs: Optional[Dict[str, kbetype.IKBEType]] = None

    # ARRAY data
    of: Optional[kbetype.IKBEType] = None

    @property
    def is_alias(self) -> bool:
        return self.name != self.base_type_name

    @property
    def is_fixed_dict(self) -> bool:
        return self.pairs is not None or self.fd_type_id_by_key is not None

    @property
    def is_array(self) -> bool:
        return self.of is not None or self.arr_of_id is not None

    @property
    def type_name(self) -> str:
        if not self.name or self.name.startswith('_'):
            # It's an inner defined type
            return f'{self.base_type_name}_{self.id}'
        return self.name


class MsgArgsType(enum.IntEnum):
    """Fixed or variable length of message (see MESSAGE_ARGS_TYPE)"""
    VARIABLE = -1
    FIXED = 0


@dataclass(frozen=True)
class MessageDescr:
    """Specification of a message (see messages_fixed_defaults.xml)"""
    id: int
    name: str
    args_type: MsgArgsType
    field_types: tuple[kbetype.IKBEType, ...]
    desc: str

    @property
    def short_name(self):
        return self.name.split('::')[1]


@dataclass
class PropertyDesc:
    uid: int  # unique identifier of the property
    name: str  # name of the property
    kbetype: kbetype.IKBEType  # decoder / encoder
    distribution_flag: kbeenum.DistributionFlag
    alias_id: int  # see aliasEntityID in kbengine.xml


@dataclass
class MethodDesc:
    uid: int  # the unique identifier of the method
    alias_id: int
    name: str
    kbetypes: list[kbetype.IKBEType]


@dataclass
class EntityDesc:
    name: str
    uid: int
    cls: IEntity
    property_desc_by_id: Dict[int, PropertyDesc]
    client_methods: list[MethodDesc]
    base_methods: list[MethodDesc]
    cell_methods: list[MethodDesc]

    @property
    def is_optimized_prop_uid(self) -> bool:
        return any(p.alias_id != -1 for p in self.property_desc_by_id.values())

    @property
    def is_optimized_cl_method_uid(self) -> bool:
        return any(m.alias_id != -1 for m in self.client_methods.values())


@dataclass(frozen=True)
class ServerErrorDescr:
    """Description of server errors.

    It's a representation of server files server_errors_defaults.xml / server_errors.xml
    """
    id: int
    name: str
    desc: str
