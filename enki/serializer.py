"""Classes to serialize / deserialize communication data."""

import abc
import logging
import struct

from enki import message
from enki import msgspec

logger = logging.getLogger(__name__)


class ISerializer(abc.ABC):
    """Serialize / deserialize a kbe network packet."""

    @abc.abstractmethod
    def deserialize(self, data: bytes) -> message.Message:
        """Deserialize a kbe netwokr packet to a message."""
        pass

    @abc.abstractmethod
    def serialize(self, message: message.Message) -> bytes:
        """Serialize a message to a kbe network packet."""
        pass


class Serializer(ISerializer):
    
    _PACK_INFO_FMT = '=HH'  # msg_id, msg_lenght

    def deserialize(self, data: bytes) -> message.Message:
        # TODO: (1 дек. 2020 г. 22:30:44 burov_alexey@mail.ru)
        # По длине сообщения нужно делать проверку, что не было вычитано что-то
        # не так
        msg_id, msg_lenght = struct.unpack(self._PACK_INFO_FMT, data[:4])
        msg_spec = msgspec.app.client.MSG_MAP[msg_id]
        # TODO: (1 дек. 2020 г. 22:06:43 burov_alexey@mail.ru)
        # Использовать memoryview
        data = data[4:]
        fields = []
        for kbe_type in msg_spec.field_types:
            # TODO: (1 дек. 2020 г. 22:17:21 burov_alexey@mail.ru)
            # Из-за строк скорее нужно возвращать кол-во обработанных байтов,
            # (для кого-то это будет просто размер типа)
            value = kbe_type.decode(data)
            fields.append(value)
            data = data[kbe_type.size:]
        
        return message.Message(
            spec=msg_spec,
            fields=tuple(fields)
        )

    def serialize(self, msg: message.Message) -> bytes:
        data = b''.join(kbe_type.encode(value) for value, kbe_type in msg.field_map())
        res = self._build_packet(msg.id, data)
        return res
            
    def _build_packet(self, msg_id: int, data: bytes) -> bytes:
        packet_info = struct.pack(self._PACK_INFO_FMT, msg_id, len(data))
        return packet_info + data