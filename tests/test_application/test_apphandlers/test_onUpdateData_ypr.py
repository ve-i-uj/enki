import unittest

from enki.app import handlers, appl
from enki import kbeclient, settings
from enki.app.managers import entitymgr

from tests.base import EnkiTestCaseBase


class OnUpdateData_YPR_TestCase(EnkiTestCaseBase):
    """Test onUpdateData_ypr"""

    def setUp(self):
        super().setUp()
        self.call_OnCreatedProxies()

    def test_ok(self):
        self.call_OnCreatedProxies()

        data = b"\x1d\x00\r\x00\x01\xb7'ED\x9c\x15ID\t\xe1\xdb?"
        msg, data_tail = kbeclient.Serializer().deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        entity = self._entity_mgr.initialize_entity(199, 'Avatar')
        self._entity_mgr.set_player(entity.id)

        old_pos = entity.position.clone()
        old_dir = entity.direction.clone()

        handler = handlers.OnUpdateData_YPR_Handler(self._entity_mgr)
        result: handlers.HandlerResult = handler.handle(msg)
        assert result.success

        assert old_pos.x == entity.position.x
        assert old_pos.z == entity.position.z
        assert old_pos.y == entity.position.y

        assert result.result.roll == 1.717805027961731
        assert result.result.roll == entity.direction.roll

        assert result.result.pitch == 804.337646484375
        assert result.result.pitch == entity.direction.pitch

        assert result.result.yaw == 788.6205444335938
        assert result.result.yaw == entity.direction.yaw
