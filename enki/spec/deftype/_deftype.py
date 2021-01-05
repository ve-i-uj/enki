"""Assets' types."""

import enum
import logging
from dataclasses import dataclass
from typing import Dict

logger = logging.getLogger(__name__)


@dataclass
class DataTypeSpec:
    """Specification of type from the file 'types.xml'."""
    id: int
    base_type_name: str
    name: str

    # FIXED_DICT data
    module_name: str = None
    pairs: Dict[str, 'IKBEType'] = None

    # ARRAY data
    of: 'IKBEType' = None

    @property
    def is_alias(self):
        return self.name != self.base_type_name

    @property
    def is_fixed_dict(self):
        return self.pairs is not None

    @property
    def is_array(self):
        return self.of is not None

    @property
    def type_name(self):
        if not self.name or self.name.startswith('_'):
            # It's an inner defined type
            return f'{self.base_type_name}_{self.id}'
        return self.name


