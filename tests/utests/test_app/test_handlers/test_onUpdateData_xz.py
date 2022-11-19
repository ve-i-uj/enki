import unittest

from enki.net import kbeclient

from tests.utests.base import EnkiBaseTestCase


class OnUpdateData_XZ_TestCase(EnkiBaseTestCase):
    """Test onUpdateData_xy"""

    @unittest.skip('Для этого теста нужно сперва onEntityEnterWorld вместо onCreatedProxies')
    def test_ok(self):
        self.call_OnCreatedProxies()

        data = b'\x18\x00\t\x00\x01\x07gED<\x0cID'
        msg, data_tail = kbeclient.Serializer().deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        entity = self._entity_helper.create_entity(199, 'Avatar')

        old_pos = entity.position.clone()
        old_dir = entity.direction.clone()

        handler = handler.OnUpdateData_XZ_Handler(self._entity_helper)
        result: handler.HandlerResult = handler.handle(msg)
        assert result.success

        assert old_pos.x != entity.position.x
        assert result.result.x == 789.6098022460938

        assert old_pos.y == entity.position.y

        assert old_pos.z != entity.position.z
        assert result.result.z == 804.191162109375

        assert old_dir.x == entity.direction.x
        assert old_dir.y == entity.direction.y
        assert old_dir.z == entity.direction.z
