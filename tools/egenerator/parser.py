"""Парсеры данных KBEngine."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from enki.kbeenum import DistributionFlag
from enki.kbetype.decoders.basic_data_type_decoders import (
    BLOB,
    INT16,
    INT8,
    STRING,
    UINT16,
    UINT8,
)


if TYPE_CHECKING:
    from collections import OrderedDict

logger = logging.getLogger(__name__)



    def __str__(self):
        return str(self.__class__.__name__)
