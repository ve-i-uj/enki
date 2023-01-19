from enki.net.kbeclient import MessageSerializer
from enki.app.handler import *

from tests.utests.base import EnkiBaseTestCase


class OnEntityEnterWorldTestCase(EnkiBaseTestCase):
    """Test Client::onEntityEnterWorld"""

    def test_ok(self):
        self.call_OnCreatedProxies()

        data = b'\xfb\x01\x06\x00\x81\x08\x00\x00\x02\x00\xff\x01\n\x00\xcb\x00\x00\x00\x00\x05d\x00\x00\x00\xff\x01\n\x00\xcb\x00\x00\x00\x00\x07d\x00\x00\x00'
        msg, data_tail = MessageSerializer(msgspec.app.client.SPEC_BY_ID).deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        handler = OnEntityEnterWorldHandler(self._entity_helper)
        result = handler.handle(msg)
        assert result.success
        assert result.result.entity_id == 2177
        assert result.result.entity_type_id == 2
        assert not result.result.is_on_ground

    def test_not_proxy_entity(self):
        data = b'\xfb\x01\x06\x00\x81\x08\x00\x00\x02\x00\xff\x01\n\x00\xcb\x00\x00\x00\x00\x05d\x00\x00\x00\xff\x01\n\x00\xcb\x00\x00\x00\x00\x07d\x00\x00\x00'
        msg, data_tail = MessageSerializer(msgspec.app.client.SPEC_BY_ID).deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        handler = OnEntityEnterWorldHandler(self._entity_helper)
        result = handler.handle(msg)
        assert result.success
        assert result.result.entity_id == 2177
        assert result.result.entity_type_id == 2
        assert not result.result.is_on_ground
