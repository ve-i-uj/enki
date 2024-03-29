from enki.net.client import MessageSerializer
from enki.app.clientapp.clienthandler import *

from tests.utests import base


class OnEntityDestroyedTestCase(base.EnkiBaseTestCase):
    """Test Client::onEntityDestroyed"""

    def test_ok(self):
        """Сперва нужно сущность создать потом только уничтожить."""
        self.call_OnCreatedProxies()

        data = b'\x00\x02\x81\x08\x00\x00'
        msg, data_tail = MessageSerializer(msgspec.app.client.SPEC_BY_ID).deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        handler = OnEntityDestroyedHandler(self._entity_helper)
        result = handler.handle(msg)
        assert result.success