
from enki.app.client.clienthandler.sdhandler import (
    InitSpaceDataHandler,
    SpaceDataMgr,
)
from enki.core import msgspec
from enki.net import client
from tests.utests import base


class InitSpaceDataTestCase(base.EnkiBaseTestCase):
    """Test Client::initSpaceData"""

    def test_ok(self):
        data = b"A\x00\x1f\x00\x01\x00\x00\x00_mapping\x00spaces/xinshoucun\x00"
        msg, data_tail = client.MessageEncoder(msgspec.client.SPEC_BY_ID).deserialize(memoryview(data))
        assert msg is not None, "Invalid initial data"

        handler = InitSpaceDataHandler(SpaceDataMgr())
        result = handler.handle(msg)
        assert result.success
        assert result.result.space_id == 1
        assert result.result.pairs == {"_mapping": "spaces/xinshoucun"}
