from unittest import TestCase

from enki.core import msgspec, utils
from enki.core.kbeenum import ComponentType
from enki.core.message import MessageSerializer
from enki.handler import serverhandler
from enki.handler.serverhandler.cellapphandler import OnBroadcastGlobalDataChangedHandlerResult, OnCreateCellEntityFromBaseappHandler
from tools import msgreader


class OnBroadcastGlobalDataChangedHandlerTestCase(TestCase):

    def test_onBroadcastGlobalDataChanged(self):
        handlers = serverhandler.SERVER_HANDLERS.get('cellapp')
        assert handlers is not None
        handler = handlers.get(
            msgspec.app.cellapp.onBroadcastGlobalDataChanged.id
        )
        assert handler is not None
        str_data = '0e004500000c000000565370616365730a70300a2e30000000635f7570660a456e7469747943616c6c0a70300a2849323030310a49373030310a49380a49310a7470310a5270320a2e'
        data = msgreader.normalize_wireshark_data(str_data)
        serializer = utils.get_serializer_for(ComponentType.CELLAPP)
        msg, data_tail = serializer.deserialize(memoryview(data))
        assert not data_tail
        assert msg is not None

        res: OnBroadcastGlobalDataChangedHandlerResult = handler().handle(msg) # type: ignore
        assert res.success
        assert not res.result.isDelete
        assert res.result.key == 'Spaces'
        assert res.result.value is not None


class OnCreateCellEntityFromBaseappHandlerTestCase(TestCase):

    def test_onBroadcastGlobalDataChanged(self):
        handler = OnCreateCellEntityFromBaseappHandler()
        str_data = '13007600d3070000537061776e506f696e7400d4070000591b00000000000000000000409c1cdccdc200003f4308ec16c30000419c00000000000000000000000000004000000000000000000000002ea00000000000002fa00100002ba00000000000003e00e903000000002ca00000000000002da000000000'
        data = msgreader.normalize_wireshark_data(str_data)
        serializer = utils.get_serializer_for(ComponentType.CELLAPP)
        msg, data_tail = serializer.deserialize(memoryview(data))
        assert not data_tail
        assert msg is not None

        res = handler.handle(msg) # type: ignore
        assert res.success
        pd = res.result
        assert pd.componentID == 7001
        assert pd.createToEntityID == 2003
        assert pd.entityID == 2004
        assert pd.entityType == 'SpawnPoint'
        assert pd.hasClient == False
        assert pd.inRescore == False
