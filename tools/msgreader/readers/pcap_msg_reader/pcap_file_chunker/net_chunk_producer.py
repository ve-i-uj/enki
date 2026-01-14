"""Сервис, производящий из pcap-файла чанки с данными сетевых пакетов."""

from __future__ import annotations

import asyncio
import logging
from asyncio import CancelledError, Event, Future, Task
from collections import deque
from typing import TYPE_CHECKING

from .online_pcap_file_reader import (
    NetChunkData,
    OnlinePcapFileReader,
)
from .pcap_file_stem import (
    PcapFileStem,
)

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


class Pcap2NetChunkDataProducerCancelledExeption(Exception):
    """Исключение, возникающее при отмене операции получения или ожидания чанка.

    Это исключение выбрасывается, когда операция получения сетевого чанка (produce)
    была отменена (например, из-за CancelledError). Обычно это происходит при
    остановке или прерывании работы сервиса во время ожидания новых данных.

    Attributes:
        message: Описание ошибки (наследуется от базового класса Exception)

    """


class Pcap2NetChunkDataProducerIsNotStartedExeption(Exception):
    """Исключение, возникающее при попытке использования не запущенного сервиса.

    Это исключение выбрасывается, когда вызываются методы stop() или produce()
    до того, как сервис был запущен с помощью метода start(). Гарантирует, что
    сервис будет использоваться только в правильном состоянии.

    Attributes:
        message: Описание ошибки (наследуется от базового класса Exception)

    """


class Pcap2NetChunkDataProducer:
    """Сервис читает pcap-файл и производит данные, представляющие сетевой пакет."""

    def __init__(self, pcap_file_path: Path) -> None:
        """Конструктор.

        Args:
            pcap_file_path: путь до pcap-файла с KBEngine-сообщениями

        """
        assert (
            pcap_file_path.is_file() and pcap_file_path.suffix == ".pcap"
        ), "The path should be a pcap-file"
        self._pcap_file_path = pcap_file_path

        # Проверка на формат имени файла
        assert PcapFileStem.validate(pcap_file_path.stem)
        self._pcap_file_stem = PcapFileStem(pcap_file_path.stem)

        # Событие для оповещния, что есть новый чанк из файла
        # В начале нет никаких чанков, поэтому получается, что сразу в ожидании
        self._new_net_chunk_data_event = Event()
        # Очередь с новыми чанками
        self._chunks: deque[NetChunkData] = deque()

        # Флаг состояния объекта (запущен или нет)
        self._started = False
        self._stopped = False

        # Собственно сам рабочий объект, читающий файл и производящий чанки
        self._pcap_to_stream_obj: OnlinePcapFileReader | None = None
        # Задача, из которой приходят чанки
        self._receive_chunks_task: Task | None = None

        # Для оповещении, что объект остановлен и финизилирован
        self._is_finilized_future: Future[None] = Future()

    @property
    def pcap_file_stem(self) -> PcapFileStem:
        return self._pcap_file_stem

    @property
    def is_started(self) -> bool:
        return not self._is_finilized_future.done()

    async def start(self) -> None:
        if self._started:
            logger.warning(
                "[%s] The producer is already started. Logic error", self
            )
            return

        if self._stopped:
            logger.warning(
                "[%s] The producer has been already started and stopped", self
            )
            return

        self._pcap_to_stream_obj = OnlinePcapFileReader(self._pcap_file_path)
        # Объект итератор и внутри есть своя очередь. Поэтому при старте чанки
        # начнут в нём копиться, но отдаваться будут только при запуске цикла.
        await self._pcap_to_stream_obj.start()

        async def receive_chunks() -> None:
            """Задача, производящая чанки."""
            assert self._pcap_to_stream_obj is not None
            async for net_chunk_data in self._pcap_to_stream_obj:
                self._chunks.append(net_chunk_data)
                self._new_net_chunk_data_event.set()

        self._receive_chunks_task = asyncio.create_task(receive_chunks())

        self._started = True
        logger.debug("[%s] The chunk iteration has been started", self)

    async def produce(self) -> NetChunkData | None:
        if not self._started:
            logger.debug("[%s] The iteration of chunks is not started", self)
            raise Pcap2NetChunkDataProducerIsNotStartedExeption

        # Если есть чанки, то сразу их возвращаем
        if self._chunks:
            logger.debug("[%s] There is a new net chunk data. Return", self)
            return self._chunks.popleft()

        # Чанков больше нет и продюсер останавливается. Возвращаем None, чтобы
        # сказать об этом
        if self._stopped:
            logger.debug(
                "[%s] The producer has been stopped and it has no chunks", self
            )
            self._is_finilized_future.set_result(None)
            return None

        # Все чанки отданы. Очищаем событие, чтобы ниже в wait была блокировка
        self._new_net_chunk_data_event.clear()

        try:
            # Ожидаем, когда придут новые данные
            logger.debug("[%s] There is no new net chunk data. Wait", self)
            await self._new_net_chunk_data_event.wait()
        except CancelledError:
            logger.info(
                "[%s] Chunk getting was canceled",
                self,
            )
            await self.stop()
            raise Pcap2NetChunkDataProducerCancelledExeption

        return await self.produce()

    async def stop(self) -> None:
        if not self._started:
            logger.warning("[%s] The producing of chunks is not started", self)
            raise Pcap2NetChunkDataProducerIsNotStartedExeption

        if self._stopped:
            logger.warning(
                "[%s] The producer is arleady stopped. Logic error", self
            )
            return

        if (
            self._pcap_to_stream_obj is not None
            and self._pcap_to_stream_obj.is_started
        ):
            await self._pcap_to_stream_obj.stop()
            await self._pcap_to_stream_obj.wait_until_stop()

            self._pcap_to_stream_obj = None

        if self._receive_chunks_task is not None:
            # Нужно дождаться завершения производства чанков (цикла async for)
            await self._receive_chunks_task
            self._receive_chunks_task = None

        # Чтобы высвободиться из wait
        self._new_net_chunk_data_event.set()

        self._stopped = True

        logger.debug("[%s] The producer has been stopped", self)

    async def wait_until_stop(self) -> None:
        await self._is_finilized_future

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}({self._pcap_file_stem},"
            f"chunks len = {len(self._chunks)})"
        )
