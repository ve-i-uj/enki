"""Тесты на парсинг сообщений от компонента Logger."""

from enki import msgspec
from enki.msg.msg_serializer import MessageSerializer
from enki.msg_parser.logger_msg_parser import (
    OnAppActiveTickMsgParser,
    OnRegisterNewAppMsgParser,
    WriteLogMsgParser,
)
from enki.msgspec import LoggerMsgSpecByID


class TestLogger_onRegisterNewApp:
    """Тесты сообщения Logger::onRegisterNewApp."""

    msg_spec = msgspec.logger.onRegisterNewApp
    data = b"\x08\x00*\x00\xe8\x03\x00\x00root\x00\x01\x00\x00\x00\xa1\x0f\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xac\x12\x00\x06\x9d\x99\x00\x00\x00\x00\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(LoggerMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

        result = OnRegisterNewAppMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        # Проверка нейминга, чтобы не было опечаток и т.п.
        assert result.msg_id == self.msg_spec.id
        assert (
            result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            result.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )
        assert result.msg_id == self.msg_spec.id


class TestLogger_writeLog:
    """Тесты сообщения Logger::writeLog."""

    msg_spec = msgspec.logger.writeLog
    data = b"\xc0\x02\x88\x00\xe8\x03\x00\x00\x10\x00\x00\x00\x01\x00\x00\x00\xa1\x0f\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xffR\xb0\x99h\x00\x00\x00\x00\xbb\x00\x00\x00\\\x00\x00\x00-----------------------------------------------------------------------------------------\n\n\n"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(LoggerMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

        result = WriteLogMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        # Проверка нейминга, чтобы не было опечаток и т.п.
        assert result.msg_id == self.msg_spec.id
        assert (
            result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            result.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )
        assert result.msg_id == self.msg_spec.id


class TestLogger_onAppActiveTick:
    """Тесты сообщения Logger::onAppActiveTick."""

    msg_spec = msgspec.logger.onAppActiveTick
    data = b"\xbd\x02\x01\x00\x00\x00\xa1\x0f\x00\x00\x00\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(LoggerMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

        result = OnAppActiveTickMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None

        # Проверка нейминга, чтобы не было опечаток и т.п.
        assert result.msg_id == self.msg_spec.id
        assert (
            result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            result.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )
        assert result.msg_id == self.msg_spec.id
