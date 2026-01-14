"""Test Client::onEntityEnterWorld."""

from enki.msg_parser.client_msg_parser.entity_msg_parser import (
    OnEntityEnterWorldMsgParserEntityTypeIsUINT8,
    OnEntityEnterWorldMsgParserEntityTypeIsUINT16,
)

from enki import msgspec
from enki.msg.msg_serializer import MessageSerializer


class TestOnEntityEnterWorld:
    """Test Client::onEntityEnterWorld."""

    def test_on_enter_entity_type_is_uint8(self):
        """Проверка, когда тип сущности - это UINT8."""
        data = b"\xfb\x01\x06\x00\x81\x08\x00\x00\x02\x00\xff\x01\n\x00\xcb\x00\x00\x00\x00\x05d\x00\x00\x00\xff\x01\n\x00\xcb\x00\x00\x00\x00\x07d\x00\x00\x00"
        serializer = MessageSerializer(msgspec.ClientappMsgSpecByID)
        msg, _ = serializer.deserialize(memoryview(data))
        assert msg is not None, "Invalid initial data"

        res = OnEntityEnterWorldMsgParserEntityTypeIsUINT8().parse(msg)

        assert res.success is True
        assert res.result is not None

        assert res.result.entity_id == 2177
        assert res.result.entity_type_id == 2
        assert res.result.is_on_ground is not True

    def test_on_enter_entity_type_is_uint16(self):
        """Проверка, когда тип сущности - это UINT16."""
        data = b"\xfb\x01\x06\x00\x81\x08\x00\x00\x02\x00\x00\xff\x01\n\x00\xcb\x00\x00\x00\x00\x05d\x00\x00\x00\xff\x01\n\x00\xcb\x00\x00\x00\x00\x07d\x00\x00\x00"
        serializer = MessageSerializer(msgspec.ClientappMsgSpecByID)
        msg, _ = serializer.deserialize(memoryview(data))
        assert msg is not None, "Invalid initial data"

        res = OnEntityEnterWorldMsgParserEntityTypeIsUINT16().parse(msg)

        assert res.success is True
        assert res.result is not None

        assert res.result.entity_id == 2177
        assert res.result.entity_type_id == 2
        assert res.result.is_on_ground is not True
