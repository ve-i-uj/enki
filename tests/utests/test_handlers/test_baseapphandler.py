from unittest import TestCase

from enki.core import msgspec, utils
from enki.core.enkitype import AppAddr
from enki.core.kbeenum import ComponentType
from enki.handler import serverhandler
from enki.handler.serverhandler.baseapphandler import OnAppActiveTickHandler, OnBroadcastGlobalDataChangedHandler, OnEntityAutoLoadCBFromDBMgrHandler, \
    OnDbmgrInitCompletedHandlerResult, OnEntityGetCellHandler, OnGetEntityAppFromDbmgrHandler, OnRegisterNewAppHandler
from tools import msgreader


class OnDbmgrInitCompletedHandlerTestCase(TestCase):

    def test_onDbmgrInitCompleted(self):
        handlers = serverhandler.SERVER_HANDLERS.get('baseapp')
        assert handlers is not None
        handler = handlers.get(
            msgspec.app.baseapp.onDbmgrInitCompleted.id
        )
        assert handler is not None
        str_data = '0d0035006b110000d1070000a10f00000400000001000000303645313546313032423438314143463843413139453246343130443142363400'
        data = msgreader.normalize_wireshark_data(str_data)
        serializer = utils.get_serializer_for(ComponentType.BASEAPP)
        msg, data_tail = serializer.deserialize(memoryview(data))
        assert not data_tail
        assert msg is not None

        res: OnDbmgrInitCompletedHandlerResult = handler().handle(msg) # type: ignore
        assert res.success
        pd = res.result

        assert pd.startID == 2001
        assert pd.endID == 4001
        assert pd.startGlobalOrder == 4
        assert pd.startGroupOrder == 1
        assert pd.digest == '06E15F102B481ACF8CA19E2F410D1B64'


class OnEntityAutoLoadCBFromDBMgrHandlerTestCase(TestCase):

    def test_onEntityAutoLoadCBFromDBMgr(self):
        handler = OnEntityAutoLoadCBFromDBMgrHandler()
        assert handler is not None
        str_data = '170008000000000000000100'
        data = msgreader.normalize_wireshark_data(str_data)
        serializer = utils.get_serializer_for(ComponentType.BASEAPP)
        msg, data_tail = serializer.deserialize(memoryview(data))
        assert not data_tail
        assert msg is not None

        res = handler.handle(msg) # type: ignore
        assert res.success
        pd = res.result

        assert pd.dbInterfaceIndex == 0
        assert pd.size == 0
        assert pd.entityType == 1
        assert pd.dbids == []


class OnBroadcastGlobalDataChangedHandlerTestCase(TestCase):

    def test_onBroadcastGlobalDataChanged(self):
        handler = OnBroadcastGlobalDataChangedHandler()
        assert handler is not None
        str_data = '0e004600000d0000005673706163655f310a70300a2e30000000635f7570660a456e7469747943616c6c0a70300a2849323030320a49373030310a49390a49310a7470310a5270320a2e'
        data = msgreader.normalize_wireshark_data(str_data)
        serializer = utils.get_serializer_for(ComponentType.BASEAPP)
        msg, data_tail = serializer.deserialize(memoryview(data))
        assert not data_tail
        assert msg is not None

        res = handler.handle(msg)
        assert res.success
        pd = res.result
        assert not pd.isDelete
        assert pd.key == 'space_1'
        assert pd.value is not None


class OnRegisterNewAppHandlerTestCase(TestCase):

    def test_onRegisterNewApp(self):
        handler = OnRegisterNewAppHandler()
        assert handler is not None
        str_data = '0a002e00e80300006b62656e67696e650005000000411f0000000000000300000001000000c0a8300aaec700000000000000'
        data = msgreader.normalize_wireshark_data(str_data)
        serializer = utils.get_serializer_for(ComponentType.BASEAPP)
        msg, data_tail = serializer.deserialize(memoryview(data))
        assert not data_tail
        assert msg is not None

        res = handler.handle(msg)
        assert res.success
        assert res.result is not None


class OnEntityGetCellHandlerTestCase(TestCase):

    def test_onRegisterNewApp(self):
        handler = OnEntityGetCellHandler()
        assert handler is not None
        str_data = '1400d2070000411f00000000000001000000'
        data = msgreader.normalize_wireshark_data(str_data)
        serializer = utils.get_serializer_for(ComponentType.BASEAPP)
        msg, data_tail = serializer.deserialize(memoryview(data))
        assert not data_tail
        assert msg is not None

        res = handler.handle(msg)
        assert res.success
        pd = res.result
        assert pd.componentID == 8001
        assert pd.entity_id == 2002
        assert pd.spaceID == 1


class OnGetEntityAppFromDbmgrTestCase(TestCase):

    def test_onRegisterNewApp(self):
        handler = OnGetEntityAppFromDbmgrHandler()
        assert handler is not None
        str_data = '0b002a00e8030000726f6f740005000000411f0000000000000400000001000000ac17000a9c1700000000000000'
        data = msgreader.normalize_wireshark_data(str_data)
        serializer = utils.get_serializer_for(ComponentType.BASEAPP)
        msg, data_tail = serializer.deserialize(memoryview(data))
        assert not data_tail
        assert msg is not None

        res = handler.handle(msg)
        assert res.success
        assert res.msg_id == msgspec.app.baseapp.onGetEntityAppFromDbmgr.id
        pd = res.result
        assert pd.componentID == 8001
        assert pd.internal_address == AppAddr(host='172.23.0.10', port=39959)
        assert pd.intport == 6044
