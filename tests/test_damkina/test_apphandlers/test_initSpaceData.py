import unittest

from enki.application import apphandler, entitymgr, appl
from enki import kbeclient, descr, settings
from enki.interface import IMessage, IMsgReceiver


class InitSpaceDataTestCase(unittest.TestCase):
    """Test Client::initSpaceData"""

    def setUp(self):
        super().setUp()
        login_app_addr = settings.AppAddr('0.0.0.0', 20013)
        self._app = appl.App(login_app_addr, server_tick_period=5)
        self._entity_mgr: entitymgr.EntityMgr = entitymgr.EntityMgr(self._app)

    def test_ok(self):
        data = b'A\x00\x1f\x00\x01\x00\x00\x00_mapping\x00spaces/xinshoucun\x00'
        msg, data_tail = kbeclient.Serializer().deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        self._entity_mgr.initialize_entity(203, 'Avatar')
        handler = apphandler.InitSpaceDataHandler()
        result: apphandler.HandlerResult = handler.handle(msg)
        assert result.success
        assert result.result.space_id == 1
        assert result.result.pairs == {'_mapping': 'spaces/xinshoucun'}
