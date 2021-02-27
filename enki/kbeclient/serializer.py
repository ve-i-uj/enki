"""Classes to serialize / deserialize communication data."""

import abc
import logging
import struct

from enki import message

logger = logging.getLogger(__name__)

# TODO: [27.02.2021 8:36 burov_alexey@mail.ru]
# Тут нужно или нужно давать возможность выставлять разные сериализаторы
# клиенту, или удалять интерфейс. Т.к. сейчас сериализатор создаётся в
# клиенте и интерфейс сериализатора не нужен
class ISerializer(abc.ABC):
    """Serialize / deserialize a kbe network packet."""

    @abc.abstractmethod
    def deserialize(self, data: memoryview) -> message.Message:
        """Deserialize a kbe network packet to a message."""
        pass

    @abc.abstractmethod
    def serialize(self, message: message.Message) -> bytes:
        """Serialize a message to a kbe network packet."""
        pass


class Serializer(ISerializer):
    
    _PACK_INFO_FMT = '=HH'  # msg_id, msg_lenght
    _PACK_SHORT_INFO_FMT = '=H'  # msg_id

    def deserialize(self, data: memoryview) -> message.Message:
        # TODO: (1 дек. 2020 г. 22:30:44 burov_alexey@mail.ru)
        # По длине сообщения нужно делать проверку, что не было вычитано что-то
        # не так
        msg_id, msg_length = struct.unpack(self._PACK_INFO_FMT, data[:4])
        data = data[4:]
        if len(data) != msg_length:
            # It's a part of the message
            return None
        msg_spec = message.app.client.SPEC_BY_ID[msg_id]
        # TODO: (1 дек. 2020 г. 22:06:43 burov_alexey@mail.ru)
        # Использовать memoryview
        fields = []
        for kbe_type in msg_spec.field_types:
            # TODO: (1 дек. 2020 г. 22:17:21 burov_alexey@mail.ru)
            # Из-за строк скорее нужно возвращать кол-во обработанных байтов,
            # (для кого-то это будет просто размер типа)
            value, size = kbe_type.decode(data)
            fields.append(value)
            data = data[size:]
        
        return message.Message(
            spec=msg_spec,
            fields=tuple(fields)
        )

    def serialize(self, msg: message.Message) -> bytes:
        data = b''.join(kbe_type.encode(value) for value, kbe_type in msg.get_field_map())
        res = self._build_packet(msg.id, data)
        return res
            
    def _build_packet(self, msg_id: int, data: bytes) -> bytes:
        if not data:
            packet_info = struct.pack(self._PACK_SHORT_INFO_FMT, msg_id)
        else:
            packet_info = struct.pack(self._PACK_INFO_FMT, msg_id, len(data))
        return packet_info + data
