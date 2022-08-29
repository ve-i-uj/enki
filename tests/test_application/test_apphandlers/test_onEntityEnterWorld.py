import unittest
from unittest.mock import MagicMock

from enki.app import handlers, entitymgr, appl
from enki import kbeclient, descr, settings
from enki.interface import IMessage, IMsgReceiver


class OnEntityEnterWorldTestCase(unittest.TestCase):
    """Test Client::onEntityEnterWorld"""

    def setUp(self):
        super().setUp()
        login_app_addr = settings.AppAddr('0.0.0.0', 20013)
        self._app = appl.App(login_app_addr, server_tick_period=5)
        self._entity_mgr: entitymgr.EntityMgr = entitymgr.EntityMgr(self._app)

    def test_ok(self):
        data = b'\xfb\x01\x06\x00\xcb\x00\x00\x00\x02\x00\xff\x01\n\x00\xcb\x00\x00\x00\x00\x05d\x00\x00\x00\xff\x01\n\x00\xcb\x00\x00\x00\x00\x07d\x00\x00\x00'
        msg, data_tail = kbeclient.Serializer().deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        handler = handlers.OnEntityEnterWorldHandler(self._entity_mgr)
        result: handlers.HandlerResult = handler.handle(msg)
        assert result.success
        assert result.result.entity_id == 203
        assert result.result.entity_type_id == 2
        assert not result.result.is_on_ground

        # entity.onEnterWorld.assert_called_once_with()
