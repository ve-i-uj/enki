from unittest import TestCase

from enki.core import msgspec, utils
from enki.core.kbeenum import ComponentType
from enki.handler import serverhandler
from enki.handler.serverhandler.baseapphandler import OnDbmgrInitCompletedHandlerResult
from tools import msgreader


class OnDbmgrInitCompletedHandlerTestCase(TestCase):

    def test_onBroadcastGlobalDataChanged(self):
        handlers = serverhandler.SERVER_HANDLERS.get('baseapp')
        assert handlers is not None
        handler = handlers.get(
            msgspec.app.baseapp.onDbmgrInitCompleted.id
        )
        assert handler is not None
        str_data = '0d003500830d0000d1070000a10f00000400000001000000393746443130443943333332333339424145353341373635424638453335414100'
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
        assert pd.digest == '97FD10D9C332339BAE53A765BF8E35AA'
