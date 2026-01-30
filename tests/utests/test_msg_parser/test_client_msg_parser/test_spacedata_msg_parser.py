"""Тесты парсера сообщений SpaceData (глобальное состояние space)."""

from enki import msgspec
from enki.msg.msg_serializer import MessageSerializer
from enki.msg_parser.client_msg_parser.spacedata_msg_parser import (
    DelSpaceDataParser,
    InitSpaceDataParser,
    SetSpaceDataParser,
)


class TestInitSpaceData:
    """Test Client::initSpaceData."""

    msg_spec = msgspec.client.initSpaceData

    def test_ok(self):
        """Test Client::initSpaceData."""
        data = b"A\x00\x1f\x00\x01\x00\x00\x00_mapping\x00spaces/xinshoucun\x00"
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(data))
        assert msg is not None, "Invalid initial data"

        res = InitSpaceDataParser().parse(msg)
        assert res.success
        assert res.result.space_id == 1
        assert res.result.pairs == {"_mapping": "spaces/xinshoucun"}

        # Проверка нейминга, чтобы не было опечаток и т.п.
        assert (
            res.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            res.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )
        assert res.msg_id == self.msg_spec.id


class TestSetSpaceData:
    """Test Client::setSpaceData."""

    msg_spec = msgspec.client.setSpaceData

    def test_setSpaceData(self):
        """Test Client::setSpaceData."""
        # Данные не живые, а собранные из сообщения
        data = b"B\x00\x18\x00\x01\x00\x00\x00_mapping\x00spaces/123\x00"
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, _ = serializer.deserialize(memoryview(data))
        assert msg is not None, "Invalid initial data"

        res = SetSpaceDataParser().parse(msg)
        assert res.success
        assert res.result.space_id == 1
        assert res.result.key == "_mapping"
        assert res.result.value == "spaces/123"

        # Проверка нейминга, чтобы не было опечаток и т.п.
        assert (
            res.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            res.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )
        assert res.msg_id == self.msg_spec.id


class TestDelSpaceData:
    """Test Client::delSpaceData."""

    msg_spec = msgspec.client.delSpaceData

    def test_delSpaceData(self):
        """Test Client::delSpaceData."""
        # Данные не живые, а собранные из сообщения
        data = b"C\x00\r\x00\x01\x00\x00\x00_mapping\x00"
        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)
        msg, _ = serializer.deserialize(memoryview(data))
        assert msg is not None, "Invalid initial data"

        res = DelSpaceDataParser().parse(msg)
        assert res.success
        assert res.result.space_id == 1
        assert res.result.key == "_mapping"

        # Проверка нейминга, чтобы не было опечаток и т.п.
        assert (
            res.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            res.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )
        assert res.msg_id == self.msg_spec.id
