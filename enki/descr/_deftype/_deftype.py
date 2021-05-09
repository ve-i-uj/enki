"""Assets' types."""

import logging
from dataclasses import dataclass
from typing import Dict, Optional

from enki import interface

logger = logging.getLogger(__name__)


@dataclass
class DataTypeSpec:
    """Specification of type from the file 'types.xml'."""
    id: int
    base_type_name: str
    name: str
    # decoder / encoder of kbe type_spec
    kbetype: interface.IKBEType

    # FIXED_DICT data
    module_name: Optional[str] = None
    pairs: Optional[Dict[str, interface.IKBEType]] = None

    # ARRAY data
    of: Optional[interface.IKBEType] = None

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
