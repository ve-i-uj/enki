"""Тесты на парсинг сообщений от компонента CellappMgr."""

import pytest

from enki import msgspec
from enki.msg.msg_serializer import MessageSerializer
from enki.msg_parser.cellappmgr_msg_parser import (
    ForwardMessageMsgParser,
    LookAppMsgParser,
    OnAppActiveTickMsgParser,
    OnCellappInitProgressMsgParser,
    OnLookAppMsgParser,
    OnRegisterNewAppMsgParser,
    QueryAppsLoadsMsgParser,
    QueryLoadMsgParser,
    QuerySpacesMsgParser,
    QueryWatcherMsgParser,
    ReqCreateCellEntityInNewSpaceMsgParser,
    ReqKillServerMsgParser,
    ReqRestoreSpaceInCellMsgParser,
    SetSpaceViewerMsgParser,
    StartProfileMsgParser,
    UpdateCellappMsgParser,
    UpdateSpaceDataMsgParser,
)
from enki.msgspec import CellappMgrMsgSpecByID


class TestCellappMgr_onAppActiveTick:
    """Тесты сообщения Cellappmgr::onAppActiveTick."""

    msg_spec = msgspec.cellappmgr.onAppActiveTick
    data = b">\xd7\n\x00\x00\x00\xd1\x07\x00\x00\x00\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(CellappMgrMsgSpecByID)
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

        pd = result.result

        assert pd.componentType == 10
        assert pd.componentID == 2001


class TestCellappMgr_onRegisterNewApp:
    """Тесты сообщения Cellappmgr::onRegisterNewApp."""

    msg_spec = msgspec.cellappmgr.onRegisterNewApp
    data = b"\x08\x00*\x00\xe8\x03\x00\x00root\x00\x03\x00\x00\x00q\x17\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xac\x12\x00\x08\xda\x07\x00\x00\x00\x00\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(CellappMgrMsgSpecByID)
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

        pd = result.result
        assert pd.uid == 1000
        assert pd.username == "root"
        assert pd.componentType == 3
        assert pd.componentID == 6001
        assert pd.globalorderID == -1
        assert pd.grouporderID == -1
        assert pd.intaddr == 134222508
        assert pd.intport == 2010
        assert pd.extaddr == 0
        assert pd.extport == 0
        assert pd.extaddrEx == ""


class TestCellappMgr_updateCellapp:
    """Тесты сообщения Cellappmgr::updateCellapp."""

    msg_spec = msgspec.cellappmgr.updateCellapp
    data = b"\x0f\x00Y\x1b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\x1b\xb4>\x00\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(CellappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = UpdateCellappMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        pd = result.result
        assert pd.componentID == 7001
        assert pd.numEntities == 0
        assert pd.load == 0.35176894068717957
        assert pd.flags == 0


class TestCellappMgr_updateSpaceData:
    """Тесты сообщения Cellappmgr::updateSpaceData."""

    msg_spec = msgspec.cellappmgr.updateSpaceData
    data = b"\x13\x00,\x00\x89\x13\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00Spaces\x00\x00/path/to/geomapping\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(CellappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = UpdateSpaceDataMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestCellappMgr_reqCreateCellEntityInNewSpace:
    """Тесты сообщения Cellappmgr::reqCreateCellEntityInNewSpace."""

    msg_spec = msgspec.cellappmgr.reqCreateCellEntityInNewSpace
    data = b"\x0b\x00\x10\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(CellappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = ReqCreateCellEntityInNewSpaceMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestCellappMgr_onCellappInitProgress:
    """Тесты сообщения Cellappmgr::onCellappInitProgress."""

    msg_spec = msgspec.cellappmgr.onCellappInitProgress
    data = b"\x12\x00Y\x1b\x00\x00\x00\x00\x00\x00\x00\x00\xc8B\x05\x00\x00\x00\x01\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(CellappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = OnCellappInitProgressMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        pd = result.result
        assert pd.cid == 7001
        assert pd.progress == 100.0
        assert pd.componentGlobalOrder == 5
        assert pd.componentGroupOrder == 1


class TestCellappMgr_queryLoad:
    """Тесты сообщения Cellappmgr::queryLoad."""

    msg_spec = msgspec.cellappmgr.queryLoad
    data = b"\n\x00\x1a\x00\x89\x13\x00\x00\x00\x00\x00\x00Cellapp\x00"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(CellappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = QueryLoadMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestCellappMgr_reqRestoreSpaceInCell:
    """Тесты сообщения Cellappmgr::reqRestoreSpaceInCell."""

    msg_spec = msgspec.cellappmgr.reqRestoreSpaceInCell
    data = b"\x0c\x00$\x00\x89\x13\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00Spaces\x00"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(CellappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = ReqRestoreSpaceInCellMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestCellappMgr_forwardMessage:
    """Тесты сообщения Cellappmgr::forwardMessage."""

    msg_spec = msgspec.cellappmgr.forwardMessage
    data = b"\r\x00 \x00\x89\x13\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x04\x00\x00\x00test"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(CellappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = ForwardMessageMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestCellappMgr_startProfile:
    """Тесты сообщения Cellappmgr::startProfile."""

    msg_spec = msgspec.cellappmgr.startProfile
    data = b"\x10\x00\x1b\x00CPUProfile\x00\x01\xe8\x03\x00\x00"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(CellappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = StartProfileMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestCellappMgr_reqKillServer:
    """Тесты сообщения Cellappmgr::reqKillServer."""

    msg_spec = msgspec.cellappmgr.reqKillServer
    data = b"\x11\x00\x00\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(CellappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = ReqKillServerMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestCellappMgr_queryWatcher:
    """Тесты сообщения Cellappmgr::queryWatcher."""

    msg_spec = msgspec.cellappmgr.queryWatcher
    data = b"\x88\xa0\x01\x003\x00\x03\x00\x00\x00\x89\x13\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00root\x00/components\x00"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(CellappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = QueryWatcherMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestCellappMgr_queryAppsLoads:
    """Тесты сообщения Cellappmgr::queryAppsLoads."""

    msg_spec = msgspec.cellappmgr.queryAppsLoads
    data = b'B\xc3\x01\x00"\x00\x03\x00\x00\x00\x89\x13\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00root\x00'

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(CellappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = QueryAppsLoadsMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestCellappMgr_querySpaces:
    """Тесты сообщения Cellappmgr::querySpaces."""

    msg_spec = msgspec.cellappmgr.querySpaces
    data = b'\x83\xc3\x01\x00"\x00\x03\x00\x00\x00\x89\x13\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00root\x00'

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(CellappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = QuerySpacesMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestCellappMgr_setSpaceViewer:
    """Тесты сообщения Cellappmgr::setSpaceViewer."""

    msg_spec = msgspec.cellappmgr.setSpaceViewer
    data = b"\x84\xc3\x01\x002\x00\x03\x00\x00\x00\x89\x13\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00root\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00"

    @pytest.mark.skip("TODO: Нужны реальные тестовые данные")
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(CellappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = SetSpaceViewerMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id


class TestCellappMgr_lookApp:
    """Тесты сообщения Cellappmgr::lookApp."""

    msg_spec = msgspec.cellappmgr.lookApp
    data = b"\t\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(CellappMgrMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = LookAppMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        # Сообщение пустое


class TestCellappMgr_onLookApp:
    """Тесты сообщения Cellappmgr::onLookApp."""

    msg_spec = msgspec.cellappmgr.onLookApp
    data = b"\x04\x00\x00\x00\x89\x13\x00\x00\x00\x00\x00\x00\x01"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(CellappMgrMsgSpecByID)
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
        assert pd.componentType == 4
        assert pd.componentId == 5001
        assert pd.shutdownState == 1
