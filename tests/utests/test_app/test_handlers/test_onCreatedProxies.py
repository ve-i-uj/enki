import unittest

from enki.app import handlers, appl
from enki import kbeclient, msgspec, settings, interface
from enki.app.managers import entitymgr
from enki.interface import IMessage, IMsgReceiver

from tests.utests.base import EnkiBaseTestCase


class OnCreatedProxiesTestCase(EnkiBaseTestCase):
    """Test onCreatedProxies"""

    async def test_on_update_and_on_created_proxy(self):
        data = b'\xff\x01\x0e\x00\xf3\x00\x00\x00\x00\x04\x02\x00\x00\x00\x00\x00\x00\x00\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00'
        msg_511, data_tail = kbeclient.Serializer().deserialize(memoryview(data))
        assert msg_511 is not None, 'Invalid initial data'

        handler = handlers.OnUpdatePropertysHandler(self._entity_mgr)
        result: handlers.HandlerResult = handler.handle(msg_511)

        data = b'\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00'
        msg_504, data_tail = kbeclient.Serializer().deserialize(memoryview(data))
        assert msg_504 is not None, 'Invalid initial data'

        handler = handlers.OnCreatedProxiesHandler(self._entity_mgr)
        result: handlers.HandlerResult = handler.handle(msg_504)
        assert result.success
