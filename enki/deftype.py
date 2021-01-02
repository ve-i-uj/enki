"""Assets' types."""

import logging

from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DataTypeSpec:
    """Specification of type from the file 'types.xml'."""
    id: int
    base_type_name: str
    name: str
