
import unittest
from unittest.mock import MagicMock
from enki.app.clientapp.clienthandler.ehelper import EntityHelper

from enki.app.clientapp.layer import ilayer
from enki.core import msgspec
from enki.net.client import MessageSerializer

from enki.app.clientapp.clienthandler import OnUpdatePropertysHandler, OnCreatedProxiesHandler, \
    HandlerResult

from tests.utests.base import EnkiBaseTestCase
from tests.data import entities, descr


class OnCreatedProxiesTestCase(EnkiBaseTestCase):
    """Test onCreatedProxies"""

    async def test_on_created_proxy_no_components(self):
        data = b'\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00'
        msg_504, data_tail = MessageSerializer(msgspec.app.client.SPEC_BY_ID).deserialize(memoryview(data))
        assert msg_504 is not None, 'Invalid initial data'

        ehelper = MagicMock()

        handler = OnCreatedProxiesHandler(ehelper)
        result: HandlerResult = handler.handle(msg_504)
        assert result.success

        # Есть проброс вызова в игровой слой
        assert ilayer.get_game_layer().call_entity_created.call_count == 1
        assert ilayer.get_game_layer().call_component_method.call_count == 0
        assert ehelper.add_pending_msg.call_count == 0

    @unittest.skip('TODO')
    async def test_on_created_proxy_with_components(self):
        """Нужно создать аватара и проверить, что у него нет ошибок при инициализации компонентов."""
        pass
