from unittest.mock import MagicMock

from enki import kbeenum
from enki.net.kbeclient import MessageSerializer
from enki.app.handler import *

from enki.app.handler.strmhandler import StreamDataMgr

from tests.utests.base import EnkiBaseTestCase


class onStreamDataTestCase(EnkiBaseTestCase):
    """Test Client::onStreamData*"""

    async def test_ok(self):
        data_514 = b'\x02\x02\x15\x00\x01\x00\x0e\x00\x00\x00unittest.data\x00\x01'
        msg_514, data_tail = MessageSerializer().deserialize(memoryview(data_514))
        assert msg_514 is not None, 'Invalid initial data'

        data_515 = b'\x03\x02\x14\x00\x01\x00\x0e\x00\x00\x00Unittest data\n'
        msg_515, data_tail = MessageSerializer().deserialize(memoryview(data_515))
        assert msg_515 is not None, 'Invalid initial data'

        data_516 = b'\x04\x02\x01\x00'
        msg_516, data_tail = MessageSerializer().deserialize(memoryview(data_516))
        assert msg_516 is not None, 'Invalid initial data'


        stream_data_mgr = StreamDataMgr()

        res = OnStreamDataStartedHandler(stream_data_mgr).handle(msg_514)
        assert res.success

        res = OnStreamDataRecvHandler(stream_data_mgr).handle(msg_515)
        assert res.success

        res = OnStreamDataCompletedHandler(stream_data_mgr).handle(msg_516)
        assert res.success

        stream_data = stream_data_mgr._data_by_id[1]

        assert stream_data.id == 1
        assert stream_data.descr == 'unittest.data'
        assert stream_data.type == kbeenum.DataDownloadType.STREAM_FILE
        assert stream_data.get_data() == b'Unittest data\n'
