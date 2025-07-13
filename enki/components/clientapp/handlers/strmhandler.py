"""Stream message handlers."""

import logging
import dataclasses
from dataclasses import dataclass

from enki.misc import devonly
from enki import kbeenum
from enki.core import kbetype
from enki.core.message import Message
from enki.core import msgspec
from enki.handlers.base import Handler, MsgResult, ParsedMsgInfo


logger = logging.getLogger(__name__)


@dataclass
class StreamData:
    id: int
    descr: str
    datasize: int
    type: kbeenum.DataDownloadType

    _ready: bool = False
    _chuncks: list[memoryview] = dataclasses.field(default_factory=list)
    _data: bytes = b''

    def add_chunck(self, data: memoryview):
        self._chuncks.append(data)

    def on_stop(self):
        self._ready = True
        data = self.get_data()
        assert len(data) == self.datasize

    def get_data(self):
        assert self._ready
        if not self._data:
            self._data = b''.join(mv.tobytes() for mv in self._chuncks)
            self._chuncks[:] = []
        return self._data


class StreamDataMgr:

    def __init__(self) -> None:
        self._data_by_id: dict[int, StreamData] = {}

    def on_stream_started(self, stream_id: int, datasize: int, descr: str,
                          type: kbeenum.DataDownloadType):
        self._data_by_id[stream_id] = StreamData(stream_id, descr, datasize, type)

    def on_data_received(self, stream_id: int, data: memoryview):
        assert stream_id in self._data_by_id
        stream_data = self._data_by_id[stream_id]
        stream_data.add_chunck(data)

    def on_stream_completed(self, stream_id: int):
        assert stream_id in self._data_by_id
        stream_data = self._data_by_id[stream_id]
        stream_data.on_stop()


class StreamDataMsgParser(IMsgParser):

    def __init__(self, stream_data_mgr: StreamDataMgr) -> None:
        self._stream_data_mgr = stream_data_mgr

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'


@dataclass
class OnStreamDataStartedParsedData(ParsedMsgInfo):
    stream_id: int
    datasize: int
    descr: str
    type: kbeenum.DataDownloadType


@dataclass
class OnStreamDataStartedHandlerResult(MsgResult):
    msg_id: int = msgspec.app.client.onStreamDataStarted.id
    result: OnStreamDataStartedParsedData


class OnStreamDataStartedHandler(StreamDataHandler):

    def parse(self, msg: Message) -> OnStreamDataStartedMsgResult:
        logger.debug(f'[{self}] ({devonly.func_args_values()})')
        stream_id, datasize, descr, type_code = msg.get_values()
        stream_type = kbeenum.DataDownloadType(type_code)

        self._stream_data_mgr.on_stream_started(
            stream_id, datasize, descr, stream_type
        )

        pd = OnStreamDataStartedParsedData(
            stream_id, datasize, descr, stream_type
        )
        return OnStreamDataStartedMsgResult(True, pd)


@dataclass
class OnStreamDataRecvParsedData(ParsedMsgInfo):
    stream_id: int
    datasize: int
    data: memoryview


@dataclass
class OnStreamDataRecvHandlerResult(MsgResult):
    msg_id: int = msgspec.app.client.onStreamDataRecv.id
    result: OnStreamDataRecvParsedData


class OnStreamDataRecvHandler(StreamDataHandler):

    def parse(self, msg: Message) -> OnStreamDataRecvMsgResult:
        logger.debug(f'[{self}] ({devonly.func_args_values()})')
        data: memoryview = msg.get_values()[0]
        stream_id, offset = kbetype.INT16.decode(data)
        data = data[offset:]
        datasize, offset = kbetype.UINT32.decode(data)
        data = data[offset:]

        data = data[:datasize]

        self._stream_data_mgr.on_data_received(stream_id, data)

        pd = OnStreamDataRecvParsedData(
            stream_id, datasize, data
        )
        return OnStreamDataRecvMsgResult(True, pd)


@dataclass
class OnStreamDataCompletedParsedData(ParsedMsgInfo):
    stream_id: int


@dataclass
class OnStreamDataCompletedHandlerResult(MsgResult):
    msg_id: int = msgspec.app.client.onStreamDataCompleted.id
    result: OnStreamDataCompletedParsedData


class OnStreamDataCompletedHandler(StreamDataHandler):

    def parse(self, msg: Message) -> OnStreamDataCompletedMsgResult:
        logger.debug(f'[{self}] ({devonly.func_args_values()})')
        stream_id = msg.get_values()[0]

        self._stream_data_mgr.on_stream_completed(stream_id)

        pd = OnStreamDataCompletedParsedData(
            stream_id
        )
        return OnStreamDataCompletedMsgResult(True, pd)
