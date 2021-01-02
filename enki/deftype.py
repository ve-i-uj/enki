"""Assets' types."""

import enum
import logging

from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DataTypeSpec:
    """Specification of type from the file 'types.xml'."""
    id: int
    base_type_name: str
    name: str


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
