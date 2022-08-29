import unittest

from enki.app import handlers, entitymgr, appl
from enki import kbeclient, descr, settings
from enki.interface import IMessage, IMsgReceiver

from tests import base


class OnUpdatePropertysOptimizedTestCase(base.EnkiTestCaseBase):
    """Test onUpdatePropertysOptimized"""

    def test_ok(self):
        self.call_OnCreatedProxies()

        handler = handlers.OnUpdatePropertysOptimizedHandler(self._entity_mgr)

        data = b'\x0b\x00\x04\x00\x00\x00\x0e\x03\x0b\x00\x07\x00\x01\x00\t\x18\x00\x00\x00\x18\x00\t\x00\x01\x95\x9cDD\x14\xeaCD'
        msg, data_tail = kbeclient.Serializer().deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'
        result: handlers.HandlerResult = handler.handle(msg)
        assert result.success
        assert result.result.properties == {'modelScale': 3}
