"""This module contains classes working with communication messages."""

import abc

from dataclasses import dataclass
from typing import Tuple, Any, Iterator

from enki import kbetype


class IMessage(abc.ABC):
    
    @abc.abstractproperty
    def id(self):
        """Message id."""
        pass

    @abc.abstractmethod
    def field_map(self) -> Iterator[Tuple[Any, kbetype.IKBEType]]:
        """Return map value to its KBE type"""
        pass


class IMessageRouter(abc.ABC):

    @abc.abstractmethod
    def on_receive_message(self, msg: IMessage):
        pass


@dataclass(frozen=True)
class MessageSpec:
    """Specification of a message (see messages_fixed_defaults.xml)"""
    id: int
    name: str
    field_types: Tuple[kbetype.IKBEType]
    desc: str
    

class Message(IMessage):
    
    def __init__(self, spec: MessageSpec, fields: Tuple[Any]):
        assert len(spec.field_types) == len(fields)
        # TODO: (1 дек. 2020 г. 21:26:47 burov_alexey@mail.ru)
        # Плюс проверка типа, что верные типы подставляются
        self._spec = spec
        self._fields = fields

    @property
    def id(self):
        return self._spec.id

    def field_map(self):
        return ((value, kbe_type) for value, kbe_type 
                in zip(self._fields, self._spec.field_types))


class MessageRouter(IMessageRouter):

    def on_receive_message(self, msg: Message):
        pass
