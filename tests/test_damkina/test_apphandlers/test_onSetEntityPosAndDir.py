import unittest

from enki.application import apphandler, entitymgr, appl
from enki import kbeclient, descr, settings
from enki.interface import IMessage, IMsgReceiver


class OnSetEntityPosAndDirTestCase(unittest.TestCase):
    """Test onSetEntityPosAndDir"""

    def setUp(self):
        super().setUp()
        login_app_addr = settings.AppAddr('0.0.0.0', 20013)
        self._app = appl.App(login_app_addr, server_tick_period=5)
        self._entity_mgr: entitymgr.EntityMgr = entitymgr.EntityMgr(self._app)

    def test_ok(self):
        data = b'\x0c\x00\x1c\x00\xc7\x00\x00\x00\x81\xe5@D\x83\x00SC3#BD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfd\x01\t\x00\xc7\x00\x00\x00\x01\x00\x00\x00\x00'
        msg, data_tail = kbeclient.Serializer().deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        self._entity_mgr.initialize_entity(199, 'Avatar')
        handler = apphandler.OnSetEntityPosAndDirHandler(self._entity_mgr)
        result: apphandler.HandlerResult = handler.handle(msg)
        assert result.success
        assert result.result.direction.x != 0
        assert result.result.direction.y == 0
        assert result.result.direction.z == 0
        assert result.result.position.x != 0
        assert result.result.position.y != 0
        assert result.result.position.z != 0
