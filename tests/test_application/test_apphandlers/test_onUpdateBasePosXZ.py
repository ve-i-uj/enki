import unittest

from enki.app import handlers, entitymgr, appl
from enki import kbeclient, settings


class OnUpdateBasePosXZTestCase(unittest.TestCase):
    """Test onUpdateBaseXZPos"""

    def setUp(self):
        super().setUp()
        login_app_addr = settings.AppAddr('0.0.0.0', 20013)
        self._app = appl.App(login_app_addr, server_tick_period=5)
        self._entity_mgr: entitymgr.EntityMgr = entitymgr.EntityMgr(self._app)

    def test_ok(self):
        data = b'\x0f\x00\x81\xe5@D3#BD'
        msg, data_tail = kbeclient.Serializer().deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        entity = self._entity_mgr.initialize_entity(199, 'Avatar')
        self._entity_mgr.set_player(entity.id)

        handler = handlers.OnUpdateBasePosXZHandler(self._entity_mgr)
        result: handlers.HandlerResult = handler.handle(msg)
        assert result.success
        assert result.result.x == 771.5859985351562
        assert result.result.z == 776.5499877929688
