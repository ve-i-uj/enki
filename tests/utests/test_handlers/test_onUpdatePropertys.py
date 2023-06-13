"""???"""

from unittest.mock import MagicMock
from enki.core import msgspec
from enki.net.client import MessageSerializer

from enki.app.clientapp.clienthandler import OnUpdatePropertysHandler, \
    OnCreatedProxiesHandler

from tests.utests.base import EnkiBaseTestCase


class OnUpdatePropertysTestCase(EnkiBaseTestCase):
    """Test onUpdatePropertys"""

    async def test_ok(self):
        data = b'\xff\x01\x0e\x00\xf3\x00\x00\x00\x00\x04\x02\x00\x00\x00\x00\x00\x00\x00\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00'
        msg_511, data_tail = MessageSerializer(msgspec.app.client.SPEC_BY_ID).deserialize(memoryview(data))
        data = b'\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00'
        msg_504, data_tail = MessageSerializer(msgspec.app.client.SPEC_BY_ID).deserialize(memoryview(data))

        assert msg_511 and msg_504, 'Invalid initial data'

        handler = OnCreatedProxiesHandler(self._entity_helper)
        result = handler.handle(msg_504)
        assert result.success

        # Есть возможность обновить данные сущности, т.к. она уже была создана
        # и известен её тип
        handler = OnUpdatePropertysHandler(self._entity_helper)
        result = handler.handle(msg_511)
        assert result.success
