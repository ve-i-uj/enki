"""Classes to serialize / deserialize a message object.

KBEngine is using the message type to comminicate between its components.
The module contains the class to serialize / deserialize a message object
(from bytes).
"""

import io
import logging
from typing import Tuple, Optional
from enki.net.kbeclient import kbetype

from enki import kbeenum

from enki.net import msgspec

from .message import Message, MsgDescr

logger = logging.getLogger(__name__)


class MessageSerializer:
    """Serialize / deserialize a kbe network packet."""

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

        msg_spec: MsgDescr = self._msg_spec_by_id[msg_id]
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

    def serialize(self, msg: Message) -> bytes:
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
        # Write to the start of the buffer the message id and the data length
        payload.write(kbetype.MESSAGE_ID.encode(msg.id))
        if msg.need_calc_length:
            payload.write(kbetype.MESSAGE_LENGTH.encode(written))

        payload.write(io_obj.getbuffer())
        return payload.getbuffer().tobytes()