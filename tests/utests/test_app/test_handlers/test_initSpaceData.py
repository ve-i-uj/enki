import unittest

from enki.app import ehelper, handler, appl
from enki import settings
from enki.net import kbeclient, msgspec

from enki.app.manager import sdmgr
from enki.interface import IMessage, IMsgReceiver

from tests.utests import base


class InitSpaceDataTestCase(base.EnkiBaseTestCase):
    """Test Client::initSpaceData"""

    def test_ok(self):
        data = b'A\x00\x1f\x00\x01\x00\x00\x00_mapping\x00spaces/xinshoucun\x00'
        msg, data_tail = kbeclient.MessageSerializer().deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        self._entity_helper.create_entity(203, 'Avatar', True)
        handler = handler.InitSpaceDataHandler(sdmgr.SpaceDataMgr())
        result: handler.HandlerResult = handler.handle(msg)
        assert result.success
        assert result.result.space_id == 1
        assert result.result.pairs == {'_mapping': 'spaces/xinshoucun'}
