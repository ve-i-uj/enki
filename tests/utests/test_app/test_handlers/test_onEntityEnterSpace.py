import unittest
from unittest.mock import MagicMock

from enki.app import handlers, appl
from enki import kbeclient, msgspec, settings, interface
from enki.app.managers import entitymgr
from enki.interface import IMessage, IMsgReceiver

from tests.utests.base import EnkiBaseTestCase


class OnEntityEnterSpaceTestCase(EnkiBaseTestCase):
    """Test Client::onEntityEnterSpace"""

    def test_ok(self):
        data = b'\xfd\x01\t\x00\xc7\x00\x00\x00\x01\x00\x00\x00\x00'
        msg, data_tail = kbeclient.Serializer().deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        self._entity_mgr.initialize_entity(199, 'Avatar', True)
        entity = self._entity_mgr.get_entity(199)
        entity.onEnterSpace = MagicMock()

        handler = handlers.OnEntityEnterSpaceHandler(self._entity_mgr)
        result: handlers.HandlerResult = handler.handle(msg)
        assert result.success
        assert result.result.entity_id == 199
        assert result.result.space_id == 1
        assert not result.result.is_on_ground

        entity.onEnterSpace.assert_called_once_with()
