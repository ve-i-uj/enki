"""Тесты для чтения данных сообщения из stdin."""

import datetime
from ipaddress import IPv4Address
from pathlib import Path

import pytest

from tools.msgreader.readers.pcap_msg_reader.pcap_file_chunker.online_pcap_file_reader import (
    OnlinePcapFileReader,
    Pcap2StreamNotStartedError,
    NetChunkData,
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
                tcp_src_port=-1,
                tcp_dst_port=-1,
                udp_src_port=42281,
                udp_dst_port=20086,
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
            async for chunk_data in online_pcap_reader:
                pass
