from enki.net.kbeclient import MessageSerializer
from enki.app.handler import *

from tests.utests.base import EnkiBaseTestCase


class OnRemoteMethodCallHandlerTestCase(EnkiBaseTestCase):
    """Test onRemoteMethodCallHandler"""

    def test_ok(self):
        # Account, 2178
        data = b'\xf8\x01\x14\x00\x00\x00\x07\x00\x95\x84\xfbb\x82\x08\x00\x00Account\x00'
        msg_504, _ = MessageSerializer().deserialize(memoryview(data))
        assert msg_504 is not None
        assert OnCreatedProxiesHandler(self._entity_helper).handle(msg_504).success

        data = b'\xfa\x01^\x00\x82\x08\x00\x00\x00\x03\x03\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x07\x00\x00\x00Damkina\x01\x01\x00\x01\x01\x00\x00\x001\x02\x00\x00\x00\x00\x00\x00\x00\x07\x00\x00\x00Damkina\x01\x01\x00\x01\x01\x00\x00\x001\x03\x00\x00\x00\x00\x00\x00\x00\x07\x00\x00\x00Damkina\x01\x01\x00\x01\x01\x00\x00\x001'
        msg_506, data_tail = MessageSerializer().deserialize(memoryview(data))
        assert msg_506 is not None, 'Invalid initial data'

        handler = OnRemoteMethodCallHandler(self._entity_helper)
        result = handler.handle(msg_506)
        assert result.success


    def test_component(self):
        """Вызов удалённого метода приходит для компонента (т.е. у свойства вызывается)."""
        self.call_OnCreatedProxies()

        data = b'\xfa\x01\n\x00\x81\x08\x00\x00\n\x01\t\x03\x00\x00\xff\x01 \x00\x84\x08\x00\x00\x00\x01\x81\xe5@D\x83\x00SC3#BD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfb\x01\x06\x00\x84\x08\x00\x00\x02\x00\xff\x01\n\x00\x84\x08\x00\x00\x00\x05d\x00\x00\x00\xff\x01\n\x00\x84\x08\x00\x00\x00\x07d\x00\x00\x00'
        msg_506, data = kbeclient.MessageSerializer().deserialize(memoryview(data))
        assert msg_506 is not None, 'Invalid initial data'

        handler = OnRemoteMethodCallHandler(self._entity_helper)
        result = handler.handle(msg_506)
        assert result.success
        assert result.result.method_name == 'helloCB'
