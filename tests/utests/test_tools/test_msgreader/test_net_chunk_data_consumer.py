"""Тесты потребителя сетевых пакетов."""

import asyncio
import collections
from ipaddress import IPv4Address
from pathlib import Path
import pytest

from tools.msgreader.readers.pcap_msg_reader.pcap_file_chunker.net_chunk_data import NetChunkData
from tools.msgreader.readers.pcap_msg_reader.pcap_file_chunker.net_chunk_data_consumer import PcapFileNetChunkData, NetChunkDataConsumer, PcapFileStem
from tools.msgreader.readers.pcap_msg_reader.pcap_file_chunker.net_chunk_data_producer import Pcap2NetChunkDataProducer


class TestOnlinePcapFileReader:
    """Тесты класса, читающего pcap-файл."""

    _dbmgr_pcap_file = Path(
        "/home/leto/2PeopleCompany/REPOS/enki/tests/utests/test_tools/test_msgreader/data/kbedump/dbmgr.pcap"
    )
    _interfaces_pcap_file = Path(
        "/home/leto/2PeopleCompany/REPOS/enki/tests/utests/test_tools/test_msgreader/data/kbedump/interfaces.pcap"
    )

    @pytest.mark.timeout(5)
    async def test_read_pcap_file(self):
        """Тест чтения pcap-файла."""
        dbmgr_producer = Pcap2NetChunkDataProducer(self._dbmgr_pcap_file)
        interfaces_producer = Pcap2NetChunkDataProducer(self._interfaces_pcap_file)

        consumer = NetChunkDataConsumer()

        await dbmgr_producer.start()
        await interfaces_producer.start()

        async def consume_chunks(producer: Pcap2NetChunkDataProducer, consumer: NetChunkDataConsumer):
            assert producer.is_started
            while True:
                net_chunk_data = await producer.produce()
                if net_chunk_data is None:
                    # Значит, что продюсер остановился
                    break
                consumer.consume(producer.pcap_file_stem, net_chunk_data)

        pcap_file_net_chunk_datas: list[PcapFileNetChunkData] = []

        async def collect_chunks():
            async for component_net_chunk_data in consumer:
                pcap_file_net_chunk_datas.append(component_net_chunk_data)

        dbmgr_task = asyncio.create_task(consume_chunks(dbmgr_producer, consumer))
        interfaces_task = asyncio.create_task(consume_chunks(interfaces_producer, consumer))

        collect_chunks_task = asyncio.create_task(collect_chunks())

        await asyncio.sleep(2)

        await dbmgr_producer.stop()
        await dbmgr_producer.wait_until_stop()

        await interfaces_producer.stop()
        await interfaces_producer.wait_until_stop()

        consumer.stop_consume()

        await dbmgr_task
        await interfaces_task
        await collect_chunks_task

        chunks_by_pcap_file_name: dict[PcapFileStem, list[NetChunkData]] = \
            collections.defaultdict(list)
        # Эта переменная нужна, чтобы увидеть входящие пакеты (они отличаются 
        # от ip компонета)
        chunks_by_src_ip: dict[PcapFileStem, dict[IPv4Address, list[NetChunkData]]] = \
            collections.defaultdict(dict)
        for info in pcap_file_net_chunk_datas:
            chunks_by_pcap_file_name[info.pcap_file_stem].append(info.net_chunk_data)
            chunks_by_src_ip[info.pcap_file_stem].setdefault(
                info.net_chunk_data.src, []
            ).append(info.net_chunk_data)
        
        # Есть чанки от обоих KBEngine-сервисов (т.е. есть чанки из двух файлов)
        assert len(chunks_by_pcap_file_name) == 2
