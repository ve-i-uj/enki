import unittest

from enki.app.handler.ehandler import OnUpdatePropertysOptimizedHandler
from enki.app.handler.base import HandlerResult
from enki.net import kbeclient, msgspec

from enki import settings
from enki.net import kbeclient, msgspec

from enki.app import ehelper

from tests.utests import base


class OnUpdatePropertysOptimizedTestCase(base.EnkiBaseTestCase):
    """Test onUpdatePropertysOptimized"""

    @unittest.skip('Для этого теста нужно сперва onEntityEnterWorld вместо onCreatedProxies')
    def test_ok(self):
        self.call_OnCreatedProxies()

        handler = OnUpdatePropertysOptimizedHandler(self._app, self._entity_helper)

        data = b'\x0b\x00\x04\x00\x00\x00\x0e\x03\x0b\x00\x07\x00\x01\x00\t\x18\x00\x00\x00\x18\x00\t\x00\x01\x95\x9cDD\x14\xeaCD'
        msg, data_tail = kbeclient.MessageSerializer().deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'
        result: HandlerResult = handler.handle(msg)
        assert result.success
        assert result.result.properties == {'modelScale': 3}
