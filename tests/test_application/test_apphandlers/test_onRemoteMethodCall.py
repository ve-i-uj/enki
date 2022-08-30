import unittest

from enki.app import handlers, appl
from enki import kbeclient, descr, settings, kbetype
from enki.app.managers import entitymgr
from enki.interface import IMessage, IMsgReceiver


class OnRemoteMethodCallHandlerTestCase(unittest.TestCase):
    """Test onRemoteMethodCallHandler"""

    def setUp(self):
        super().setUp()
        login_app_addr = settings.AppAddr('0.0.0.0', 20013)
        self._app = appl.App(login_app_addr, server_tick_period=5)
        self._entity_mgr: entitymgr.EntityMgr = entitymgr.EntityMgr(self._app)

    def test_ok(self):
        data = b'\xfa\x01\n\x00\xbf\x00\x00\x00\x00\x03\x00\x00\x00\x00'
        msg, data_tail = kbeclient.Serializer().deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        data = msg.get_values()[0]
        entity_id, _ = kbetype.ENTITY_ID.decode(data)
        assert entity_id == 191
        self._entity_mgr.initialize_entity(entity_id, 'Account', True)

        handler = handlers.OnRemoteMethodCallHandler(self._entity_mgr)
        result: handlers.HandlerResult = handler.handle(msg)
        assert result.success

    def test_component(self):
        """Вызов удалённого метода приходит для компонента (т.е. у свойства вызывается)."""
        data = b'\xfa\x01\n\x00\x84\x08\x00\x00\n\x01\t\x03\x00\x00\xff\x01 \x00\x84\x08\x00\x00\x00\x01\x81\xe5@D\x83\x00SC3#BD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfb\x01\x06\x00\x84\x08\x00\x00\x02\x00\xff\x01\n\x00\x84\x08\x00\x00\x00\x05d\x00\x00\x00\xff\x01\n\x00\x84\x08\x00\x00\x00\x07d\x00\x00\x00'
        msg, data = kbeclient.Serializer().deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        mst_data = msg.get_values()[0]
        entity_id, _ = kbetype.ENTITY_ID.decode(mst_data)
        assert entity_id == 2180
        self._entity_mgr.initialize_entity(entity_id, 'Avatar' , True)

        handler = handlers.OnRemoteMethodCallHandler(self._entity_mgr)
        result: handlers.HandlerResult = handler.handle(msg)
        assert result.success
        assert result.result.method_name == 'helloCB'
