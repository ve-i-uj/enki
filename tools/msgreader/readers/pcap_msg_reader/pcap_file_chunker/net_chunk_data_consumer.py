"""Агрегатор сетевых пакетов из разных pcap-файлов."""

import logging
from asyncio import CancelledError, Event
from collections import deque
from dataclasses import dataclass
from typing import Self, TypeAlias

from tools.msgreader.readers.pcap_msg_reader.pcap_file_chunker.net_chunk_data import (
    NetChunkData,
)

logger = logging.getLogger(__name__)

PcapFileStem: TypeAlias = str


@dataclass
class PcapFileNetChunkData:
    pcap_file_stem: PcapFileStem
    net_chunk_data: NetChunkData


class NetChunkDataConsumer:
    """Сервис агрегирует данные сетевых пакетов с KBEngine-сообщениями."""

    def __init__(self) -> None:
        self._chunks: deque[PcapFileNetChunkData] = deque()
        self._new_chunk_event = Event()

        self._stopped = False

    def consume(self, component_name: PcapFileStem, net_chunk_data: NetChunkData) -> None:
        # component_name - это имя контейнера, в котором запущен KBEngine-компонент
        self._chunks.append(PcapFileNetChunkData(component_name, net_chunk_data))

    def stop_consume(self) -> None:
        self._stopped = True
        # Чтобы высвободить из wait в __anext__
        self._new_chunk_event.set()

    def __aiter__(self) -> Self:
        return self

    async def __anext__(self) -> PcapFileNetChunkData:
        if self._chunks:
            return self._chunks.popleft()

        if self._stopped:
            raise StopAsyncIteration

        # Все ответы обработаны. Очищаем событие
        self._new_chunk_event.clear()

        try:
            # Ожидаем, когда придут новые данные
            await self._new_chunk_event.wait()
        except CancelledError as err:
            logger.info(
                "[%s] No response. Waiting was canceled",
                self,
            )
            raise StopAsyncIteration from err

        return await self.__anext__()
