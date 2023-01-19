"""???"""

from unittest.mock import MagicMock
from enki.net import msgspec
from enki.net.kbeclient import MessageSerializer

from enki.app.handler import OnUpdatePropertysHandler, OnCreatedProxiesHandler

from tests.utests.base import EnkiBaseTestCase


class OnUpdatePropertysTestCase(EnkiBaseTestCase):
    """Test onUpdatePropertys"""

    async def test_ok(self):
        data = b'\xff\x01\x0e\x00\xf3\x00\x00\x00\x00\x04\x02\x00\x00\x00\x00\x00\x00\x00\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00'
        msg_511, data_tail = MessageSerializer(msgspec.app.client.SPEC_BY_ID).deserialize(memoryview(data))
        data = b'\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00'
        msg_504, data_tail = MessageSerializer(msgspec.app.client.SPEC_BY_ID).deserialize(memoryview(data))

        assert msg_511 and msg_504, 'Invalid initial data'

        ehelper = self._entity_helper

        handler = OnCreatedProxiesHandler(ehelper)
        result = handler.handle(msg_504)
        assert result.success

        handler = OnUpdatePropertysHandler(ehelper)
        result = handler.handle(msg_511)
        assert result.success

    async def test_on_update_before_on_created_proxy(self) -> None:
        data = b'\xff\x01\x0e\x00\xf3\x00\x00\x00\x00\x04\x02\x00\x00\x00\x00\x00\x00\x00\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00'
        msg_511, data = MessageSerializer(msgspec.app.client.SPEC_BY_ID).deserialize(memoryview(data))
        msg_504, data_tail = MessageSerializer(msgspec.app.client.SPEC_BY_ID).deserialize(memoryview(data))
        assert msg_511 and msg_504, 'Invalid initial data'

        ehelper = self._entity_helper

        assert not OnUpdatePropertysHandler(ehelper).handle(msg_511).success

        handler = OnCreatedProxiesHandler(self._entity_helper)
        result = handler.handle(msg_504)
        assert result.success
