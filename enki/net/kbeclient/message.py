"""This module contains classes working with communication messages.

* No dependences *
"""

import abc
import logging
from dataclasses import dataclass
from typing import Any, Tuple, Iterator, List

from enki.kbeenum import MsgArgsType

from .kbetype import IKBEType

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MsgDescr:
    """Specification of a message (see messages_fixed_defaults.xml)"""
    @property
    def id(self) -> int:
        return None

    @property
    def lenght(self) -> int:
        return None

    @property
    def name(self) -> str:
        return None

    @property
    def args_type(self) -> MsgArgsType:
        return None

    @property
    def field_types(self) -> tuple[IKBEType, ...]:
        return None

    @property
    def desc(self) -> str:
        return None


    @property
    def short_name(self):
        return self.name.split('::')[1]

    @property
    def need_calc_length(self) -> bool:
        return self.lenght == -1


class IMessage(abc.ABC):
    """Wrapper around client-server communication data."""

    @property
    @abc.abstractmethod
    def id(self) -> int:
        """Message id (see messages_fixed_defaults.xml)."""
        pass

    @property
    @abc.abstractmethod
    def need_calc_length(self) -> bool:
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Message name (see messages_fixed_defaults.xml)."""
        pass

    @property
    @abc.abstractmethod
    def args_type(self) -> MsgArgsType:
        pass

    @abc.abstractmethod
    def get_field_map(self) -> Iterator[Tuple[Any, IKBEType]]:
        """Return map of field values to its KBE type"""
        pass

    @abc.abstractmethod
    def get_values(self) -> List[Any]:
        """Return values of message fields."""
        pass


class Message(IMessage):

    def __init__(self, spec: MsgDescr, fields: tuple):
        assert len(spec.field_types) == len(fields)
        # TODO: (1 дек. 2020 г. 21:26:47 burov_alexey@mail.ru)
        # Плюс проверка типа, что верные типы подставляются
        self._spec = spec
        self._fields = fields

    @property
    def id(self):
        return self._spec.id

    @property
    def need_calc_length(self) -> bool:
        return self._spec.need_calc_length

    @property
    def name(self):
        return self._spec.name

    @property
    def args_type(self) -> MsgArgsType:
        return self._spec.args_type

    def get_field_map(self):
        return ((value, kbe_type) for value, kbe_type
                in zip(self._fields, self._spec.field_types))

    def get_values(self) -> List[Any]:
        return [value for value in self._fields]

    def __str__(self):
        return f'{self.__class__.__name__}(id={self.id}, name={self.name})'

    __repr__ = __str__


class IMsgReceiver(abc.ABC):
    """Message receiver interface."""

    @abc.abstractmethod
    def on_receive_msg(self, msg: Message) -> bool:
        """Call on receive message.

        Returns message's handled or not.
        """
        pass

    @abc.abstractmethod
    def on_end_receive_msg(self):
        pass
