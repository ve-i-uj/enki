"""???"""

import dataclasses
from dataclasses import dataclass

from enki import kbeenum


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
