import unittest

from enki.app import handlers, appl
from enki import kbeclient, msgspec, settings, interface
from enki.app.managers import entitymgr, sdmgr
from enki.interface import IMessage, IMsgReceiver

from tests.utests import base


class InitSpaceDataTestCase(base.EnkiBaseTestCase):
    """Test Client::initSpaceData"""

    def test_ok(self):
        data = b'A\x00\x1f\x00\x01\x00\x00\x00_mapping\x00spaces/xinshoucun\x00'
        msg, data_tail = kbeclient.Serializer().deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        self._entity_mgr.initialize_entity(203, 'Avatar', True)
        handler = handlers.InitSpaceDataHandler(sdmgr.SpaceDataMgr())
        result: handlers.HandlerResult = handler.handle(msg)
        assert result.success
        assert result.result.space_id == 1
        assert result.result.pairs == {'_mapping': 'spaces/xinshoucun'}
