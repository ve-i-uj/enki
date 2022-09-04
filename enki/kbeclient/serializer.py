"""Classes to serialize / deserialize communication data."""

import io
import logging
from typing import Tuple, Optional

from enki import descr, kbetype, dcdescr
from enki.kbeclient import message

logger = logging.getLogger(__name__)


class Serializer:
    """Serialize / deserialize a kbe network packet."""

    def deserialize(self, data: memoryview
                    ) -> Tuple[Optional[message.Message], memoryview]:
        """Deserialize a kbe network packet to a message.

        The second element of the returned tuple is a tail of data,
        not handled data. It's beginning of the other message.
        """
        origin_data: memoryview = data[:]
        msg_id, offset = kbetype.MESSAGE_ID.decode(data)
        data = data[offset:]

        msg_spec: dcdescr.MessageDescr = descr.app.client.SPEC_BY_ID[msg_id]
        if msg_spec.args_type == dcdescr.MsgArgsType.FIXED \
                and not msg_spec.field_types:
            # This is a short message. Only message id, there is no payload.
            return message.Message(spec=msg_spec, fields=tuple()), data

        if not msg_spec.need_calc_length:
            fields = []
            for kbe_type in msg_spec.field_types:
                value, size = kbe_type.decode(data)
                fields.append(value)
                data = data[size:]

            return message.Message(spec=msg_spec, fields=tuple(fields)), data

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

        return message.Message(spec=msg_spec, fields=tuple(fields)), tail

    def serialize(self, msg: message.Message) -> bytes:
        """Serialize a message to a kbe network packet."""
        if msg.args_type == dcdescr.MsgArgsType.FIXED and not msg.get_values():
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
