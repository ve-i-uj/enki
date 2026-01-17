from __future__ import annotations

import asyncio
import logging
from asyncio import CancelledError, Future, Task
from signal import Signals
from typing import TYPE_CHECKING

from enki.misc import devonly
from tools.msgreader.readers.pcap_msg_reader.msg_data.ip2component import (
    Ip2ComponentType,
)
from tools.msgreader.readers.pcap_msg_reader.msg_data.msg_data_printer import (
    MsgDataPrinter,
)
from tools.msgreader.readers.pcap_msg_reader.msg_data.net_chunk_to_msg_data_parser import (
    NetChunk2MsgDataParser,
)
from tools.msgreader.readers.pcap_msg_reader.net_chunk.net_chunk_consumer import (
    NetChunkDataConsumer,
)
from tools.msgreader.readers.pcap_msg_reader.net_chunk.net_chunk_producer import (
    Pcap2NetChunkDataProducer,
)

if TYPE_CHECKING:
    from pathlib import Path


logger = logging.getLogger(__name__)


class PcapMsgReaderApp:
    """Приложение читает KBEngine-сообщения из пакетов транспортного уровня."""

    def __init__(
        self,
        pcap_files_directory: Path,
        mapping_file: Path,
        ignored_msgs: list[str],
    ) -> None:
        """Конструктор.

        Args:
            pcap_files_directory: путь до директории, содержащей
                pcap-файлы с KBEngine-сообщениями
            mapping_file: файл, содержащий мапинг ip-адреса
                KBEngine-компонента к имени компонента
            ignored_msgs: список имён сообщений, которые нужно
                игнорировать (пример: ["Logger::writeLog", ])

        """
        assert pcap_files_directory.is_dir(), "The path should be a directory"
        self._pcap_files_directory = pcap_files_directory
        self._mapping_file = mapping_file

        # Инициализация продюсеров данных сетевых пакетов из pcap-файлов.
        # Под каждый pcap файл в директории создаётся продюсер.
        self._net_chunks_producers: list[Pcap2NetChunkDataProducer] = []
        for pcap_file_path in self._pcap_files_directory.iterdir():
            if not pcap_file_path.is_file() or pcap_file_path.suffix != ".pcap":
                logger.debug(
                    "[%s] The path '%s' is not a pcap-file. Skip",
                    self,
                    pcap_file_path,
                )
                continue

            self._net_chunks_producers.append(
                Pcap2NetChunkDataProducer(pcap_file_path)
            )
        # Потребитель данных сетевых пакетов, который агрегирует данные из
        # разных pcap-файлов.
        self._consumer = NetChunkDataConsumer()
        self._consume_chunks_tasks: list[Task] = []

        # Парсинг данных из сетевого пакета в сообщения + метаинформация
        self._ip2comp_type = Ip2ComponentType(self._mapping_file)
        self._ip2comp_type.load_mapping()
        self._net_chunk_parser = NetChunk2MsgDataParser(self._ip2comp_type)
        self._parse_chunks_task: Task | None = None

        # Вывод результатов пользователю
        self._msg_data_printer = MsgDataPrinter(ignored_msgs)
        self._show_msg_data_task: Task | None = None

        self._is_running_future: Future[None] | None = None

        self._stopped = False

    @property
    def is_started(self) -> bool:
        return self._is_running_future is not None

    @property
    def stopping(self) -> bool:
        return self._stopped

    async def start(self) -> None:
        """Запустить чтение pcap-файлов и их отображение."""
        logger.debug("[%s] %s", self, devonly.func_args_values())

        async def consume_chunks(
            producer: Pcap2NetChunkDataProducer, consumer: NetChunkDataConsumer
        ) -> None:
            """Связка продюсеров сетевых пакетов и их потребителя."""
            logger.debug("[%s] %s", self, devonly.func_args_values())
            assert producer.is_started
            while True:
                try:
                    net_chunk_data = await producer.produce()
                except CancelledError:
                    break
                if net_chunk_data is None:
                    # Значит, что продюсер остановился
                    break
                consumer.consume(producer.pcap_file_stem, net_chunk_data)

        # Запустить всех продюсеров сетевых чанков и связать их с потребителем
        for producer in self._net_chunks_producers:
            await producer.start()
            self._consume_chunks_tasks.append(
                asyncio.create_task(consume_chunks(producer, self._consumer))
            )
        logger.debug("[%s] The producers of net chunks are run", self)

        async def parse_chunks(
            consumer: NetChunkDataConsumer,
            net_chunk_parser: NetChunk2MsgDataParser,
        ) -> None:
            """Связка объекта потребителя сетевых пакетов и парсера пакетов."""
            logger.debug("[%s] %s", self, devonly.func_args_values())
            # Остановка итератора означает, что он завершил свою работу.
            async for component_net_chunk_data in consumer:
                net_chunk_parser.parse(component_net_chunk_data)

        # Запустить связку потребителя и парсера сетевых пакетов.
        self._parse_chunks_task = asyncio.create_task(
            parse_chunks(self._consumer, self._net_chunk_parser)
        )

        async def show_msg_data(
            net_chunk_parser: NetChunk2MsgDataParser,
            msg_data_printer: MsgDataPrinter,
        ) -> None:
            """Связка парсера сетевых данных и объекта выдающего результат."""
            logger.debug("[%s] %s", self, devonly.func_args_values())
            try:
                async for msg_data in net_chunk_parser:
                    msg_data_printer.show_msg_data(msg_data)
            except CancelledError:
                pass

        # Запустить связку парсера сетевых данных и объекта выдающего результат.
        self._show_msg_data_task = asyncio.create_task(
            show_msg_data(self._net_chunk_parser, self._msg_data_printer)
        )

        logger.info("[%s] The reading of pcap-files has been started", self)

        self._is_running_future = Future()

    async def wait_until_stop(self) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        assert self._is_running_future is not None
        await self._is_running_future

    async def stop(self) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())

        if self._stopped:
            logger.info("[%s] The application is already stopping now", self)
            return

        self._stopped = True

        if self._is_running_future is None:
            logger.error("[%s] The application is not started", self)
            return

        if self._is_running_future.done():
            logger.warning("[%s] The application is already stopped", self)
            return

        # Конвеер выработки чанков основан на том, что они будут вырабатываться
        # вечно, т.к. pcap-файл читается в online режиме. Поэтому нужно
        # остановить производство чанков (т.е. чтения pcap). А затем дождаться,
        # когда консьюмер потребит все сетевые чанки из очереди каждого продюсера.
        for producer in self._net_chunks_producers:
            await producer.stop()
        for producer in self._net_chunks_producers:
            await producer.wait_until_stop()
        self._net_chunks_producers[:] = []

        # Это ожидание, когда консьюмером будут потреблены все выработанные
        # элементы.
        await asyncio.gather(*self._consume_chunks_tasks)
        self._consume_chunks_tasks[:] = []

        # Считанных данных из pcap-файла больше нет. Останавливаем консьюмер
        # и ждём пока он скормит все свои элементы, как итератор, парсеру.
        self._consumer.stop()
        assert self._parse_chunks_task is not None
        await self._parse_chunks_task

        # Сообщаем, что больше парсить нечего и ждём, когда итератор парсера
        # отдаст все распарсенные элементы.
        self._net_chunk_parser.stop()
        assert self._show_msg_data_task is not None
        await self._show_msg_data_task

        if not self._is_running_future.done():
            self._is_running_future.set_result(None)

    async def _handle_signal(self, sig) -> None:
        logger.debug("%s", devonly.func_args_values())
        if self.stopping:
            return

        logger.info(
            "The '%s' signal catched. Stop the application ...",
            Signals(sig).name,
        )
        while not self.is_started:
            logger.info("The application is not started yet. Wait to stop")
            await asyncio.sleep(0)

        try:
            await self.stop()
        except Exception as err:
            logger.error(
                "[%s] There is an error when stopping (err = '%s')",
                self,
                err,
                exc_info=True,
            )

        logger.info("The application is stopping now ...")

    def add_stop_signal(self, sig: Signals) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        loop = asyncio.get_event_loop()

        loop.add_signal_handler(
            sig,
            lambda *signame: asyncio.create_task(self._handle_signal(sig)),
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"
