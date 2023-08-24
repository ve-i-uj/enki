"""This module contains classes working with communication messages."""

from __future__ import annotations
import dataclasses

import io
import logging
from dataclasses import dataclass
from typing import Any, Tuple, Iterator, List, Optional

from . import kbeenum
from .kbeenum import MsgArgsType, ComponentType

from . import kbetype
from .kbetype import IKBEType

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MsgDescr:
    """Specification of a message (see messages_fixed_defaults.xml)"""
    id: int
    lenght: int
    name: str
    args_type: MsgArgsType
    field_types: tuple[IKBEType, ...]
    desc: str

    @property
    def short_name(self):
        return self.name.split('::')[1]

    @property
    def component_type(self) -> ComponentType:
        comp_name =  self.name.split('::')[0]
        return getattr(ComponentType, comp_name.upper())

    @property
    def need_calc_length(self) -> bool:
        return self.lenght == -1

    def change_component_owner(self, comp_type: ComponentType, id: int | None = None) -> MsgDescr:
        """Изменить владельца-компонента этого сообщения.

        Кроме фиксированных сообщений для каждого компонента в Enki вводятся
        ещё пользовательские сообщения, чтобы, например, описать формат ответа
        от компонента. У такого сообщения могут быть разные компоненты-владельцы,
        но одинаковая сигнатура. Данный метод вводиться, чтобы можно было
        динамически менять владельца в зависимости от того, чей ждём ответ.
        """
        _comp_name, msg_name =  self.name.split('::')
        new_comp_name = comp_type.name.capitalize()
        dct = dataclasses.asdict(self)
        dct['name'] = f'{new_comp_name}::{msg_name}'
        if id is not None:
            dct['id'] = id
        return MsgDescr(**dct)


class Message:

    def __init__(self, spec: MsgDescr, fields: tuple):
        assert len(spec.field_types) == len(fields)
        self._spec = spec
        self._fields = fields

    @property
    def id(self):
        """Message id (see messages_fixed_defaults.xml)."""
        return self._spec.id

    @property
    def spec(self):
        return self._spec

    @property
    def need_calc_length(self) -> bool:
        return self._spec.need_calc_length

    @property
    def name(self):
        """Message name (see messages_fixed_defaults.xml)."""
        return self._spec.name

    @property
    def args_type(self) -> MsgArgsType:
        return self._spec.args_type

    def get_field_map(self):
        """Return map of field values to its KBE type"""
        return ((value, kbe_type) for value, kbe_type
                in zip(self._fields, self._spec.field_types))

    def get_values(self) -> List[Any]:
        """Return values of message fields."""
        return [value for value in self._fields]

    def __str__(self):
        return f'{self.__class__.__name__}(id={self.id}, name={self.name})'

    __repr__ = __str__


class MessageSerializer:
    """Serialize / deserialize a kbe network packet.

    KBEngine is using the message type to comminicate between its components.
    This class serializes / deserializes a message object (from bytes).
    """

    def __init__(self, msg_spec_by_id: dict[int, MsgDescr]) -> None:
        self._msg_spec_by_id = msg_spec_by_id

    def deserialize(self, data: memoryview
                    ) -> Tuple[Optional[Message], memoryview]:
        """Deserialize a kbe network packet to a message.

        The second element of the returned tuple is a tail of data,
        not handled data. It's beginning of the other message.
        """
        origin_data: memoryview = data[:]
        msg_id, offset = kbetype.MESSAGE_ID.decode(data)
        data = data[offset:]

        if msg_id not in self._msg_spec_by_id:
            logger.warning(f'[{self}] There is no specification for the message "{msg_id}"')
            return None, origin_data

        msg_spec = self._msg_spec_by_id[msg_id]
        if msg_spec.args_type == kbeenum.MsgArgsType.FIXED \
                and not msg_spec.field_types:
            # This is a short message. Only message id, there is no payload.
            return Message(spec=msg_spec, fields=tuple()), data

        if not msg_spec.need_calc_length:
            fields = []
            for kbe_type in msg_spec.field_types:
                value, size = kbe_type.decode(data)
                fields.append(value)
                data = data[size:]

            return Message(spec=msg_spec, fields=tuple(fields)), data

        msg_length, offset = kbetype.MESSAGE_LENGTH.decode(data)
        data = data[offset:]

        if len(data) < msg_length:
            # It's a part of the message
            return None, origin_data

        tail = memoryview(b'')
        if len(data) > msg_length:
            # There are two messages in data
            tail = data[msg_length:]
            data = data[:msg_length]

        fields = []
        for kbe_type in msg_spec.field_types:
            value, size = kbe_type.decode(data)
            fields.append(value)
            data = data[size:]

        return Message(spec=msg_spec, fields=tuple(fields)), tail

    def serialize(self, msg: Message, only_data: bool = False) -> bytes:
        """Serialize a message to a kbe network packet."""
        if msg.args_type == kbeenum.MsgArgsType.FIXED and not msg.get_values():
            io_obj = io.BytesIO()
            io_obj.write(kbetype.MESSAGE_ID.encode(msg.id))
            return io_obj.getbuffer().tobytes()

        io_obj = io.BytesIO()
        # Write message arguments
        written = 0
        for value, kbe_type in msg.get_field_map():
            written += io_obj.write(kbe_type.encode(value))

        payload = io.BytesIO()
        # Иногда нужно отправлять только данные, без префикса с номером и длиной
        if not only_data:
            # Write to the start of the buffer the message id and the data length
            payload.write(kbetype.MESSAGE_ID.encode(msg.id))
            if msg.need_calc_length:
                payload.write(kbetype.MESSAGE_LENGTH.encode(written))

        payload.write(io_obj.getbuffer())
        return payload.getbuffer().tobytes()

    def deserialize_only_data(self, data: bytes, spec: MsgDescr
                              ) -> Tuple[Optional[Message], memoryview]:
        """Декодировать сообщение без оболочки."""
        return self.deserialize(memoryview(
            kbetype.MESSAGE_ID.encode(spec.id) \
            + (kbetype.MESSAGE_LENGTH.encode(len(data)) if spec.need_calc_length else b'') \
            + data
        ))
