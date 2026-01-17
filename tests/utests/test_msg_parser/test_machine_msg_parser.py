"""Тесты на парсинг сообщений от компонента Machine."""

from enki import msgspec
from enki.msg.msg_serializer import MessageSerializer
from enki.msg_parser.machine_msg_parser import (
    OnBroadcastInterfaceMsgParser,
    OnFindInterfaceAddrMsgParser,
)
from enki.msgspec import MachineMsgSpecByID


class TestMachine_onBroadcastInterface:
    """Тесты сообщения Machine::onBroadcastInterface."""

    msg_spec = msgspec.machine.onBroadcastInterface
    data = b"\x08\x00q\x00\xe8\x03\x00\x00root\x00\n\x00\x00\x00\xd1\x07\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xac\x12\x00\x04\x93\xcf\xac\x12\x00\x04\x83S\x00\x85>\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10:\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd0\x84\x00\x00\x00\x00\x00\x00\xac\x12\x00\x04Q\xca"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(MachineMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

        result = OnBroadcastInterfaceMsgParser().parse(msg)

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


class TestMachine_onFindInterfaceAddr:
    """Тесты сообщения Machine::onFindInterfaceAddr."""

    msg_spec = msgspec.machine.onFindInterfaceAddr
    data = b"\x01\x00\x1f\x00\xe8\x03\x00\x00root\x00\x01\x00\x00\x00\xa1\x0f\x00\x00\x00\x00\x00\x00\n\x00\x00\x00\xac\x12\x00\x06Qz"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(MachineMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

        result = OnFindInterfaceAddrMsgParser().parse(msg)

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
