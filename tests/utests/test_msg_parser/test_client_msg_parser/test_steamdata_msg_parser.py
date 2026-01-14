"""Тесты сообщений Client::onStreamData* ."""

from enki import msgspec
from enki.msg.msg_serializer import MessageSerializer
from enki.msg_parser.client_msg_parser.steamdata_msg_parser import (
    OnStreamDataCompletedMsgParser,
    OnStreamDataRecvMsgParser,
    OnStreamDataStartedMsgParser,
    StreamTypeEnum,
)


class TestOnStreamDataStarted:
    """Test Client::onStreamDataStarted."""

    msg_spec = msgspec.client.onStreamDataStarted
    data = b"\x02\x02\x15\x00\x01\x00\x0e\x00\x00\x00unittest.data\x00\x01"

    async def test_onStreamDataStarted(self):
        """Тест на удачный парсинг данных сообщения Client::onStreamDataStarted."""
        serializer = MessageSerializer(msgspec.ClientappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = OnStreamDataStartedMsgParser().parse(msg)
        assert res.success is True
        assert res.result is not None
        assert res.msg_id == msgspec.client.onStreamDataStarted.id

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

        pd = res.result

        assert pd.stream_id == 1
        assert pd.stream_size == 14
        assert pd.stream_descr == "unittest.data"
        assert pd.stream_download_type == StreamTypeEnum.FILE


class TestOnStreamDataRecv:
    """Test Client::onStreamDataRecv."""

    msg_spec = msgspec.client.onStreamDataRecv
    data = b"\x03\x02\x14\x00\x01\x00\x0e\x00\x00\x00Unittest data\n"

    async def test_onStreamDataRecv(self):
        """Тест на удачный парсинг данных Client::onStreamDataRecv."""
        serializer = MessageSerializer(msgspec.ClientappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = OnStreamDataRecvMsgParser().parse(msg)
        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id

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

        pd = res.result

        assert pd.stream_id == 1
        assert pd.stream_chunk == b"Unittest data\n"


class TestOnStreamDataCompleted:
    """Test Client::onStreamDataCompleted."""

    msg_spec = msgspec.client.onStreamDataCompleted
    data = b"\x02\x02\x15\x00\x01\x00\x0e\x00\x00\x00unittest.data\x00\x01"

    async def test_onStreamDataCompleted(self):
        """Тест на удачный парсинг данных Client::onStreamDataCompleted."""
        serializer = MessageSerializer(msgspec.ClientappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = OnStreamDataCompletedMsgParser().parse(msg)
        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id

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

        pd = res.result

        assert pd.stream_id == 1
