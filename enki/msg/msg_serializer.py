"""Сериализатор и десериализатор объекта KBEngine-сообщения."""

from __future__ import annotations

import logging
from io import BytesIO
from typing import TYPE_CHECKING, TypeAlias

from enki.kbetype.decoders.basic_data_type_decoders import UINT16
from enki.kbetype.pytypes.basic_data_types import KBEUInt16

from .message import Message

if TYPE_CHECKING:
    from .msg_descr import ComponentMsgSpecById, MsgId

logger = logging.getLogger(__name__)


# Алиасы на декодеры типов для читаемости
_MESSAGE_LENGTH: TypeAlias = UINT16  # pylint: disable=invalid-name
_MESSAGE_ID: TypeAlias = UINT16  # pylint: disable=invalid-name


class MessageSerializer:
    """Сериализатор и десериализатор объекта KBEngine-сообщения.

    KBEngine is using the message type to comminicate between its components.
    """

    def __init__(self, comp_msg_spec_by_id: ComponentMsgSpecById) -> None:
        """Конструктор.

        Args:
            comp_msg_spec_by_id (ComponentMsgSpecById): словарь с описаниями
                сообщений компонента.

        """
        self._msg_spec_by_id = comp_msg_spec_by_id.msg_spec_by_id
        self._component = comp_msg_spec_by_id.component

    def deserialize(
        self, data: memoryview
    ) -> tuple[Message | None, memoryview]:
        """Deserialize a kbe network data to a message.

        The second element of the returned tuple is a tail of data,
        not handled data. It's beginning of the other message.

        Args:
            data (memoryview): serialized message

        Returns:
            tuple[Message | None, memoryview]: The deserialized message and
                data tail. If the message cannot be parsed it will be None. The
                data tail is the origin data in this case.

        """
        origin_data: memoryview = data[:]
        msg_id, offset = _MESSAGE_ID.decode(data)
        data = data[offset:]

        if msg_id not in self._msg_spec_by_id:
            logger.warning(
                '[%s] There is no specification for the message "%s"',
                self,
                msg_id,
            )
            return None, origin_data

        msg_spec = self._msg_spec_by_id[msg_id]
        if msg_spec.is_a_short_message:
            # This is a short message. Only message id, there is no payload.
            return (
                Message(msg_id, msg_spec.name, self._component, values=()),
                data,
            )

        if not msg_spec.is_length_calculation_needed:
            values = []
            for kbe_type in msg_spec.args:
                try:
                    value, offset = kbe_type.decode(data)
                except ValueError as err:
                    logger.debug(
                        "[%s] The data cannot be decoded (err = '%s')",
                        self,
                        err,
                    )
                    return None, origin_data

                values.append(value)
                data = data[offset:]

            return (
                Message(
                    msg_id, msg_spec.name, self._component, values=tuple(values)
                ),
                data,
            )

        msg_length, offset = _MESSAGE_LENGTH.decode(data)
        data = data[offset:]

        if len(data) < msg_length:
            logger.debug(
                "[%s] The data length is smaller then the message length", self
            )
            # It's a part of the message
            return None, origin_data

        tail = memoryview(b"")
        if len(data) > msg_length:
            # There are two messages in the packet? Первую часть парсим, по
            # поводу второй части решение принимает вызывающий слой.
            tail = data[msg_length:]
            data = data[:msg_length]
            logger.debug("[%s] There is a data tail (%s)", self, tail.tobytes())

        values = []
        for kbe_type in msg_spec.args:
            try:
                value, offset = kbe_type.decode(data)
            except ValueError as err:
                # Пришло кривое значение, под тип не подходит
                logger.debug(
                    '[%s] The data cannot be decoded (err = "%s")', self, err
                )
                return None, origin_data

            values.append(value)
            data = data[offset:]

        return (
            Message(
                msg_id, msg_spec.name, self._component, values=tuple(values)
            ),
            tail,
        )

    def serialize(self, msg: Message, *, only_data: bool = False) -> bytes:
        """Serialize the message to the network data.

        Args:
            msg (Message): the message to deserialize
            only_data (bool, optional): _description_. Defaults to False.

        Returns:
            bytes: the network prezentation of the message

        """
        msg_spec = self._msg_spec_by_id[msg.id]
        if msg_spec.is_a_short_message:
            io_obj = BytesIO()
            io_obj.write(_MESSAGE_ID.encode(KBEUInt16(msg.id)))
            return io_obj.getbuffer().tobytes()

        args_io_obj = BytesIO()
        # Write message arguments
        written = 0
        for value, kbe_type in zip(msg.get_values(), msg_spec.args):
            written += args_io_obj.write(kbe_type.encode(value))  # type: ignore

        # Иногда нужно отправлять только данные, без префикса с номером
        # сообщения и его длиной
        if only_data:
            return args_io_obj.getbuffer().tobytes()

        payload = BytesIO()
        # Write to the start of the buffer the message id and the data length
        payload.write(_MESSAGE_ID.encode(KBEUInt16(msg.id)))
        if msg_spec.is_length_calculation_needed:
            payload.write(_MESSAGE_LENGTH.encode(KBEUInt16(written)))

        payload.write(args_io_obj.getbuffer())
        return payload.getbuffer().tobytes()

    def deserialize_only_data(
        self, data: bytes, msg_id: MsgId
    ) -> tuple[Message | None, memoryview]:
        """Декодировать сообщение без оболочки.

        Args:
            data (bytes): данные для десериализации сообщения
            msg_id (MsgId): описание сообщения

        Returns:
            tuple[Message | None, memoryview]: сообщение и оставшиеся данные.
                If the message cannot be parsed it will be None.

        """
        msg_spec = self._msg_spec_by_id[msg_id]
        return self.deserialize(
            memoryview(
                _MESSAGE_ID.encode(KBEUInt16(msg_spec.id))
                + (
                    _MESSAGE_LENGTH.encode(KBEUInt16(len(data)))
                    if msg_spec.is_length_calculation_needed
                    else b""
                )
                + data
            )
        )

    def __str__(self) -> str:
        return f"MessageSerializer(for_component={self._component.name})"

    __repr__ = __str__
