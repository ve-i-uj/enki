"""This module contains classes working with communication messages."""

import logging

from typing import Tuple, Any, List

from enki import dcdescr

from . import interface

logger = logging.getLogger(__name__)


class Message(interface.IMessage):

    def __init__(self, spec: dcdescr.MessageDescr, fields: tuple):
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

    @property
    def args_type(self):
        return self._spec.args_type

    def get_field_map(self):
        return ((value, kbe_type) for value, kbe_type
                in zip(self._fields, self._spec.field_types))

    def get_values(self) -> List[Any]:
        return [value for value in self._fields]

    def __str__(self):
        return f'{self.__class__.__name__}(id={self.id}, name={self.name})'
