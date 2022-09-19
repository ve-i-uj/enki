import unittest

from enki.app import handlers, appl
from enki import kbeclient, settings
from enki.app.managers import entitymgr

from tests.utests.base import EnkiBaseTestCase


class OnUpdateData_XZ_Y_TestCase(EnkiBaseTestCase):
    """Test onUpdateData_xy_z"""

    def setUp(self):
        super().setUp()
        self.call_OnCreatedProxies()

    @unittest.skip('Для этого теста нужно сперва onEntityEnterWorld вместо onCreatedProxies')
    def test_ok(self):
        data = b"\x1d\x00\r\x00\x01\xb7'ED\x9c\x15ID\t\xe1\xdb?"
        msg, data_tail = kbeclient.Serializer().deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        entity = self._entity_mgr.initialize_entity(199, 'Avatar')
        self._entity_mgr.set_player(entity.id)

        old_pos = entity.position.clone()
        old_dir = entity.direction.clone()

        handler = handlers.OnUpdateData_XZ_Y_Handler(self._entity_mgr)
        result: handlers.HandlerResult = handler.handle(msg)
        assert result.success

        assert entity.position.x

        # It's updated
        assert old_pos.x != entity.position.x
        assert result.result.x == 788.6205444335938
        assert result.result.x == entity.position.x

        assert old_pos.z != entity.position.z
        assert result.result.z == 804.337646484375
        assert result.result.z == entity.position.z

        # The value is the same
        assert old_pos.y == entity.position.y

        # Direction
        assert old_dir.roll == entity.direction.roll
        assert old_dir.pitch == entity.direction.pitch

        assert old_dir.yaw != entity.direction.yaw
        assert result.result.yaw == 1.717805027961731
        assert result.result.yaw == entity.direction.z
