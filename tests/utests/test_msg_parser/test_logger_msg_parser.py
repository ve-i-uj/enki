"""Тесты на парсинг сообщений от компонента Logger."""

from enki import msgspec
from enki.msg.msg_serializer import MessageSerializer
from enki.msg_parser.logger_msg_parser import (
    DeregisterLogWatcherMsgParser,
    LookAppMsgParser,
    OnAppActiveTickMsgParser,
    OnRegisterNewAppMsgParser,
    QueryLoadMsgParser,
    QueryWatcherMsgParser,
    RegisterLogWatcherMsgParser,
    ReqCloseServerMsgParser,
    ReqKillServerMsgParser,
    StartProfileMsgParser,
    UpdateLogWatcherSettingMsgParser,
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
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

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
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

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
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

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


class TestLogger_lookApp:
    """Тесты сообщения Logger::lookApp."""

    msg_spec = msgspec.logger.lookApp
    data = b"\t\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(LoggerMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = LookAppMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id
        assert (
            result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            result.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )


class TestLogger_queryLoad:
    """Тесты сообщения Logger::queryLoad."""

    msg_spec = msgspec.logger.queryLoad
    data = b"\x0a\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(LoggerMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = QueryLoadMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id
        assert (
            result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            result.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )


class TestLogger_updateLogWatcherSetting:
    """Тесты сообщения Logger::updateLogWatcherSetting."""

    msg_spec = msgspec.logger.updateLogWatcherSetting
    data = b"\x0b\x00\x2a\x00\xe8\x03\x00\x00\xff\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x002024-01-01\x00key\x00\x03\x01\x02\x03"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(LoggerMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = UpdateLogWatcherSettingMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id
        assert (
            result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            result.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )


class TestLogger_reqCloseServer:
    """Тесты сообщения Logger::reqCloseServer."""

    msg_spec = msgspec.logger.reqCloseServer
    data = b"\x0c\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(LoggerMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = ReqCloseServerMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id
        assert (
            result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            result.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )


class TestLogger_startProfile:
    """Тесты сообщения Logger::startProfile."""

    msg_spec = msgspec.logger.startProfile
    data = b"\x0d\x00\x15\x00test_profile\x00\x01\xe8\x03\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(LoggerMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = StartProfileMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id
        assert (
            result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            result.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )


class TestLogger_reqKillServer:
    """Тесты сообщения Logger::reqKillServer."""

    msg_spec = msgspec.logger.reqKillServer
    data = b"\x0e\x00*\x00\xa1\x0f\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00root\x00\xe8\x03\x00\x00shutdown\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(LoggerMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = ReqKillServerMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id
        assert (
            result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            result.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )


class TestLogger_registerLogWatcher:
    """Тесты сообщения Logger::registerLogWatcher."""

    msg_spec = msgspec.logger.registerLogWatcher
    data = b"\xbe\x02\x2f\x00\xe8\x03\x00\x00\xff\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x002024-01-01\x00key\x00\x03\x01\x02\x03\x01\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(LoggerMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = RegisterLogWatcherMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id
        assert (
            result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            result.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )


class TestLogger_deregisterLogWatcher:
    """Тесты сообщения Logger::deregisterLogWatcher."""

    msg_spec = msgspec.logger.deregisterLogWatcher
    data = b"\xbf\x02\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(LoggerMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = DeregisterLogWatcherMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id
        assert (
            result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            result.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )


class TestLogger_queryWatcher:
    """Тесты сообщения Logger::queryWatcher."""

    msg_spec = msgspec.logger.queryWatcher
    data = b"\x50\xa0\x00\x00\x0a\x00/watchers\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(LoggerMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = QueryWatcherMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id
        assert (
            result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            result.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )
