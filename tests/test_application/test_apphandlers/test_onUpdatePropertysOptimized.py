import unittest

from enki.application import apphandler, entitymgr, appl
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
        data = b'\x0b\x00\x04\x00\x00\x00\x0e\x03\x0b\x00\x07\x00\x00\x00\t\x18\x00\x00\x00\x18\x00\t\x00\x00\x07\x9fDD^\xcd>D'
        msg, data_tail = kbeclient.Serializer().deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        self._entity_mgr.add_entity_id_by_alias_id(204)
        self._entity_mgr.initialize_entity(204, 'Avatar')
        handler = apphandler.OnUpdatePropertysOptimizedHandler(self._entity_mgr)
        result: apphandler.HandlerResult = handler.handle(msg)
        assert result.success
        assert result.result.properties == {'modelScale': 3}
