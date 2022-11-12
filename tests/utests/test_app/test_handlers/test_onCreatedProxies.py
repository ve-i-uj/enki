
from unittest.mock import MagicMock

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

        self._app = MagicMock()

        handler = OnCreatedProxiesHandler(self._app, self._app._entity_helper)
        result: HandlerResult = handler.handle(msg_504)
        assert result.success

        # Есть проброс вызова в игровой слой
        assert self._app.game.call_entity_created.call_count == 1
        # Методы компонента на вызываются, т.к. у Account'а нет компонентов
        assert self._app.game.call_component_method.call_count == 0
        # Т.к. нет буферизированных сообщений это сообщение должно было
        # вызываться всего один раз
        assert self._app.on_receive_msg.call_count == 0

    async def test_on_update_and_on_created_proxy(self):
        data = b'\xff\x01\x0e\x00\xf3\x00\x00\x00\x00\x04\x02\x00\x00\x00\x00\x00\x00\x00\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00'
        msg_511, data_tail = MessageSerializer().deserialize(memoryview(data))
        assert msg_511 is not None, 'Invalid initial data'

        handler = OnUpdatePropertysHandler(self._app, self._app._entity_helper)
        result = handler.handle(msg_511)
        assert not result.success, "The message was not added to the bufer"

        data = b'\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00'
        msg_504, data_tail = MessageSerializer().deserialize(memoryview(data))
        assert msg_504 is not None, 'Invalid initial data'


        handler = OnCreatedProxiesHandler(self._app, self._app._entity_helper)
        result: HandlerResult = handler.handle(msg_504)
        assert result.success
