from enki.net.client import MessageSerializer
from enki.app.clientapp.clienthandler import *

from tests.utests.base import EnkiBaseTestCase


class OnUpdateBasePosXZTestCase(EnkiBaseTestCase):
    """Test onUpdateBaseXZPos"""

    def test_ok(self):
        self.call_OnCreatedProxies()

        data = b'\x0f\x00\x81\xe5@D3#BD'
        msg, data_tail = MessageSerializer(msgspec.app.client.SPEC_BY_ID).deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        handler = OnUpdateBasePosXZHandler(self._entity_helper)
        result = handler.handle(msg)
        assert result.success
        assert result.result.x == 771.5859985351562
        assert result.result.z == 776.5499877929688
