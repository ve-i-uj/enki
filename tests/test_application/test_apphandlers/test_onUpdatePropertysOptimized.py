import unittest

from enki.app import handlers, entitymgr, appl
from enki import kbeclient, descr, settings
from enki.interface import IMessage, IMsgReceiver


class OnUpdatePropertysOptimizedTestCase(unittest.TestCase):
    """Test onUpdatePropertysOptimized"""

    def setUp(self):
        super().setUp()
        login_app_addr = settings.AppAddr('0.0.0.0', 20013)
        self._app = appl.App(login_app_addr, server_tick_period=5)
        self._entity_mgr: entitymgr.EntityMgr = entitymgr.EntityMgr(self._app)

    def test_ok(self):
        data = b'\xf8\x01\x13\x00\x00\x00\x07\x00\x95\x84\xfbb\x81\x08\x00\x00Avatar\x00'
        msg_504, _ = kbeclient.Serializer().deserialize(memoryview(data))
        assert msg_504 is not None
        res_504 = handlers.OnCreatedProxiesHandler(self._entity_mgr).handle(msg_504)
        assert res_504.success

        data = b'\x0b\x00\x04\x00\x00\x00\x0e\x03\x0b\x00\x07\x00\x00\x00\t\x18\x00\x00\x00\x18\x00\t\x00\x00\x07\x9fDD^\xcd>D'
        msg, data_tail = kbeclient.Serializer().deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        handler = handlers.OnUpdatePropertysOptimizedHandler(self._entity_mgr)
        result: handlers.HandlerResult = handler.handle(msg)
        assert result.success
        assert result.result.properties == {'modelScale': 3}
