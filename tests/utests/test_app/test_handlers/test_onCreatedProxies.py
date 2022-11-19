
import unittest
from unittest.mock import MagicMock
from enki import layer

from enki.net.kbeclient import MessageSerializer

from enki.app.handler import OnUpdatePropertysHandler, OnCreatedProxiesHandler, \
    HandlerResult

from tests.utests.base import EnkiBaseTestCase



class OnCreatedProxiesTestCase(EnkiBaseTestCase):
    """Test onCreatedProxies"""

    async def test_on_created_proxy_no_components(self):
        data = b'\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00'
        msg_504, data_tail = MessageSerializer().deserialize(memoryview(data))
        assert msg_504 is not None, 'Invalid initial data'

        ehelper = MagicMock()

        handler = OnCreatedProxiesHandler(ehelper)
        result: HandlerResult = handler.handle(msg_504)
        assert result.success

        # Есть проброс вызова в игровой слой
        assert layer.get_game_layer().call_entity_created.call_count == 1
        assert layer.get_game_layer().call_component_method.call_count == 0
        assert ehelper.add_pending_msg.call_count == 0

    async def test_on_update_and_on_created_proxy(self):
        """Ещё до создания сущности приходит сообщение об обновлении свойств.

        Это сообщение нужно сохранить.
        """
        data = b'\xff\x01\x0e\x00\xf3\x00\x00\x00\x00\x04\x02\x00\x00\x00\x00\x00\x00\x00\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00'
        msg_511, data_tail = MessageSerializer().deserialize(memoryview(data))
        assert msg_511 is not None, 'Invalid initial data'

        ehelper = MagicMock()
        ehelper.get_entity_cls_name_by_eid.return_value = False

        handler = OnUpdatePropertysHandler(ehelper)
        result = handler.handle(msg_511)
        assert not result.success, "The message was not added to the bufer"

        # Сообщение добавлено в ожидающие создания сущности
        assert ehelper.add_pending_msg.call_count == 1
        # В игру уведомления не было
        assert layer.get_game_layer().call_entity_created.call_count == 0

        data = b'\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00'
        msg_504, data_tail = MessageSerializer().deserialize(memoryview(data))
        assert msg_504 is not None, 'Invalid initial data'

        handler = OnCreatedProxiesHandler(ehelper)
        result: HandlerResult = handler.handle(msg_504)
        assert result.success

        assert layer.get_game_layer().call_entity_created.call_count == 1
        assert layer.get_game_layer().call_component_method.call_count == 0
        assert ehelper.resend_msgs.call_count == 1

    @unittest.skip('TODO')
    async def test_on_created_proxy_with_components(self):
        """Нужно создать аватара и проверить, что у него нет ошибок при инициализации компонентов."""
        pass
