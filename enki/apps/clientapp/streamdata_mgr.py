"""Менеджер по работе со стримом данных приходящим чанками."""

import logging
from dataclasses import dataclass
from typing import TypeAlias

from enki.kbetype.decoders.custom_decoders import KBEStreamId
from enki.kbetype.pytypes.basic_data_types import (
    KBEString,
    KBEUInt32,
)
from enki.msg_parser.client_msg_parser import (
    StreamTypeEnum,
)

logger = logging.getLogger(__name__)

StreamId: TypeAlias = KBEStreamId
StreamDescr: TypeAlias = KBEString
StreamSize: TypeAlias = KBEUInt32
StreamChunk: TypeAlias = bytes
StreamResultData: TypeAlias = bytes


class NoStreamError(Exception):
    """Исключение, возникающее при отсутствии запрошенного стрима."""


@dataclass
class StreamData:
    """Агрегатор данных, приходящий чанками.

    Attributes:
        id: Идентификатор потока данных
        descr: Описание потока данных
        datasize: Общий размер данных потока в байтах
        type: Тип потока данных (FILE или STRING)
        result_data: Накопленные данные потока
        is_completed: Флаг завершения потока

    """

    id: StreamId
    descr: StreamDescr
    datasize: StreamSize
    type: StreamTypeEnum

    result_data: StreamResultData = StreamResultData(b"")
    is_completed: bool = False


class StreamDataMgr:
    """Менеджер для работы с несколькими потоками данных в рамках одного клиента.

    Обеспечивает:
    - Хранение данных всех активных потоков
    - Обработку событий начала/получения данных/завершения потоков
    - Удаление завершенных потоков
    """

    def __init__(self) -> None:
        """Инициализирует менеджер потоков данных."""
        self._data_by_id: dict[int, StreamData] = {}

    def get_and_delete_stream_data(self, stream_id: StreamId) -> StreamData:
        """Получить и удалить данные потока по его идентификатору.

        Args:
            stream_id: Идентификатор потока данных

        Returns:
            StreamData: Данные запрошенного потока

        Raises:
            NoStreamError: Если поток с указанным идентификатором не найден

        """
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
        """Обработать событие начала нового потока данных.

        Args:
            stream_id: Идентификатор нового потока
            datasize: Ожидаемый размер данных потока
            descr: Описание потока
            stream_type: Тип потока (FILE или STRING)

        """
        self._data_by_id[stream_id] = StreamData(
            stream_id, descr, datasize, stream_type
        )

    def on_data_received(
        self, stream_id: StreamId, stream_chunk: StreamChunk
    ) -> None:
        """Обработать получение части данных потока.

        Args:
            stream_id: Идентификатор потока
            stream_chunk: Полученная часть данных

        """
        stream_data = self._data_by_id.get(stream_id)
        if stream_data is None:
            logger.error("[%s] There is no stream id '%s'", self, stream_id)
            return

        stream_data.result_data += stream_chunk

    def on_stream_completed(self, stream_id: StreamId) -> None:
        """Обработать событие завершения потока данных.

        Args:
            stream_id: Идентификатор завершенного потока

        """
        stream_data = self._data_by_id.get(stream_id)
        if stream_data is None:
            logger.error("[%s] There is no stream id '%s'", self, stream_id)
            return

        stream_data.is_completed = True
