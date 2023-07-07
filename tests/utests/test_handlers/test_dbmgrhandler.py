from unittest import TestCase

from enki.core import msgspec, utils
from enki.core.kbeenum import ComponentType
from enki.core.message import MessageSerializer
from enki.handler import serverhandler
from enki.handler.serverhandler.dbmgrhandler import EntityAutoLoadHandler, OnBroadcastGlobalDataChangedHandlerResult, SyncEntityStreamTemplateHandlerResult
from tools import msgreader


class OnBroadcastGlobalDataChangedHandlerTestCase(TestCase):

    def test_onBroadcastGlobalDataChanged(self):
        handlers = serverhandler.SERVER_HANDLERS.get('dbmgr')
        assert handlers is not None
        handler = handlers.get(
            msgspec.app.dbmgr.onBroadcastGlobalDataChanged.id
        )
        assert handler is not None
        str_data = '0c004b0000000d0000005673706163655f310a70300a2e30000000635f7570660a456e7469747943616c6c0a70300a2849323030320a49373030310a49390a49310a7470310a5270320a2e05000000'
        data = msgreader.normalize_wireshark_data(str_data)
        serializer = utils.get_serializer_for(ComponentType.DBMGR)
        msg, data_tail = serializer.deserialize(memoryview(data))
        assert not data_tail
        assert msg is not None

        res: OnBroadcastGlobalDataChangedHandlerResult = handler().handle(msg) # type: ignore
        assert res.success
        assert not res.result.isDelete
        assert res.result.key == 'space_1'
        assert res.result.value is not None
        assert res.result.componentType == ComponentType.CELLAPP


class SyncEntityStreamTemplateTestCase(TestCase):

    def test_syncEntityStreamTemplate(self):
        # См. комментарий к обработчику
        handlers = serverhandler.SERVER_HANDLERS.get('dbmgr')
        assert handlers is not None
        handler = handlers.get(
            msgspec.app.dbmgr.syncEntityStreamTemplate.id
        )
        assert handler is not None
        str_data = '1d0014000000010000000000000002000000000000000000'
        data = msgreader.normalize_wireshark_data(str_data)
        serializer = utils.get_serializer_for(ComponentType.DBMGR)
        msg, data_tail = serializer.deserialize(memoryview(data))
        assert not data_tail
        assert msg is not None

        res: SyncEntityStreamTemplateHandlerResult = handler().handle(msg) # type: ignore
        assert res.success
        pd = res.result
        assert isinstance(pd.data, bytes)


class EntityAutoLoadTestCase(TestCase):

    def test_entityAutoLoad(self):
        handler = EntityAutoLoadHandler()
        str_data = '1c0014000000591b00000000000001000000000020000000'
        data = msgreader.normalize_wireshark_data(str_data)
        serializer = utils.get_serializer_for(ComponentType.DBMGR)
        msg, data_tail = serializer.deserialize(memoryview(data))
        assert not data_tail
        assert msg is not None

        res = handler.handle(msg)
        assert res.success
        pd = res.result
        assert pd.dbInterfaceIndex == 0
        assert pd.componentID == 7001
        assert pd.entityType == 1
        assert pd.start == 0
        assert pd.end == 32
