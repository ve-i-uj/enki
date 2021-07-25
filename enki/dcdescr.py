"""Data classes to describe all generated code.

Data class description --> dcdescr .
"""

import enum
import logging
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from enki import kbetype, kbeentity

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
    field_types: Tuple[kbetype.IKBEType]
    desc: str

    @property
    def short_name(self):
        return self.name.split('::')[1]


@dataclass
class PropertyDesc:
    uid: int  # unique identifier of the property
    name: str  # name of the property
    kbetype: kbetype.IKBEType  # decoder / encoder


@dataclass
class MethodDesc:
    name: str
    arg_types: list[str]


@dataclass
class EntityDesc:
    name: str
    uid: int
    cls: kbeentity.Entity
    property_desc_by_id: Dict[int, PropertyDesc]
    client_methods: list[MethodDesc]
    base_methods: list[MethodDesc]
    cell_methods: list[MethodDesc]


@dataclass(frozen=True)
class ServerErrorDescr:
    """Description of server errors.

    It's a representation of server files server_errors_defaults.xml / server_errors.xml
    """
    id: int
    name: str
    desc: str
