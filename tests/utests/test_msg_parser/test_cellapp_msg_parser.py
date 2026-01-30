import pytest

from enki import msgspec
from enki.msg.msg_serializer import MessageSerializer
from enki.msg_parser.cellapp_msg_parser import (
    ForwardEntityMessageToCellappFromClientMsgParser,
    OnAppActiveTickMsgParser,
    OnBroadcastCellAppDataChangedMsgParser,
    OnCreateCellEntityInNewSpaceFromBaseappMsgParser,
    OnDbmgrInitCompletedMsgParser,
    OnDestroyCellEntityFromBaseappMsgParser,
    OnEntityCallMsgParser,
    OnExecScriptCommandMsgParser,
    OnExecuteRawDatabaseCommandCBMsgParser,
    OnGetEntityAppFromDbmgrMsgParser,
    OnRegisterNewAppMsgParser,
    OnRemoteCallMethodFromClientMsgParser,
    OnRemoteRealMethodCallMsgParser,
    OnReqAllocEntityIDMsgParser,
    OnRestoreSpaceInCellFromBaseappMsgParser,
    OnUpdateDataFromClientForControlledEntityMsgParser,
    OnUpdateDataFromClientMsgParser,
    OnUpdateGhostPropertysMsgParser,
    OnUpdateGhostVolatileDataMsgParser,
    QueryLoadMsgParser,
    QueryWatcherMsgParser,
    ReqKillServerMsgParser,
    ReqSetFlagsMsgParser,
    ReqTeleportToCellAppCBMsgParser,
    ReqTeleportToCellAppMsgParser,
    ReqTeleportToCellAppOverMsgParser,
    RequestRestoreMsgParser,
    ReqWriteToDBFromBaseappMsgParser,
    SetSpaceViewerMsgParser,
    StartProfileMsgParser,
)
from enki.msgspec import CellappMsgSpecByID


class TestCellapp_OnBroadcastCellAppDataChanged:
    """Тест для OnBroadcastCellAppDataChanged - обработка изменения данных CellApp."""

    msg_spec = msgspec.cellapp.onBroadcastCellAppDataChanged
    # Данные: isDelete=False, key=pickle.dumps("test_key"), value=pickle.dumps("test_value")
    data = b"\x1f\x005\x00\x00\x80\x04\x95\x0b\x00\x00\x00\x00\x00\x00\x00\x8c\x08test_key\x94.\x80\x04\x95\x0c\x00\x00\x00\x00\x00\x00\x00\x8c\ttest_value\x94."

    @pytest.mark.skip("Случайные данные")
    def test_onBroadcastCellAppDataChanged(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnBroadcastCellAppDataChangedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert not res.result.isDelete
        assert res.result.key == "test_key"
        assert res.result.value == "test_value"


class TestCellapp_OnCreateCellEntityInNewSpaceFromBaseapp:
    """Тест для создания сущности в новом пространстве."""

    msg_spec = msgspec.cellapp.onCreateCellEntityInNewSpaceFromBaseapp
    data = b"\x1e\x00E\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00TestEntityType\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

    @pytest.mark.skip("Случайные данные")
    def test_onCreateCellEntityInNewSpaceFromBaseapp(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnCreateCellEntityInNewSpaceFromBaseappMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        # Основная проверка делегируется CreateCellEntityInNewSpaceFromBaseappParser
        # который уже должен быть протестирован отдельно


class TestCellapp_OnGetEntityAppFromDbmgr:
    """Тест для получения информации о приложении сущности от Dbmgr."""

    msg_spec = msgspec.cellapp.onGetEntityAppFromDbmgr
    data = b"\x0f\x00=\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00"

    @pytest.mark.skip("Случайные данные")
    def test_onGetEntityAppFromDbmgr(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnGetEntityAppFromDbmgrMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        # Значения будут распакованы в соответствии со структурой OnGetEntityAppFromDbmgrParsedMsgData


class TestCellapp_OnAppActiveTick:
    """Тест парсинга сообщения Cellapp::onAppActiveTick."""

    msg_spec = msgspec.cellapp.onAppActiveTick
    data = b"=\xd7\x03\x00\x00\x00q\x17\x00\x00\x00\x00\x00\x00"

    def test_onAppActiveTick(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnAppActiveTickMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.msg_id == self.msg_spec.id

        pd = res.result
        assert pd.componentType == 3
        assert pd.componentID == 6001


class TestCellapp_onRegisterNewApp:
    """Тесты сообщения Cellapp::onRegisterNewApp."""

    msg_spec = msgspec.cellapp.onRegisterNewApp
    data = b"\x08\x001\x00\xe8\x03\x00\x00root\x00\x06\x00\x00\x00A\x1f\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xac\x12\x00\n\xbc\xff\xac\x12\x00\nN/0.0.0.0\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = OnRegisterNewAppMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        pd = result.result
        assert pd.uid == 1000
        assert pd.username == "root"
        assert pd.componentType == 6
        assert pd.componentID == 8001
        assert pd.globalorderID == -1
        assert pd.grouporderID == -1
        assert pd.intaddr == 167776940
        assert pd.intport == 65468
        assert pd.extaddr == 167776940
        assert pd.extport == 12110
        assert pd.extaddrEx == "0.0.0.0"


class TestCellapp_QueryLoad:
    """Тест для запроса нагрузки."""

    msg_spec = msgspec.cellapp.queryLoad
    data = b"\x1c\x00\x04\x00test_load_data\x00"

    @pytest.mark.skip("Случайные данные")
    def test_queryLoad(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = QueryLoadMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.result.load_data == b"test_load_data\x00"


class TestCellapp_OnExecScriptCommand:
    """Тест для выполнения скриптовой команды."""

    msg_spec = msgspec.cellapp.onExecScriptCommand
    data = b'\x1d\x00\x04\x00print("hello")\x00'

    @pytest.mark.skip("Случайные данные")
    def test_onExecScriptCommand(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnExecScriptCommandMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.result.script_data == b'print("hello")\x00'


class TestCellapp_OnReqAllocEntityID:
    """Тест для запроса выделения ID сущности."""

    msg_spec = msgspec.cellapp.onReqAllocEntityID
    data = b"!\x00\x04\x00\x01\x00\x00\x00\x02\x00\x00\x00"

    @pytest.mark.skip("Случайные данные")
    def test_onReqAllocEntityID(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnReqAllocEntityIDMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.result.alloc_data == b"\x01\x00\x00\x00\x02\x00\x00\x00"


class TestCellapp_OnRestoreSpaceInCellFromBaseapp:
    """Тест для восстановления пространства в клетке от Baseapp."""

    msg_spec = msgspec.cellapp.onRestoreSpaceInCellFromBaseapp
    data = b'"\x00\x04\x00\x01\x00\x00\x00restore_data\x00'

    @pytest.mark.skip("Случайные данные")
    def test_onRestoreSpaceInCellFromBaseapp(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnRestoreSpaceInCellFromBaseappMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.result.restore_data == b"\x01\x00\x00\x00restore_data\x00"


class TestCellapp_RequestRestore:
    """Тест для запроса восстановления."""

    msg_spec = msgspec.cellapp.requestRestore
    data = b"#\x00\x04\x00restore_request_data\x00"

    @pytest.mark.skip("Случайные данные")
    def test_requestRestore(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = RequestRestoreMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.result.request_data == b"restore_request_data\x00"


class TestCellapp_OnDestroyCellEntityFromBaseapp:
    """Тест для уничтожения сущности клетки от Baseapp."""

    msg_spec = msgspec.cellapp.onDestroyCellEntityFromBaseapp
    data = b"$\x00\x04\x00destroy_entity_data\x00"

    @pytest.mark.skip("Случайные данные")
    def test_onDestroyCellEntityFromBaseapp(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnDestroyCellEntityFromBaseappMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.result.destroy_data == b"destroy_entity_data\x00"


class TestCellapp_OnEntityCall:
    """Тест для вызова сущности."""

    msg_spec = msgspec.cellapp.onEntityCall
    data = b"%\x00\x04\x00entity_call_binary_data\x00"

    @pytest.mark.skip("Случайные данные")
    def test_onEntityCall(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnEntityCallMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.result.entity_call_data == b"entity_call_binary_data\x00"


class TestCellapp_OnRemoteCallMethodFromClient:
    """Тест для удаленного вызова метода от клиента."""

    msg_spec = msgspec.cellapp.onRemoteCallMethodFromClient
    data = b"&\x00\x04\x00remote_method_call_data\x00"

    @pytest.mark.skip("Случайные данные")
    def test_onRemoteCallMethodFromClient(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnRemoteCallMethodFromClientMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.result.remote_call_data == b"remote_method_call_data\x00"


class TestCellapp_OnUpdateDataFromClient:
    """Тест для обновления данных от клиента."""

    msg_spec = msgspec.cellapp.onUpdateDataFromClient
    data = b"'\x00\x04\x00client_update_data\x00"

    @pytest.mark.skip("Случайные данные")
    def test_onUpdateDataFromClient(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnUpdateDataFromClientMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.result.update_data == b"client_update_data\x00"


class TestCellapp_OnUpdateDataFromClientForControlledEntity:
    """Тест для обновления данных контролируемой сущности от клиента."""

    msg_spec = msgspec.cellapp.onUpdateDataFromClientForControlledEntity
    data = b"(\x00\x04\x00controlled_entity_update\x00"

    @pytest.mark.skip("Случайные данные")
    def test_onUpdateDataFromClientForControlledEntity(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnUpdateDataFromClientForControlledEntityMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert (
            res.result.controlled_update_data == b"controlled_entity_update\x00"
        )


class TestCellapp_OnExecuteRawDatabaseCommandCB:
    """Тест для колбэка выполнения сырой команды БД."""

    msg_spec = msgspec.cellapp.onExecuteRawDatabaseCommandCB
    data = b")\x00\x04\x00db_command_callback_data\x00"

    @pytest.mark.skip("Случайные данные")
    def test_onExecuteRawDatabaseCommandCB(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnExecuteRawDatabaseCommandCBMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.result.db_command_data == b"db_command_callback_data\x00"


class TestCellapp_ReqWriteToDBFromBaseapp:
    """Тест для записи в БД от Baseapp."""

    msg_spec = msgspec.cellapp.reqWriteToDBFromBaseapp
    data = b"*\x00\x04\x00write_to_db_data\x00"

    @pytest.mark.skip("Случайные данные")
    def test_reqWriteToDBFromBaseapp(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = ReqWriteToDBFromBaseappMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.result.write_db_data == b"write_to_db_data\x00"


class TestCellapp_ForwardEntityMessageToCellappFromClient:
    """Тест для пересылки сообщения сущности от клиента."""

    msg_spec = msgspec.cellapp.forwardEntityMessageToCellappFromClient
    data = b"+\x00\x04\x00forwarded_message_data\x00"

    @pytest.mark.skip("Случайные данные")
    def test_forwardEntityMessageToCellappFromClient(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = ForwardEntityMessageToCellappFromClientMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert (
            res.result.forwarded_message_data == b"forwarded_message_data\x00"
        )


class TestCellapp_QueryWatcher:
    """Тест для запроса наблюдателя."""

    msg_spec = msgspec.cellapp.queryWatcher
    data = b",\x00\x04\x00watcher_query_data\x00"

    @pytest.mark.skip("Случайные данные")
    def test_queryWatcher(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = QueryWatcherMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.result.watcher_query_data == b"watcher_query_data\x00"


class TestCellapp_StartProfile:
    """Тест для начала профилирования."""

    msg_spec = msgspec.cellapp.startProfile
    data = b"-\x00\x04\x00profile_start_data\x00"

    @pytest.mark.skip("Случайные данные")
    def test_startProfile(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = StartProfileMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.result.profile_data == b"profile_start_data\x00"


class TestCellapp_ReqTeleportToCellApp:
    """Тест для запроса телепорта к CellApp."""

    msg_spec = msgspec.cellapp.reqTeleportToCellApp
    data = b".\x00\x04\x00teleport_request_data\x00"

    @pytest.mark.skip("Случайные данные")
    def test_reqTeleportToCellApp(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = ReqTeleportToCellAppMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.result.teleport_data == b"teleport_request_data\x00"


class TestCellapp_ReqTeleportToCellAppCB:
    """Тест для колбэка телепорта к CellApp."""

    msg_spec = msgspec.cellapp.reqTeleportToCellAppCB
    data = b"/\x00\x04\x00teleport_callback_data\x00"

    @pytest.mark.skip("Случайные данные")
    def test_reqTeleportToCellAppCB(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = ReqTeleportToCellAppCBMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert (
            res.result.teleport_callback_data == b"teleport_callback_data\x00"
        )


class TestCellapp_ReqTeleportToCellAppOver:
    """Тест для завершения телепорта к CellApp."""

    msg_spec = msgspec.cellapp.reqTeleportToCellAppOver
    data = b"0\x00\x04\x00teleport_complete_data\x00"

    @pytest.mark.skip("Случайные данные")
    def test_reqTeleportToCellAppOver(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = ReqTeleportToCellAppOverMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert (
            res.result.teleport_complete_data == b"teleport_complete_data\x00"
        )


class TestCellapp_OnUpdateGhostPropertys:
    """Тест для обновления свойств призрака."""

    msg_spec = msgspec.cellapp.onUpdateGhostPropertys
    data = b"1\x00\x04\x00ghost_properties_update\x00"

    @pytest.mark.skip("Случайные данные")
    def test_onUpdateGhostPropertys(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnUpdateGhostPropertysMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert (
            res.result.ghost_properties_data == b"ghost_properties_update\x00"
        )


class TestCellapp_OnRemoteRealMethodCall:
    """Тест для удаленного вызова реального метода."""

    msg_spec = msgspec.cellapp.onRemoteRealMethodCall
    data = b"2\x00\x04\x00remote_real_method_call\x00"

    @pytest.mark.skip("Случайные данные")
    def test_onRemoteRealMethodCall(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnRemoteRealMethodCallMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert (
            res.result.remote_real_method_data == b"remote_real_method_call\x00"
        )


class TestCellapp_OnUpdateGhostVolatileData:
    """Тест для обновления изменчивых данных призрака."""

    msg_spec = msgspec.cellapp.onUpdateGhostVolatileData
    data = b"3\x00\x04\x00ghost_volatile_update\x00"

    @pytest.mark.skip("Случайные данные")
    def test_onUpdateGhostVolatileData(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = OnUpdateGhostVolatileDataMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.result.ghost_volatile_data == b"ghost_volatile_update\x00"


class TestCellapp_ReqKillServer:
    """Тест для запроса убийства сервера."""

    msg_spec = msgspec.cellapp.reqKillServer
    data = b"4\x00\x04\x00kill_server_request\x00"

    @pytest.mark.skip("Случайные данные")
    def test_reqKillServer(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = ReqKillServerMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.result.kill_server_data == b"kill_server_request\x00"


class TestCellapp_ReqSetFlags:
    """Тест для установки флагов."""

    msg_spec = msgspec.cellapp.reqSetFlags
    data = b"5\x00\x04\x00set_flags_request\x00"

    @pytest.mark.skip("Случайные данные")
    def test_reqSetFlags(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = ReqSetFlagsMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.result.set_flags_data == b"set_flags_request\x00"


class TestCellapp_SetSpaceViewer:
    """Тест для установки просмотрщика пространства."""

    msg_spec = msgspec.cellapp.setSpaceViewer
    data = b"6\x00\x04\x00space_viewer_set_data\x00"

    @pytest.mark.skip("Случайные данные")
    def test_setSpaceViewer(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        res = SetSpaceViewerMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None
        assert res.result.space_viewer_data == b"space_viewer_set_data\x00"


class TestCellapp_onDbmgrInitCompleted:
    """Тесты сообщения Cellapp::onDbmgrInitCompleted."""

    msg_spec = msgspec.cellapp.onDbmgrInitCompleted
    data = b"\r\x005\x00\x9a\x02\x00\x00\xd1\x07\x00\x00\xa1\x0f\x00\x00\x05\x00\x00\x00\x01\x00\x00\x0006E15F102B481ACF8CA19E2F410D1B64\x00"

    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        assert not data_tail

        result = OnDbmgrInitCompletedMsgParser().parse(msg)

        assert result.success is True
        assert result.result is not None
        assert result.msg_id == self.msg_spec.id

        pd = result.result
        assert pd.gametime == 666
        assert pd.startID == 2001
        assert pd.endID == 4001
        assert pd.startGlobalOrder == 5
        assert pd.startGroupOrder == 1
        assert pd.digest == "06E15F102B481ACF8CA19E2F410D1B64"
