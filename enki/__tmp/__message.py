"""This module contains classes working with communication messages."""

from __future__ import annotations

import io
import logging
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, TypeAlias

from ..kbeenum import ComponentType
from .kbetype import IKBETypeDecoder

logger = logging.getLogger(__name__)

MsgId: TypeAlias = int


class MsgArgsType(IntEnum):
    """Fixed or variable length of message (see MESSAGE_ARGS_TYPE)."""

    VARIABLE = -1
    FIXED = 0


@dataclass(frozen=True)
class MsgDescr:
    """Specification of a message (see messages_fixed_defaults.xml)."""

    id: MsgId
    lenght: int
    name: str
    args_type: MsgArgsType
    field_types: tuple[IKBETypeDecoder, ...]
    desc: str

    @property
    def short_name(self) -> str:
        """Имя сообщения без имени компонента."""
        return self.name.split("::")[1]

    @property
    def component_type(self) -> ComponentType:
        """Компонент, которому пренадлежит сообщение."""
        comp_name = self.name.split("::")[0]
        return getattr(ComponentType, comp_name.upper())

    @property
    def is_length_calculation_needed(self) -> bool:
        """Нужно ли считывать длину сообщения."""
        return self.lenght == -1


MsgSpecById: TypeAlias = dict[MsgId, MsgDescr]


class Message:
    """Сообщение KBEngine для общения с другим компонентом."""

    def __init__(self, spec: MsgDescr, fields: tuple[Any, ...]) -> None:
        """Конструктор.

        Args:
            spec (MsgDescr): описание сообщения
            fields (tuple[Any]): значения полей

        """
        assert len(spec.field_types) == len(fields)
        self._spec = spec
        self._fields = fields

    @property
    def id(self) -> MsgId:
        """Message id (see messages_fixed_defaults.xml)."""
        return self._spec.id

    @property
    def component(self) -> ComponentType:
        """Тип компонента этого сообщения."""
        return self._spec.component_type

    @property
    def name(self) -> str:
        """Message name (see messages_fixed_defaults.xml)."""
        return self._spec.name

    def get_values(self) -> list[Any]:
        """Return values of message fields.

        Returns:
            list[Any]: значения полей сообщения

        """
        return list(self._fields)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"

    __repr__ = __str__


class MessageEncoder:
    """Serialize / deserialize a kbe network packet.

    KBEngine is using the message type to comminicate between its components.
    This class serializes / deserializes a message object (from bytes).
    """

    def __init__(self, msg_spec_by_id: MsgSpecById) -> None:
        self._msg_spec_by_id = msg_spec_by_id

    def deserialize(self, data: memoryview) -> tuple[Message | None, memoryview]:
        """Deserialize a kbe network packet to a message.

        The second element of the returned tuple is a tail of data,
        not handled data. It's beginning of the other message.
        """
        origin_data: memoryview = data[:]
        msg_id, offset = kbetype.MESSAGE_ID.decode(data)
        data = data[offset:]

        if msg_id not in self._msg_spec_by_id:
            logger.warning(
                '[%s] There is no specification for the message "%s"', self, msg_id
            )
            return None, origin_data

        msg_spec = self._msg_spec_by_id[msg_id]
        if (
            msg_spec.args_type == MsgArgsType.FIXED
            and not msg_spec.field_types
        ):
            # This is a short message. Only message id, there is no payload.
            return Message(spec=msg_spec, fields=tuple()), data

        if not msg_spec.is_length_calculation_needed:
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

        tail = memoryview(b"")
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
        msg_spec = self._msg_spec_by_id[msg.id]

        if msg_spec.args_type == MsgArgsType.FIXED and not msg.get_values():
            io_obj = io.BytesIO()
            io_obj.write(kbetype.MESSAGE_ID.encode(msg.id))
            return io_obj.getbuffer().tobytes()

        io_obj = io.BytesIO()
        # Write message arguments
        written = 0
        for value, kbe_type in zip(msg.get_values(), msg_spec.field_types):
            written += io_obj.write(kbe_type.encode(value))

        payload = io.BytesIO()
        # Иногда нужно отправлять только данные, без префикса с номером и длиной
        if not only_data:
            # Write to the start of the buffer the message id and the data length
            payload.write(kbetype.MESSAGE_ID.encode(msg.id))
            if msg.is_length_calculation_needed:
                payload.write(kbetype.MESSAGE_LENGTH.encode(written))

        payload.write(io_obj.getbuffer())
        return payload.getbuffer().tobytes()

    def deserialize_only_data(
        self, data: bytes, spec: MsgDescr
    ) -> Tuple[Optional[Message], memoryview]:
        """Декодировать сообщение без оболочки."""
        return self.deserialize(
            memoryview(
                kbetype.MESSAGE_ID.encode(spec.id)
                + (
                    kbetype.MESSAGE_LENGTH.encode(len(data))
                    if spec.is_length_calculation_needed
                    else b""
                )
                + data
            )
        )

    def __str__(self) -> str:
        for_component = list(self._msg_spec_by_id.values())[0].component_type.name
        return f"MessageSerializer(for_component={for_component})"

    __repr__ = __str__
