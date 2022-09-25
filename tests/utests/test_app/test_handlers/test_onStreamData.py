import asyncio
import unittest

from enki.app import handlers, appl
from enki import kbeclient, msgspec, settings, interface
from enki.app.managers import entitymgr, sdmgr
from enki.interface import IMessage, IMsgReceiver
from enki.kbeenum import DataDownloadType

from tests.utests import base


class onStreamDataTestCase(base.EnkiBaseTestCase):
    """Test Client::onStreamData*"""

    async def test_ok(self):
        data_514 = b'\x02\x02\x15\x00\x01\x00\x0e\x00\x00\x00unittest.data\x00\x01'
        msg_514, data_tail = kbeclient.Serializer().deserialize(memoryview(data_514))
        assert msg_514 is not None, 'Invalid initial data'

        data_515 = b'\x03\x02\x14\x00\x01\x00\x0e\x00\x00\x00Unittest data\n'
        msg_515, data_tail = kbeclient.Serializer().deserialize(memoryview(data_515))
        assert msg_515 is not None, 'Invalid initial data'

        data_516 = b'\x04\x02\x01\x00'
        msg_516, data_tail = kbeclient.Serializer().deserialize(memoryview(data_516))
        assert msg_516 is not None, 'Invalid initial data'

        self._app._state = appl._AppStateEnum.CONNECTED
        self._app.on_receive_msg(msg_514)
        self._app.on_receive_msg(msg_515)
        self._app.on_receive_msg(msg_516)

        await asyncio.sleep(1)

        stream_data = self._app._stream_data_mgr._data_by_id[1]

        assert stream_data.id == 1
        assert stream_data.descr == 'unittest.data'
        assert stream_data.type == DataDownloadType.STREAM_FILE
        assert stream_data.get_data() == b'Unittest data\n'