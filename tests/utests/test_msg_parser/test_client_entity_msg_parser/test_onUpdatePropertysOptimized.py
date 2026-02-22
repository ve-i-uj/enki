import unittest
from typing import TYPE_CHECKING

from enki import msgspec
from enki.msg.msg_serializer import MessageSerializer
from tests.utests import conftest

if TYPE_CHECKING:
    from enki.msg_parser.imsg_parser import MsgParserResult


class OnUpdatePropertysOptimizedTestCase(conftest.EnkiBaseTestCase):
    """Test onUpdatePropertysOptimized."""

    @unittest.skip(
        "Для этого теста нужно сперва onEntityEnterWorld вместо onCreatedProxies"
    )
    def test_ok(self):
        self.call_OnCreatedProxies()

        handler = OnUpdatePropertysOptimizedHandler(
            self._app, self._entity_helper
        )

        data = b"\x0b\x00\x04\x00\x00\x00\x0e\x03\x0b\x00\x07\x00\x01\x00\t\x18\x00\x00\x00\x18\x00\t\x00\x01\x95\x9cDD\x14\xeaCD"
        msg, _data_tail = MessageSerializer(
            msgspec.ClientMsgSpecByID
        ).deserialize(memoryview(data))
        assert msg is not None, "Invalid initial data"
        result: MsgParserResult = handler.handle(msg)
        assert result.success
        assert result.result.properties == {"modelScale": 3}
