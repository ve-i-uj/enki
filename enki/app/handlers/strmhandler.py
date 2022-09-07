"""Stream message handlers."""

import enum
import logging
from dataclasses import dataclass
from typing import Dict, Optional

from enki import descr, kbeenum, kbetype, kbeclient, settings
from enki.misc import devonly

from enki.app.handlers import base

from enki.app import managers

logger = logging.getLogger(__name__)


class StreamDataHandler(base.Handler):

    def __init__(self, stream_data_mgr: managers.StreamDataMgr) -> None:
        self._stream_data_mgr = stream_data_mgr

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'


@dataclass
class OnStreamDataStartedParsedData(base.ParsedMsgData):
    stream_id: int
    datasize: int
    descr: str
    type: kbeenum.DataDownloadType


@dataclass
class OnStreamDataStartedHandlerResult(base.HandlerResult):
    msg_id: int = descr.app.client.onStreamDataStarted.id
    result: OnStreamDataStartedParsedData


class OnStreamDataStartedHandler(StreamDataHandler):

    def handle(self, msg: kbeclient.Message) -> OnStreamDataStartedHandlerResult:
        logger.debug(f'[{self}] ({devonly.func_args_values()})')
        stream_id, datasize, descr, type_code = msg.get_values()
        stream_type = kbeenum.DataDownloadType(type_code)

        self._stream_data_mgr.on_stream_started(
            stream_id, datasize, descr, stream_type
        )

        pd = OnStreamDataStartedParsedData(
            stream_id, datasize, descr, stream_type
        )
        return OnStreamDataStartedHandlerResult(True, pd)


@dataclass
class OnStreamDataRecvParsedData(base.ParsedMsgData):
    stream_id: int
    datasize: int
    data: memoryview


@dataclass
class OnStreamDataRecvHandlerResult(base.HandlerResult):
    msg_id: int = descr.app.client.onStreamDataRecv.id
    result: OnStreamDataRecvParsedData


class OnStreamDataRecvHandler(StreamDataHandler):

    def handle(self, msg: kbeclient.Message) -> OnStreamDataRecvHandlerResult:
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
        return OnStreamDataRecvHandlerResult(True, pd)


@dataclass
class OnStreamDataCompletedParsedData(base.ParsedMsgData):
    stream_id: int


@dataclass
class OnStreamDataCompletedHandlerResult(base.HandlerResult):
    msg_id: int = descr.app.client.onStreamDataCompleted.id
    result: OnStreamDataCompletedParsedData


class OnStreamDataCompletedHandler(StreamDataHandler):

    def handle(self, msg: kbeclient.Message) -> OnStreamDataCompletedHandlerResult:
        logger.debug(f'[{self}] ({devonly.func_args_values()})')
        stream_id = msg.get_values()[0]

        self._stream_data_mgr.on_stream_completed(stream_id)

        pd = OnStreamDataCompletedParsedData(
            stream_id
        )
        return OnStreamDataCompletedHandlerResult(True, pd)
