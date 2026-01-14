"""Тесты для чтения данных сообщения из stdin."""

import asyncio
import collections
import datetime
import logging
from ipaddress import IPv4Address
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from enki import msgspec
from tools.msgreader.readers.pcap_msg_reader.ip2component import (
    Ip2ComponentType,
)
from tools.msgreader.readers.pcap_msg_reader.msg_data_printer import (
    MsgDataPrinter,
)
from tools.msgreader.readers.pcap_msg_reader.net_chunk_parser import (
    NetChunk2MsgDataParser,
)
from tools.msgreader.readers.pcap_msg_reader.pcap_file_chunker.net_chunk import (
    NetChunkData,
    PortValue,
)
from tools.msgreader.readers.pcap_msg_reader.pcap_file_chunker.net_chunk_consumer import (
    NetChunkDataConsumer,
    PcapFileNetChunkData,
)
from tools.msgreader.readers.pcap_msg_reader.pcap_file_chunker.net_chunk_producer import (
    Pcap2NetChunkDataProducer,
)
from tools.msgreader.readers.pcap_msg_reader.pcap_file_chunker.online_pcap_file_reader import (
    NetChunkData,
    OnlinePcapFileReader,
    Pcap2StreamNotStartedError,
)
from tools.msgreader.readers.pcap_msg_reader.pcap_msg_reader_app import (
    PcapMsgReaderApp,
)

if TYPE_CHECKING:
    from tools.msgreader.readers.pcap_msg_reader.pcap_file_chunker.pcap_file_stem import (
        PcapFileStem,
    )


class TestOnlinePcapFileReader:
    """Тесты класса, читающего pcap-файл."""

    # TODO: [2025-09-28 08:09 burov_alexey@mail.ru]:
    # Здесь нужно относительный путь ввести
    _pcap_file = Path(
        "/home/leto/2PeopleCompany/REPOS/enki/tests/utests/test_tools/test_msgreader/data/kbedump/dbmgr.pcap"
    )

    @pytest.mark.timeout(5)
    async def test_read_pcap_file(self):
        """Тест чтения pcap-файла."""
        online_pcap_reader = OnlinePcapFileReader(self._pcap_file)
        await online_pcap_reader.start()
        # Проверяем, что работает, как итератор и данные первого чанка
        i = 0
        async for chunk_data in online_pcap_reader:
            i += 1
            assert chunk_data == NetChunkData(
                time=datetime.datetime(2026, 1, 9, 17, 21, 26, 970459),
                src=IPv4Address("172.18.0.4"),
                dst=IPv4Address("255.255.255.255"),
                tcp_src_port=PortValue.no_port(),
                tcp_dst_port=PortValue.no_port(),
                udp_src_port=PortValue(42281),
                udp_dst_port=PortValue(20086),
                data="08007100e8030000726f6f74000a000000d1070000000000000100000000000000ffffffffffffffffffffffffac120004ad89ac120004b79900e70000000000000000000000000065010000000000000000000000000000000000000000000000000000000000d084000000000000ac1200044f39",
            )
            break

        # Проверяем, что хотя бы была одна итерация
        assert i > 0

        # Проверяем остановку
        await online_pcap_reader.stop()

    @pytest.mark.timeout(5)
    async def test_iterated_not_started(self):
        """Попытка итерировать pcap-файл, если читалка не запущена."""
        online_pcap_reader = OnlinePcapFileReader(self._pcap_file)
        with pytest.raises(Pcap2StreamNotStartedError):
            async for _chunk_data in online_pcap_reader:
                pass


class TestNetChunkDataConsumer:
    """Тесты класса, потребляющего данные pcap-файлов."""

    _dbmgr_pcap_file = Path(
        "/home/leto/2PeopleCompany/REPOS/enki/tests/utests/test_tools/test_msgreader/data/kbedump/dbmgr-4001-172.18.0.6.pcap"
    )
    _interfaces_pcap_file = Path(
        "/home/leto/2PeopleCompany/REPOS/enki/tests/utests/test_tools/test_msgreader/data/kbedump/interfaces-3001-172.18.0.5.pcap"
    )

    @pytest.mark.timeout(5)
    async def test_consume_pcap_files(self):
        """Тест агрегирования сетевых чанков от нескольких pcap-файлов."""
        dbmgr_producer = Pcap2NetChunkDataProducer(self._dbmgr_pcap_file)
        interfaces_producer = Pcap2NetChunkDataProducer(
            self._interfaces_pcap_file
        )

        consumer = NetChunkDataConsumer()

        await dbmgr_producer.start()
        await interfaces_producer.start()

        async def consume_chunks(
            producer: Pcap2NetChunkDataProducer, consumer: NetChunkDataConsumer
        ) -> None:
            assert producer.is_started
            while True:
                net_chunk_data = await producer.produce()
                if net_chunk_data is None:
                    # Значит, что продюсер остановился
                    break
                consumer.consume(producer.pcap_file_stem, net_chunk_data)

        pcap_file_net_chunk_datas: list[PcapFileNetChunkData] = []

        async def collect_chunks() -> None:
            async for component_net_chunk_data in consumer:
                pcap_file_net_chunk_datas.append(component_net_chunk_data)

        dbmgr_task = asyncio.create_task(
            consume_chunks(dbmgr_producer, consumer)
        )
        interfaces_task = asyncio.create_task(
            consume_chunks(interfaces_producer, consumer)
        )

        collect_chunks_task = asyncio.create_task(collect_chunks())

        await asyncio.sleep(2)

        await dbmgr_producer.stop()
        await dbmgr_producer.wait_until_stop()
        await dbmgr_task

        await interfaces_producer.stop()
        await interfaces_producer.wait_until_stop()
        await interfaces_task

        consumer.stop()

        await collect_chunks_task

        chunks_by_pcap_file_name: dict[PcapFileStem, list[NetChunkData]] = (
            collections.defaultdict(list)
        )
        # Эта переменная нужна, чтобы увидеть входящие пакеты (они отличаются
        # от ip компонета)
        chunks_by_src_ip: dict[str, dict[IPv4Address, list[NetChunkData]]] = (
            collections.defaultdict(dict)
        )
        for info in pcap_file_net_chunk_datas:
            chunks_by_pcap_file_name[info.pcap_file_stem].append(
                info.net_chunk_data
            )
            chunks_by_src_ip[info.pcap_file_stem._filename_stem].setdefault(
                info.net_chunk_data.src, []
            ).append(info.net_chunk_data)

        # Есть чанки от обоих KBEngine-сервисов (т.е. есть чанки из двух файлов)
        assert len(chunks_by_pcap_file_name) == 2


class TestNetChunk2MsgDataParser:
    """Тесты класса, парсящего данные чанков из pcap-файла в KBEngine-сообщения."""

    _dbmgr_pcap_file = Path(
        "/home/leto/2PeopleCompany/REPOS/enki/tests/utests/test_tools/test_msgreader/data/kbedump/dbmgr-4001-172.18.0.6.pcap"
    )
    _interfaces_pcap_file = Path(
        "/home/leto/2PeopleCompany/REPOS/enki/tests/utests/test_tools/test_msgreader/data/kbedump/interfaces-3001-172.18.0.5.pcap"
    )
    _component_name_by_ip_file = Path(
        "/home/leto/2PeopleCompany/REPOS/enki/tests/utests/test_tools/test_msgreader/data/component-name-by-ip.file"
    )

    @pytest.mark.timeout(5)
    async def test_parse_net_chunks(self):
        """Тест парсинга сетевых чанков от нескольких pcap-файлов."""
        dbmgr_producer = Pcap2NetChunkDataProducer(self._dbmgr_pcap_file)
        interfaces_producer = Pcap2NetChunkDataProducer(
            self._interfaces_pcap_file
        )

        consumer = NetChunkDataConsumer()

        await dbmgr_producer.start()
        await interfaces_producer.start()

        async def consume_chunks(
            producer: Pcap2NetChunkDataProducer, consumer: NetChunkDataConsumer
        ) -> None:
            assert producer.is_started
            while True:
                net_chunk_data = await producer.produce()
                if net_chunk_data is None:
                    # Значит, что продюсер остановился
                    break
                consumer.consume(producer.pcap_file_stem, net_chunk_data)

        ip2comp_type = Ip2ComponentType(self._component_name_by_ip_file)
        net_chunk_parser = NetChunk2MsgDataParser(ip2comp_type)

        async def parse_chunks() -> None:
            async for component_net_chunk_data in consumer:
                net_chunk_parser.parse(component_net_chunk_data)

        consume_dbmgr_chunks_task = asyncio.create_task(
            consume_chunks(dbmgr_producer, consumer)
        )
        consume_interfaces_chunks_task = asyncio.create_task(
            consume_chunks(interfaces_producer, consumer)
        )

        parse_chunks_task = asyncio.create_task(parse_chunks())

        # Подождём пока все чанка из файла прочитаются.
        await asyncio.sleep(2)

        # Конвеер выработки чанков основан на том, что они будут вырабатываться
        # вечно, т.к. pcap-файл читается unlinkne режиме. Поэтому нужно
        # остановить производство чанков (т.е. чтения pcap) и затем потребление
        # чанков.

        await dbmgr_producer.stop()
        await dbmgr_producer.wait_until_stop()
        # Ждём когда цикл async for остановится
        await consume_dbmgr_chunks_task

        await interfaces_producer.stop()
        await interfaces_producer.wait_until_stop()
        # Ждём когда цикл async for остановится
        await consume_interfaces_chunks_task

        consumer.stop()

        await parse_chunks_task

        assert not [
            d
            for d in net_chunk_parser._msgs_data
            if not d.deserialize_msg_result
        ]

        # Есть асинхронный итератор
        parsed_data = None
        async for parsed_data in net_chunk_parser:
            break
        net_chunk_parser.stop()

        assert parsed_data is not None


class TestMsgDataRepresentator:
    """Тесты сервиса для отображения для пользователя данных KBEngine-сообщения."""

    _dbmgr_pcap_file = Path(
        "/home/leto/2PeopleCompany/REPOS/enki/tests/utests/test_tools/test_msgreader/data/kbedump/dbmgr-4001-172.18.0.6.pcap"
    )
    _interfaces_pcap_file = Path(
        "/home/leto/2PeopleCompany/REPOS/enki/tests/utests/test_tools/test_msgreader/data/kbedump/interfaces-3001-172.18.0.5.pcap"
    )
    _component_name_by_ip_file = Path(
        "/home/leto/2PeopleCompany/REPOS/enki/tests/utests/test_tools/test_msgreader/data/component-name-by-ip.file"
    )

    @pytest.mark.timeout(5)
    async def test_show_parsed(self, caplog):
        """Тест отображения распарсенного сетевого чанка пользователю.

        Просто проверка, что нет ошибок и возможность посмотреть под дебагером.
        """
        # Нужно, чтобы можно было видеть только сообщения. Или важные предупреждения
        caplog.set_level(logging.WARNING)

        dbmgr_producer = Pcap2NetChunkDataProducer(self._dbmgr_pcap_file)
        interfaces_producer = Pcap2NetChunkDataProducer(
            self._interfaces_pcap_file
        )

        consumer = NetChunkDataConsumer()

        await dbmgr_producer.start()
        await interfaces_producer.start()

        async def consume_chunks(
            producer: Pcap2NetChunkDataProducer, consumer: NetChunkDataConsumer
        ) -> None:
            assert producer.is_started
            while True:
                net_chunk_data = await producer.produce()
                if net_chunk_data is None:
                    # Значит, что продюсер остановился
                    break
                consumer.consume(producer.pcap_file_stem, net_chunk_data)

        ip2comp_type = Ip2ComponentType(self._component_name_by_ip_file)
        ip2comp_type.load_mapping()

        net_chunk_parser = NetChunk2MsgDataParser(ip2comp_type)

        async def parse_chunks() -> None:
            async for component_net_chunk_data in consumer:
                net_chunk_parser.parse(component_net_chunk_data)

        ignored_msgs = [msgspec.logger.writeLog.name]
        msg_data_representator = MsgDataPrinter(ignored_msgs)

        async def show_msg_data() -> None:
            async for msg_data in net_chunk_parser:
                msg_data_representator.show_msg_data(msg_data)

        consume_dbmgr_chunks_task = asyncio.create_task(
            consume_chunks(dbmgr_producer, consumer)
        )
        consume_interfaces_chunks_task = asyncio.create_task(
            consume_chunks(interfaces_producer, consumer)
        )

        parse_chunks_task = asyncio.create_task(parse_chunks())

        asyncio.create_task(show_msg_data())

        # Подождём пока все чанка из файла прочитаются.
        await asyncio.sleep(2)

        # Конвеер выработки чанков основан на том, что они будут вырабатываться
        # вечно, т.к. pcap-файл читается online режиме. Поэтому нужно
        # остановить производство чанков (т.е. чтения pcap) и затем потребление
        # чанков.

        await dbmgr_producer.stop()
        await dbmgr_producer.wait_until_stop()
        # Ждём когда цикл async for остановится
        await consume_dbmgr_chunks_task

        await interfaces_producer.stop()
        await interfaces_producer.wait_until_stop()
        # Ждём когда цикл async for остановится
        await consume_interfaces_chunks_task

        consumer.stop()

        await parse_chunks_task


class TestPcapMsgReaderApp:
    """Тесты приложения, читающего pcap-файлы в режиме online."""

    _pcap_files_directory = Path(
        "/home/leto/2PeopleCompany/REPOS/enki/tests/utests/test_tools/test_msgreader/data/kbedump"
    )
    _component_name_by_ip_file = Path(
        "/home/leto/2PeopleCompany/REPOS/enki/tests/utests/test_tools/test_msgreader/data/component-name-by-ip.file"
    )

    @pytest.mark.timeout(5)
    async def test_init(self):
        """Тест инициализации приложения."""
        PcapMsgReaderApp(
            self._pcap_files_directory,
            self._component_name_by_ip_file,
            ignored_msgs=[],
        )

    @pytest.mark.timeout(5)
    async def test_start(self, caplog):
        """Тест запуска приложения."""
        # Нужно, чтобы можно было видеть только сообщения. Или важные предупреждения
        caplog.set_level(logging.WARNING)

        app = PcapMsgReaderApp(
            self._pcap_files_directory,
            self._component_name_by_ip_file,
            ignored_msgs=[msgspec.logger.writeLog.name],
        )
        await app.start()

        await asyncio.sleep(3)

        await app.stop()
