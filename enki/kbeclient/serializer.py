"""Classes to serialize / deserialize communication data."""

import logging
import struct
from typing import Tuple, Optional

from enki import descr
from enki.kbeclient import message

logger = logging.getLogger(__name__)


class Serializer:
    """Serialize / deserialize a kbe network packet."""
    
    _PACK_INFO_FMT = '=HH'  # msg_id, msg_length
    _PACK_SHORT_INFO_FMT = '=H'  # msg_id

    def deserialize(self, data: memoryview
                    ) -> Tuple[Optional[message.Message], memoryview]:
        """Deserialize a kbe network packet to a message.

        The second element of the returned tuple is a tail of data,
        not handled data. It's beginning of the other message.
        """
        msg_id, msg_length = struct.unpack(self._PACK_INFO_FMT, data[:4])

        if len(data[4:]) < msg_length:
            # It's a part of the message
            return None, data

        tail = None
        data = data[4:]
        if len(data) > msg_length:
            # There are two messages in data
            tail = data[msg_length:]
            data = data[:msg_length]

        msg_spec = descr.app.client.SPEC_BY_ID[msg_id]
        fields = []
        for kbe_type in msg_spec.field_types:
            value, size = kbe_type.decode(data)
            fields.append(value)
            data = data[size:]
        
        return message.Message(spec=msg_spec, fields=tuple(fields)), tail

    def serialize(self, msg: message.Message) -> bytes:
        """Serialize a message to a kbe network packet."""
        data = b''.join(kbe_type.encode(value) for value, kbe_type in msg.get_field_map())
        res = self._build_packet(msg.id, data)
        return res
            
    def _build_packet(self, msg_id: int, data: bytes) -> bytes:
        if not data:
            packet_info = struct.pack(self._PACK_SHORT_INFO_FMT, msg_id)
        else:
            packet_info = struct.pack(self._PACK_INFO_FMT, msg_id, len(data))
        return packet_info + data
