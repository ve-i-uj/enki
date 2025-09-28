"""Тесты для чтения данных сообщения из stdin."""

import datetime
from ipaddress import IPv4Address
from pathlib import Path
import subprocess

import pytest

from tools.msgreader.readers.stream_reader.stream_pcap import (
    Pcap2Stream,
    Pcap2StreamNotStartedError,
    NetChunkData,
)


class TestPcap2Stream:
    """Тесты класса, читающего pcap-файл."""

    # TODO: [2025-09-28 08:09 burov_alexey@mail.ru]:
    # Здесь нужно относительный путь ввести
    _pcap_file = Path(
        "/home/leto/2PeopleCompany/REPOS/enki/tests/utests/test_tools/test_msgreader/data/merged.pcap"
    )

    @pytest.mark.timeout(5)
    async def test_read_pcap_file(self):
        """Тест чтения pcap-файла."""
        pcap2stream = Pcap2Stream(self._pcap_file)
        await pcap2stream.start()
        # Проверяем, что работает, как итератор и данные первого чанка
        i = 0
        async for chunk_data in pcap2stream:
            i += 1
            assert chunk_data == NetChunkData(
                time=datetime.datetime(
                    2025, 9, 19, 19, 2, 23, 354598
                ),
                src=IPv4Address("172.18.0.10"),
                dst=IPv4Address("172.18.0.8"),
                tcp_src_port=45642,
                tcp_dst_port=34801,
                udp_src_port=-1,
                udp_dst_port=-1,
                data="0f00591b00000000000000000000f96a6b3e00000000",
            )
            break

        # Проверяем, что хотя бы была одна итерация
        assert i > 0

        # Проверяем остановку
        await pcap2stream.stop()

    @pytest.mark.timeout(5)
    async def test_iterated_not_started(self):
        """Попытка итерировать pcap-файл, если читалка не запущена."""
        pcap2stream = Pcap2Stream(self._pcap_file)
        with pytest.raises(Pcap2StreamNotStartedError):
            async for chunk_data in pcap2stream:
                pass
