import unittest

from enki.app import handler, appl
from enki import settings
from enki.net import kbeclient, msgspec

from enki.app import ehelper
from enki.interface import IMessage, IMsgReceiver

from tests.utests.base import EnkiBaseTestCase


class OnCreatedProxiesTestCase(EnkiBaseTestCase):
    """Test onCreatedProxies"""

    async def test_on_update_and_on_created_proxy(self):
        data = b'\xff\x01\x0e\x00\xf3\x00\x00\x00\x00\x04\x02\x00\x00\x00\x00\x00\x00\x00\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00'
        msg_511, data_tail = kbeclient.MessageSerializer().deserialize(memoryview(data))
        assert msg_511 is not None, 'Invalid initial data'

        handler = handler.OnUpdatePropertysHandler(self._entity_mgr)
        result: handler.HandlerResult = handler.handle(msg_511)

        data = b'\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00'
        msg_504, data_tail = kbeclient.MessageSerializer().deserialize(memoryview(data))
        assert msg_504 is not None, 'Invalid initial data'

        handler = handler.OnCreatedProxiesHandler(self._entity_mgr)
        result: handler.HandlerResult = handler.handle(msg_504)
        assert result.success
