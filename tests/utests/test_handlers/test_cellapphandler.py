from unittest import TestCase

from enki.core import msgspec, utils
from enki.core.kbeenum import ComponentType
from enki.core.message import MessageSerializer
from enki.handler import serverhandler
from enki.handler.serverhandler.cellapphandler import OnBroadcastGlobalDataChangedHandlerResult
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
