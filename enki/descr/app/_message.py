"""This module contains classes working with communication messages."""

import enum
import logging

from dataclasses import dataclass
from typing import Tuple, Any, List

from enki import interface

logger = logging.getLogger(__name__)


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
    field_types: Tuple[interface.IKBEType]
    desc: str

    @property
    def short_name(self):
        return self.name.split('::')[1]
