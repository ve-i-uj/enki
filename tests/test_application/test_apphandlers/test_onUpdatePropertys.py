import unittest

from enki.app import handlers, entitymgr, appl
from enki import kbeclient, descr, settings
from enki.interface import IMessage, IMsgReceiver


class OnUpdatePropertysTestCase(unittest.TestCase):
    """Test onUpdatePropertys"""

    def setUp(self):
        super().setUp()
        login_app_addr = settings.AppAddr('0.0.0.0', 20013)
        self._app = appl.App(login_app_addr, server_tick_period=5)
        self._entity_mgr: entitymgr.EntityMgr = entitymgr.EntityMgr(self._app)

    def test_ok(self):
        data = b'\xff\x01\x0e\x00\x81\x08\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\xf8\x01\x14\x00\x00\x00\x07\x00\x95\x84\xfbb\x81\x08\x00\x00Account\x00'
        msg, data_tail = kbeclient.Serializer().deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        self._entity_mgr.initialize_entity(2177, 'Account')
        handler = handlers.OnUpdatePropertysHandler(self._entity_mgr)
        result: handlers.HandlerResult = handler.handle(msg)
        assert result.success

    def test_on_update_before_on_created_proxy(self):
        data = b'\xff\x01\x0e\x00\xf3\x00\x00\x00\x00\x04\x02\x00\x00\x00\x00\x00\x00\x00\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00'
        msg_511, data = kbeclient.Serializer().deserialize(memoryview(data))
        msg_504, data_tail = kbeclient.Serializer().deserialize(memoryview(data))
        assert msg_511 and msg_504, 'Invalid initial data'

        handlers.OnUpdatePropertysHandler(self._entity_mgr).handle(msg_511)

        handler = handlers.OnCreatedProxiesHandler(self._entity_mgr)
        result: handlers.HandlerResult = handler.handle(msg_504)
        assert result.success
