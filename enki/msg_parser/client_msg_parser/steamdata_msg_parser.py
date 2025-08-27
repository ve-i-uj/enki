"""Обработчики сообщений, связанных с потоком данных от сервера."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, ClassVar, TypeAlias

from enki import msgspec
from enki.kbeenum import DataDownloadType
from enki.kbetype.decoders.basic_data_type_decoders import UINT32
from enki.kbetype.decoders.custom_decoders import (
    KBE_STREAM_ID,
    KBEStreamId,
)
from enki.kbetype.pytypes.basic_data_types import (
    KBEInt8,
    KBERowByteData,
    KBEString,
    KBEUInt32,
)
from enki.misc import devonly
from enki.msg_parser.imsg_parser import IMsgParser, MsgParserResult, ParsedMsgData

if TYPE_CHECKING:
    from enki.msg.message import Message

logger = logging.getLogger(__name__)

PositiveInt: TypeAlias = int

StreamId: TypeAlias = int
StreamSize: TypeAlias = PositiveInt
StreamDescr: TypeAlias = str
StreamChunk: TypeAlias = bytes


class StreamTypeEnum(Enum):
    """Тип потока данных в сообщении Client::onStreamDataStarted ."""

    FILE = 1
    STRING = 2


@dataclass
class OnStreamDataStartedParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Client::onStreamDataStarted."""

    streamId: KBEStreamId  # noqa: N815  # pylint: disable=invalid-name
    totalBytes: KBEUInt32  # noqa: N815  # pylint: disable=invalid-name
    descr: KBEString
    type_code: KBEInt8

    @property
    def stream_id(self) -> StreamId:
        """Получить идентификатор потока.

        Returns:
            StreamId: числовой идентификатор потока данных

        """
        return StreamId(self.streamId)

    @property
    def stream_size(self) -> StreamSize:
        """Получить общий размер данных в потоке.

        Returns:
            StreamSize: размер данных в байтах

        """
        return StreamSize(self.totalBytes)

    @property
    def stream_descr(self) -> StreamDescr:
        """Получить описание потока данных.

        Returns:
            StreamDescr: текстовое описание потока

        """
        return StreamDescr(self.descr)

    @property
    def stream_download_type(self) -> StreamTypeEnum:
        """Получить тип стрима.

        Returns:
            StreamTypeEnum: тип стрима (FILE или STRING)

        """
        dd_type = DataDownloadType(self.type_code)
        return StreamTypeEnum(dd_type.value)

    __add_to_dict__: ClassVar = ("stream_download_type",)


@dataclass(frozen=True)
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
        logger.debug("[%s] (%s)", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        pd = OnStreamDataStartedParsedMsgData(*values)
        return OnStreamDataStartedMsgParserResult(success=True, result=pd)


@dataclass
class OnStreamDataRecvParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Client::onStreamDataRecv."""

    streamId: KBEStreamId  # noqa: N815  # pylint: disable=invalid-name
    datasize: int  # В KBEngine какая-то переменная из curl
    data: KBERowByteData

    @property
    def stream_id(self) -> StreamId:
        """Получить идентификатор потока.

        Returns:
            StreamId: числовой идентификатор потока данных

        """
        return StreamId(self.streamId)

    @property
    def stream_chunk(self) -> StreamChunk:
        """Получить текущий чанк данных потока.

        Returns:
            StreamChunk: байты текущего чанка данных

        """
        return StreamChunk(self.data)


@dataclass(frozen=True)
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
        logger.debug("[%s] (%s)", self, devonly.func_args_values())

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

    stream_id: StreamId


@dataclass(frozen=True)
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
        logger.debug("[%s] (%s)", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        stream_id: KBEStreamId = values[0]

        pd = OnStreamDataCompletedParsedMsgData(stream_id)
        return OnStreamDataCompletedMsgParserResult(success=True, result=pd)
