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
class MessageSpec:
    """Specification of a message (see messages_fixed_defaults.xml)"""
    id: int
    name: str
    args_type: MsgArgsType
    field_types: Tuple[interface.IKBEType]
    desc: str

    @property
    def short_name(self):
        return self.name.split('::')[1]


class Message(interface.IMessage):

    def __init__(self, spec: MessageSpec, fields: Tuple):
        assert len(spec.field_types) == len(fields)
        # TODO: (1 дек. 2020 г. 21:26:47 burov_alexey@mail.ru)
        # Плюс проверка типа, что верные типы подставляются
        self._spec = spec
        self._fields = fields

    @property
    def id(self):
        return self._spec.id

    @property
    def name(self):
        return self._spec.name

    def get_field_map(self):
        return ((value, kbe_type) for value, kbe_type
                in zip(self._fields, self._spec.field_types))

    def get_values(self) -> List[Any]:
        return [value for value in self._fields]

    def __str__(self):
        return f'{self.__class__.__name__}(id={self.id}, name={self.name})'
