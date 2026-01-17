"""Агрегатор сетевых пакетов из разных pcap-файлов."""

import logging
from asyncio import CancelledError, Event
from collections import deque
from dataclasses import dataclass
from typing import Self

from enki.misc import devonly
from tools.msgreader.readers.pcap_msg_reader.net_chunk.net_chunk import (
    NetChunkData,
)
from tools.msgreader.readers.pcap_msg_reader.net_chunk.pcap_file_stem import (
    PcapFileStem,
)

logger = logging.getLogger(__name__)


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

    def consume(
        self, pcap_file_stem: PcapFileStem, net_chunk_data: NetChunkData
    ) -> None:
        # component_name - это имя контейнера, в котором запущен KBEngine-компонент
        self._chunks.append(
            PcapFileNetChunkData(pcap_file_stem, net_chunk_data)
        )
        self._new_chunk_event.set()

    def stop(self) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
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
