"""Менеджер по работе с сообщениями Client::onStreamData* ."""

import logging
from dataclasses import dataclass
from typing import TypeAlias

from enki.msg_parser.client_msg_parser.steamdata_msg_parser import (
    StreamChunk,
    StreamDescr,
    StreamId,
    StreamSize,
    StreamTypeEnum,
)

logger = logging.getLogger(__name__)

StreamResultData: TypeAlias = bytes


class NoStreamError(Exception):
    """Нет запрошенного стрима."""


@dataclass
class StreamData:
    """Агрегатор данных, приходящих из сообщений Client::onStreamData* ."""

    id: StreamId
    descr: StreamDescr
    datasize: StreamSize
    type: StreamTypeEnum

    result_data: StreamResultData = b""
    is_completed: bool = False


class StreamDataMgr:
    """Менеджер многих стримов в рамках одного клиента."""

    def __init__(self) -> None:
        self._data_by_id: dict[int, StreamData] = {}

    def get_and_delete_stream_data(self, stream_id: StreamId) -> StreamData:
        stream_data = self._data_by_id.get(stream_id)
        if stream_data is None:
            err_text = f"[{self}] There is no stream id '{stream_id}'"
            logger.error(err_text)
            raise NoStreamError(err_text)

        del self._data_by_id[stream_id]
        return stream_data

    def on_stream_started(
        self,
        stream_id: StreamId,
        datasize: StreamSize,
        descr: StreamDescr,
        stream_type: StreamTypeEnum,
    ) -> None:
        self._data_by_id[stream_id] = StreamData(
            stream_id, descr, datasize, stream_type
        )

    def on_data_received(
        self, stream_id: StreamId, stream_chunk: StreamChunk
    ) -> None:
        stream_data = self._data_by_id.get(stream_id)
        if stream_data is None:
            logger.error("[%s] There is no stream id '%s'", self, stream_id)
            return

        stream_data.result_data += stream_chunk

    def on_stream_completed(self, stream_id: StreamId) -> None:
        stream_data = self._data_by_id.get(stream_id)
        if stream_data is None:
            logger.error("[%s] There is no stream id '%s'", self, stream_id)
            return

        stream_data.is_completed = True
