"""???"""

from enki.apps.clientapp.clienthandler import (
    OnCreatedProxiesHandler,
    OnUpdatePropertysHandler,
)

from enki import msgspec
from enki.net.client import MessageEncoder


class OnUpdatePropertysTestCase:
    """Test onUpdatePropertys."""

    async def test_ok(self):
        data = b"\xff\x01\x0e\x00\xf3\x00\x00\x00\x00\x04\x02\x00\x00\x00\x00\x00\x00\x00\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00"
        msg_511, data_tail = MessageEncoder(
            msgspec.client.SPEC_BY_ID
        ).deserialize(memoryview(data))
        data = b"\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00"
        msg_504, _data_tail = MessageEncoder(
            msgspec.client.SPEC_BY_ID
        ).deserialize(memoryview(data))

        assert msg_511 and msg_504, "Invalid initial data"

        handler = OnCreatedProxiesHandler(self._entity_helper)
        result = handler.handle(msg_504)
        assert result.success

        # Есть возможность обновить данные сущности, т.к. она уже была создана
        # и известен её тип
        handler = OnUpdatePropertysHandler(self._entity_helper)
        result = handler.handle(msg_511)
        assert result.success
