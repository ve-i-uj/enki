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
