"""Тесты на парсинг сообщений от компонента Machine."""

import pytest
from enki import msgspec
from enki.msg.msg_serializer import MessageSerializer
from enki.msg_parser.machine_msg_parser import (
    OnBroadcastInterfaceMsgParser,
    OnFindInterfaceAddrMsgParser,
    QueryComponentIDMsgParser,
    OnQueryAllInterfaceInfosMsgParser,
    LookAppMsgParser,
    OnLookAppMsgParser,
    OnQueryMachinesMsgParser,
    QueryLoadMsgParser,
    StartServerMsgParser,
    StopServerMsgParser,
    KillServerMsgParser,
    SetFlagsMsgParser,
    ReqKillServerMsgParser,
)
from enki.msgspec import MachineMsgSpecByID


class TestMachine_onBroadcastInterface:
    """Тесты сообщения Machine::onBroadcastInterface."""

    msg_spec = msgspec.machine.onBroadcastInterface
    data = b"\x08\x00q\x00\xe8\x03\x00\x00root\x00\x05\x00\x00\x00Y\x1b\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00\x01\x00\x00\x00\xff\xff\xff\xff\xac\x12\x00\t\xbf\x93\x00\x00\x00\x00\x00\x00\x00\xcd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe0\xc6\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00P\xc3\x00\x00\x00\x00\x00\x00\xac\x12\x00\tPJ"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(MachineMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

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

        pd = result.result

        # Основные поля
        assert pd.uid == 1000
        assert pd.username == "root"
        assert pd.componentType == 5
        assert pd.componentID == 7001
        assert pd.componentIDEx == 2
        assert pd.globalorderid == 5
        assert pd.grouporderid == 1
        assert pd.gus == -1
        assert pd.intaddr == 150999724
        assert pd.intport == 37823
        assert pd.extaddr == 0
        assert pd.extport == 0
        assert pd.extaddrEx == ""
        assert pd.pid == 205
        assert pd.cpu == 0.0
        assert pd.mem == 0.0
        assert pd.usedmem == 29810688
        assert pd.state == 0
        assert pd.machineID == 0
        assert pd.extradata == 0
        assert pd.extradata1 == 0
        assert pd.extradata2 == 0
        assert pd.extradata3 == 50000
        assert pd.backRecvAddr == 150999724
        assert pd.backRecvPort == 19024


class TestMachine_onFindInterfaceAddr:
    """Тесты сообщения Machine::onFindInterfaceAddr."""

    msg_spec = msgspec.machine.onFindInterfaceAddr
    data = b"\x01\x00\x1f\x00\xe8\x03\x00\x00root\x00\x03\x00\x00\x00q\x17\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\xac\x12\x00\x08Q\x12"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(MachineMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

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

        pd = result.result

        # Основные поля
        assert pd.uid == 1000
        assert pd.username == "root"
        assert pd.componentType == 3
        assert pd.componentID == 6001
        assert pd.findComponentType == 4
        assert pd.finderAddr == 134222508
        assert pd.finderRecvPort == 4689


class TestMachine_queryComponentID:
    """Тесты сообщения Machine::queryComponentID."""

    msg_spec = msgspec.machine.queryComponentID
    data = b"\t\x00\x1a\x00\r\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x85\x92\x00\x00\x9c\x97gT\x00\x00M\x06\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(MachineMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = QueryComponentIDMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        pd = result.result

        assert pd.componentType == 13
        assert pd.componentID == 0
        assert pd.uid == 37509
        assert pd.finderRecvPort == 38812
        assert pd.macMD5 == 21607
        assert pd.pid == 1613


class TestMachine_onQueryAllInterfaceInfos:
    """Тесты сообщения Machine::onQueryAllInterfaceInfos."""

    msg_spec = msgspec.machine.onQueryAllInterfaceInfos
    data = b"\x04\x00\x07\x00\x00\x00\x00\x00\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(MachineMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = OnQueryAllInterfaceInfosMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        pd = result.result

        # Основные поля
        assert pd.uid == 0
        assert pd.username == ""
        assert pd.finderRecvPort == 0


class TestMachine_lookApp:
    """Тесты сообщения Machine::lookApp."""

    msg_spec = msgspec.machine.lookApp
    data = b"\n\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(MachineMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = LookAppMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestMachine_onLookApp:
    """Тесты сообщения Machine::onLookApp."""

    msg_spec = msgspec.machine.onLookApp
    data = b"\x08\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(MachineMsgSpecByID)
        msg, data_tail = serializer.deserialize_only_data(
            self.data, self.msg_spec.id
        )
        assert msg is not None
        assert not data_tail

        result = OnLookAppMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        pd = result.result

        # Основные поля
        assert pd.componentType == 8
        assert pd.componentId == 1
        assert pd.shutdownState == 1


class TestMachine_onQueryMachines:
    """Тесты сообщения Machine::onQueryMachines."""

    msg_spec = msgspec.machine.onQueryMachines
    data = b"\x05\x00\x11\x00\x01\x00\x00\x00\x01\x00\x00\x00TestFilter\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(MachineMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = OnQueryMachinesMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        pd = result.result

        # Основные поля
        assert pd.machineID == 1
        assert pd.queryType == 1
        assert pd.filter == "TestFilter"


class TestMachine_queryLoad:
    """Тесты сообщения Machine::queryLoad."""

    msg_spec = msgspec.machine.queryLoad
    data = b"\x0b\x00\x04\x00\x01\x02\x03\x04"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(MachineMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = QueryLoadMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        pd = result.result

        # Основные поля
        assert pd.data == b"\x01\x02\x03\x04"


class TestMachine_startserver:
    """Тесты сообщения Machine::startserver."""

    msg_spec = msgspec.machine.startserver
    data = b"\x02\x00\t\x00start_data\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(MachineMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = StartServerMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        pd = result.result

        # Основные поля
        assert pd.data == b"start_data"


class TestMachine_stopserver:
    """Тесты сообщения Machine::stopserver."""

    msg_spec = msgspec.machine.stopserver
    data = b"\x03\x00\x08\x00stop_data\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(MachineMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = StopServerMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        pd = result.result

        # Основные поля
        assert pd.data == b"stop_data"


class TestMachine_killserver:
    """Тесты сообщения Machine::killserver."""

    msg_spec = msgspec.machine.killserver
    data = b"\x06\x00\t\x00kill_data\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(MachineMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = KillServerMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        pd = result.result

        # Основные поля
        assert pd.data == b"kill_data"


class TestMachine_setflags:
    """Тесты сообщения Machine::setflags."""

    msg_spec = msgspec.machine.setflags
    data = b"\x07\x00\x0b\x00flags_data\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(MachineMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = SetFlagsMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        pd = result.result

        # Основные поля
        assert pd.data == b"flags_data"


class TestMachine_reqKillServer:
    """Тесты сообщения Machine::reqKillServer."""

    msg_spec = msgspec.machine.reqKillServer
    data = b"\x0c\x00\x0e\x00req_kill_data\x00"

    @pytest.mark.skip("Случайные данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(MachineMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = ReqKillServerMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        pd = result.result

        # Основные поля
        assert pd.data == b"req_kill_data"
