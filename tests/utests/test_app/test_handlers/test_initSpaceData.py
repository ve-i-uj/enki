import unittest

from enki.net import msgspec
from enki.net import kbeclient

from enki.app.handler.sdhandler import SpaceDataMgr, InitSpaceDataHandler

from tests.utests import base


class InitSpaceDataTestCase(base.EnkiBaseTestCase):
    """Test Client::initSpaceData"""

    def test_ok(self):
        data = b'A\x00\x1f\x00\x01\x00\x00\x00_mapping\x00spaces/xinshoucun\x00'
        msg, data_tail = kbeclient.MessageSerializer(msgspec.app.client.SPEC_BY_ID).deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        handler = InitSpaceDataHandler(SpaceDataMgr())
        result = handler.handle(msg)
        assert result.success
        assert result.result.space_id == 1
        assert result.result.pairs == {'_mapping': 'spaces/xinshoucun'}
