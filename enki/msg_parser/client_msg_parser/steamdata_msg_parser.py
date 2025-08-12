"""Обработчики сообщений, связанных с потоком данных от сервера."""

from enum import Enum
import logging
import dataclasses
from dataclasses import dataclass
from typing import Any, ClassVar, TypeAlias

from enki.kbetype.decoders.basic_data_type_decoders import INT16, UINT32
from enki.kbetype.decoders.custom_decoders import KBE_STREAM_ID, KBERowByteData, KBEStreamId
from enki.kbetype.pytypes.basic_data_types import KBEInt16, KBEInt8, KBEString, \
    KBEUInt32
from enki.misc import devonly
from enki.msg.message import Message
from enki import msgspec

from ..imsg_parser import IMsgParser, MsgParserResult, ParsedMsgData


logger = logging.getLogger(__name__)

class StreamDataDownloadType(Enum):
    """Тип потока данных."""
    
    STREAM_FILE = 1
    STREAM_STRING = 2


@dataclass
class StreamData:
    """Агрегатор данных, приходящих из сообщений Client::onStreamData* .
    
    Заглушка.
    """
    
    id: int
    descr: str
    datasize: int
    type: StreamDataDownloadType

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
    """Менеджер многих стримов в рамках одного клиента."""

    def __init__(self) -> None:
        self._data_by_id: dict[int, StreamData] = {}

    def on_stream_started(self, stream_id: int, datasize: int, descr: str,
                          type: StreamDataDownloadType):
        self._data_by_id[stream_id] = StreamData(stream_id, descr, datasize, type)

    def on_data_received(self, stream_id: int, data: memoryview):
        assert stream_id in self._data_by_id
        stream_data = self._data_by_id[stream_id]
        stream_data.add_chunck(data)

    def on_stream_completed(self, stream_id: int):
        assert stream_id in self._data_by_id
        stream_data = self._data_by_id[stream_id]
        stream_data.on_stop()


# TODO: [2025-08-12 18:50 burov_alexey@mail.ru]:
# Его скорей всего в отделный модуль, где он будет получать уведомления после 
# парсинга и сам с ними работать.
class StreamDataMsgParser(IMsgParser):

    def __init__(self, stream_data_mgr: StreamDataMgr) -> None:
        self._stream_data_mgr = stream_data_mgr

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'


@dataclass
class OnStreamDataStartedParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Client::onStreamDataStarted."""

    streamId: KBEStreamId
    totalBytes: KBEUInt32
    descr: KBEString    
    type_code: KBEInt8
    
    @property
    def stream_download_type(self) -> StreamDataDownloadType:
        """Тип стрима.

        Returns:
            StreamDataDownloadType: тип стрима

        """
        return StreamDataDownloadType(self.type_code)

    __add_to_dict__: ClassVar = ["component_type"]


@dataclass
class OnStreamDataStartedMsgParserResult(MsgParserResult):
    """Результат парсинга Client::onStreamDataStarted."""
    
    success: bool
    msg_id: int = msgspec.client.onStreamDataStarted.id
    result: OnStreamDataStartedParsedMsgData
    text: str = ""


class OnStreamDataStartedMsgParser(IMsgParser):
    """Парсер сообщения Client::onStreamDataStarted."""

    def parse(self, msg: Message) -> OnStreamDataStartedMsgParserResult:
        """Распарсить сообщение Client::onStreamDataStarted.

        Args:
            msg (Message): сообщение Client::onStreamDataStarted

        Returns:
            OnStreamDataStartedMsgParserResult: результат парсинга

        """
        logger.debug(f'[{self}] ({devonly.func_args_values()})')
        
        values: tuple[Any, ...] = msg.get_values()
        pd = OnStreamDataStartedParsedMsgData(*values)
        return OnStreamDataStartedMsgParserResult(success=True, result=pd)


@dataclass
class OnStreamDataRecvParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Client::onStreamDataRecv."""

    streamId: KBEStreamId
    datasize: int  # В KBEngine какая-то переменная из curl
    data: KBERowByteData


@dataclass
class OnStreamDataRecvMsgParserResult(MsgParserResult):
    """Результат парсинга сообщения Client::onStreamDataRecv."""

    msg_id: int = msgspec.client.onStreamDataRecv.id
    result: OnStreamDataRecvParsedMsgData
    

class OnStreamDataRecvMsgParser(IMsgParser):
    """Парсер сообщения Client::onStreamDataRecv."""

    def parse(self, msg: Message) -> OnStreamDataRecvMsgParserResult:
        """Распарсить сообщение Client::onStreamDataRecv.

        Разбирает потоковые данные, включая:
        - ID потока
        - Размер данных
        - Сами данные (чанк)

        Args:
            msg (Message): сообщение Client::onStreamDataRecv

        Returns:
            OnStreamDataRecvMsgParserResult: результат парсинга, содержащий:
                - streamId: идентификатор потока
                - datasize: размер данных в чанке
                - data: сами данные чанка

        Raises:
            AssertionError: если после парсинга остались необработанные данные
        """
        logger.debug(f'[{self}] ({devonly.func_args_values()})')
        
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])
        stream_id, offset = KBE_STREAM_ID.decode(data)
        data = data[offset:]
        datasize, offset = UINT32.decode(data)
        data = data[offset:]

        data_chunk = data[:datasize]
        data = data[datasize:]

        # В сообщении должно быть указано его длина. Поэтому данных не должно 
        # остаться.
        assert not data

        pd = OnStreamDataRecvParsedMsgData(
            stream_id, datasize, KBERowByteData(data_chunk)
        )
        return OnStreamDataRecvMsgParserResult(success=True, result=pd)
    

@dataclass
class OnStreamDataCompletedParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Client::onStreamDataCompleted."""

    stream_id: KBEStreamId


@dataclass
class OnStreamDataCompletedMsgParserResult(MsgParserResult):
    """Результат парсинга сообщения Client::onStreamDataCompleted."""

    msg_id: int = msgspec.client.onStreamDataCompleted.id
    result: OnStreamDataCompletedParsedMsgData


class OnStreamDataCompletedMsgParser(IMsgParser):
    """Парсер сообщения Client::onStreamDataCompleted."""

    def parse(self, msg: Message) -> OnStreamDataCompletedMsgParserResult:
        """Распарсить сообщение Client::onStreamDataCompleted.

        Args:
            msg (Message): сообщение Client::onStreamDataCompleted

        Returns:
            OnStreamDataCompletedMsgParserResult: результат парсинга
            
        """
        logger.debug(f'[{self}] ({devonly.func_args_values()})')
        values: tuple[Any, ...] = msg.get_values()
        stream_id: KBEStreamId = values[0]

        pd = OnStreamDataCompletedParsedMsgData(
            stream_id
        )
        return OnStreamDataCompletedMsgParserResult(success=True, result=pd)