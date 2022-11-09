import unittest
from unittest.mock import MagicMock

from enki.app import handler, appl
from enki import settings
from enki.net import kbeclient, msgspec

from enki.app import ehelper
from enki.interface import IMessage, IMsgReceiver

from tests.utests import base


class OnEntityEnterWorldTestCase(base.EnkiBaseTestCase):
    """Test Client::onEntityEnterWorld"""

    def test_ok(self):
        self.call_OnCreatedProxies()

        data = b'\xfb\x01\x06\x00\x81\x08\x00\x00\x02\x00\xff\x01\n\x00\xcb\x00\x00\x00\x00\x05d\x00\x00\x00\xff\x01\n\x00\xcb\x00\x00\x00\x00\x07d\x00\x00\x00'
        msg, data_tail = kbeclient.MessageSerializer().deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        entity = self._entity_mgr.get_entity(2177)
        entity.onEnterWorld = MagicMock()

        handler = handler.OnEntityEnterWorldHandler(self._entity_mgr)
        result: handler.HandlerResult = handler.handle(msg)
        assert result.success
        assert result.result.entity_id == 2177
        assert result.result.entity_type_id == 2
        assert not result.result.is_on_ground

        entity.onEnterWorld.assert_called_once_with()
