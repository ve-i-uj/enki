import unittest

from enki.application import apphandler, entitymgr, appl
from enki import kbeclient, settings


class OnUpdateData_XZ_TestCase(unittest.TestCase):
    """Test onUpdateData_xy"""

    def setUp(self):
        super().setUp()
        login_app_addr = settings.AppAddr('0.0.0.0', 20013)
        self._app = appl.App(login_app_addr, server_tick_period=5)
        self._entity_mgr: entitymgr.EntityMgr = entitymgr.EntityMgr(self._app)

    def test_ok(self):
        data = b'\x18\x00\t\x00\x01\x07gED<\x0cID'
        msg, data_tail = kbeclient.Serializer().deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        entity = self._entity_mgr.initialize_entity(199, 'Avatar')
        self._entity_mgr.set_player(entity.id)

        old_pos = entity.position.clone()
        old_dir = entity.direction.clone()

        handler = apphandler.OnUpdateData_XZ_Handler(self._entity_mgr)
        result: apphandler.HandlerResult = handler.handle(msg)
        assert result.success

        assert entity.position.x

        # It's updated
        assert old_pos.x != entity.position.x
        assert result.result.x == 3696.437744140625
        assert result.result.x == entity.position.x

        assert old_pos.z != entity.position.z
        assert result.result.z == 574404.25
        assert result.result.z == entity.position.z

        # The value is the same
        assert old_pos.y == entity.position.y

        # Direction
        assert old_dir.x == entity.direction.x
        assert old_dir.y == entity.direction.y
        assert old_dir.z == entity.direction.z
