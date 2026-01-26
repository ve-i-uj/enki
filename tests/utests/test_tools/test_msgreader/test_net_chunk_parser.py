import asyncio
import datetime
from ipaddress import IPv4Address
from pathlib import Path

import pytest

from tools.msgreader.readers.pcap_msg_reader.msg_data.ip2component import (
    Ip2ComponentType,
)
from tools.msgreader.readers.pcap_msg_reader.msg_data.net_chunk_to_msg_data_parser import (
    NetChunk2MsgDataParser,
)
from tools.msgreader.readers.pcap_msg_reader.net_chunk.net_chunk import (
    NetChunkData,
    PortValue,
)
from tools.msgreader.readers.pcap_msg_reader.net_chunk.net_chunk_consumer import (
    PcapFileNetChunkData,
)
from tools.msgreader.readers.pcap_msg_reader.net_chunk.pcap_file_stem import (
    PcapFileStem,
)


class TestNetChunk2MsgDataParser:

    @pytest.mark.timeout(5)
    async def test_parse_Supervisor_onLookApp(
        self, supervisor_mapping_config_file
    ):
        """Со своего хоста приходит healcheck запрос и в ответ Machine::onLookApp.

        Была ошибка, что MsgReader думает, что это Machine::onBroadcastInterface,
        хотя это Machine::onLookApp без оболочки.
        """
        ip2comp_type = Ip2ComponentType(Path(supervisor_mapping_config_file))
        ip2comp_type.load_mapping()
        net_chunk_parser = NetChunk2MsgDataParser(ip2comp_type)

        pcap_file_net_chunk_data = PcapFileNetChunkData(
            PcapFileStem("supervisor-1001-172.18.0.3"),
            net_chunk_data=NetChunkData(
                time=datetime.datetime(2026, 1, 15, 15, 29, 17, 325317),
                src=IPv4Address("172.18.0.3"),
                dst=IPv4Address("172.18.0.3"),
                tcp_src_port=PortValue(20099),
                tcp_dst_port=PortValue(53316),
                udp_src_port=PortValue(-1),
                udp_dst_port=PortValue(-1),
                data="08000000010000000000000001",
            ),
        )

        net_chunk_parser.parse(pcap_file_net_chunk_data)
        await asyncio.sleep(0)

        assert len(net_chunk_parser._msgs_data) == 1
        msg_data = net_chunk_parser._msgs_data[0]

        assert msg_data.deserialize_msg_result.success

        assert msg_data.deserialize_msg_result.result.msg is not None
        assert (
            msg_data.deserialize_msg_result.result.msg.name
            == "Machine::onLookApp"
        )
        assert not msg_data.deserialize_msg_result.result.data_tail

    @pytest.mark.timeout(5)
    async def test_parse_Logger_onLookApp(self, logger_mapping_config_file):
        """Со своего хоста приходит healcheck запрос и в ответ Logger::onLookApp.

        Была ошибка, что MsgReader думает, что это Logger::queryLoad,
        хотя это Logger::onLookApp без оболочки.
        """
        ip2comp_type = Ip2ComponentType(Path(logger_mapping_config_file))
        ip2comp_type.load_mapping()
        net_chunk_parser = NetChunk2MsgDataParser(ip2comp_type)

        pcap_file_net_chunk_data = PcapFileNetChunkData(
            PcapFileStem("logger-2001-172.18.0.4"),
            net_chunk_data=NetChunkData(
                time=datetime.datetime(2026, 1, 15, 15, 29, 17, 325317),
                src=IPv4Address("172.18.0.4"),
                dst=IPv4Address("172.18.0.4"),
                tcp_src_port=PortValue(20099),
                tcp_dst_port=PortValue(53316),
                udp_src_port=PortValue(-1),
                udp_dst_port=PortValue(-1),
                data="0a000000d10700000000000001",
            ),
        )

        net_chunk_parser.parse(pcap_file_net_chunk_data)
        await asyncio.sleep(0)

        assert len(net_chunk_parser._msgs_data) == 1
        msg_data = net_chunk_parser._msgs_data[0]

        assert msg_data.deserialize_msg_result.success
        assert msg_data.deserialize_msg_result.result.msg is not None
        assert (
            msg_data.deserialize_msg_result.result.msg.name
            == "Logger::onLookApp"
        )
        assert not msg_data.deserialize_msg_result.result.data_tail

    @pytest.mark.timeout(5)
    async def test_parse_LoginApp_hello(self, loginapp_mapping_config_file):
        """С клиента приходит сообщение LoginApp::hello.

        Нужно отличать от мусора по tcp на сетевом мосту в фильтрах.
        """
        ip2comp_type = Ip2ComponentType(Path(loginapp_mapping_config_file))
        ip2comp_type.load_mapping()
        net_chunk_parser = NetChunk2MsgDataParser(ip2comp_type)

        pcap_file_net_chunk_data = PcapFileNetChunkData(
            PcapFileStem("loginapp-9001-172.18.0.11"),
            net_chunk_data=NetChunkData(
                time=datetime.datetime(
                    2026,
                    1,
                    24,
                    11,
                    21,
                    48,
                    257638,
                    tzinfo=datetime.timezone.utc,
                ),
                src=IPv4Address("172.18.0.1"),
                dst=IPv4Address("172.18.0.11"),
                tcp_src_port=PortValue(44808),
                tcp_dst_port=PortValue(20013),
                udp_src_port=PortValue(-1),
                udp_dst_port=PortValue(-1),
                data="04001100322e352e313000302e312e300000000000",
            ),
        )

        net_chunk_parser.parse(pcap_file_net_chunk_data)
        await asyncio.sleep(0)

        assert len(net_chunk_parser._msgs_data) == 1
        msg_data = net_chunk_parser._msgs_data[0]

        assert msg_data.deserialize_msg_result.success
        assert msg_data.deserialize_msg_result.result.msg is not None
        assert (
            msg_data.deserialize_msg_result.result.msg.name == "Loginapp::hello"
        )
        assert not msg_data.deserialize_msg_result.result.data_tail

    @pytest.mark.timeout(5)
    async def test_parse_Client_onHello(self, client_mapping_config_file):
        """С клиента приходит сообщение Client::onHello.

        Нужно отличать от мусора по tcp на сетевом мосту в фильтрах.
        """
        ip2comp_type = Ip2ComponentType(Path(client_mapping_config_file))
        ip2comp_type.load_mapping()
        net_chunk_parser = NetChunk2MsgDataParser(ip2comp_type)

        pcap_file_net_chunk_data = PcapFileNetChunkData(
            PcapFileStem("loginapp-9001-172.18.0.11"),
            net_chunk_data=NetChunkData(
                time=datetime.datetime(
                    2026,
                    1,
                    24,
                    11,
                    21,
                    48,
                    257866,
                    tzinfo=datetime.timezone.utc,
                ),
                src=IPv4Address("172.18.0.11"),
                dst=IPv4Address("172.18.0.1"),
                tcp_src_port=PortValue(20013),
                tcp_dst_port=PortValue(44808),
                udp_src_port=PortValue(-1),
                udp_dst_port=PortValue(-1),
                data="09025300322e352e313000302e312e300036363042333337343934434443453339314538454138463046353539304442380030364531354631303242343831414346384341313945324634313044314236340002000000",
            ),
        )

        net_chunk_parser.parse(pcap_file_net_chunk_data)
        await asyncio.sleep(0)

        assert len(net_chunk_parser._msgs_data) == 1
        msg_data = net_chunk_parser._msgs_data[0]

        assert msg_data.deserialize_msg_result.success
        assert msg_data.deserialize_msg_result.result.msg is not None
        assert (
            msg_data.deserialize_msg_result.result.msg.name
            == "Client::onHelloCB"
        )
        assert not msg_data.deserialize_msg_result.result.data_tail

    @pytest.mark.timeout(5)
    async def test_parse_DBMgr_onEntityOffline(self, dbmgr_mapping_config_file):
        """Сообщение DBMgr::onEntityOffline -> .

        Не парсилось, т.к. была не выставлена фиксированная длина в описании.
        """
        ip2comp_type = Ip2ComponentType(Path(dbmgr_mapping_config_file))
        ip2comp_type.load_mapping()
        net_chunk_parser = NetChunk2MsgDataParser(ip2comp_type)

        pcap_file_net_chunk_data = PcapFileNetChunkData(
            pcap_file_stem=PcapFileStem("dbmgr-4001-172.18.0.6"),
            net_chunk_data=NetChunkData(
                time=datetime.datetime(
                    2026,
                    1,
                    24,
                    12,
                    14,
                    51,
                    975539,
                    tzinfo=datetime.timezone.utc,
                ),
                src=IPv4Address("172.18.0.10"),
                dst=IPv4Address("172.18.0.6"),
                tcp_src_port=PortValue(49056),
                tcp_dst_port=PortValue(58399),
                udp_src_port=PortValue(-1),
                udp_dst_port=PortValue(-1),
                data="1300060000000000000001000000",
            ),
        )

        net_chunk_parser.parse(pcap_file_net_chunk_data)
        await asyncio.sleep(0)

        assert len(net_chunk_parser._msgs_data) == 1
        msg_data = net_chunk_parser._msgs_data[0]

        assert msg_data.deserialize_msg_result.success
        assert msg_data.deserialize_msg_result.result.msg is not None
        assert (
            msg_data.deserialize_msg_result.result.msg.name
            == "DBMgr::onEntityOffline"
        )
        assert not msg_data.deserialize_msg_result.result.data_tail

    @pytest.mark.timeout(5)
    async def test_parse_Baseappp(self, mapping_config_file):
        """Сообщение от DBMgr -> Baseapp.

        Не парсилось, т.к.
        """
        ip2comp_type = Ip2ComponentType(Path(mapping_config_file))
        ip2comp_type.load_mapping()
        net_chunk_parser = NetChunk2MsgDataParser(ip2comp_type)

        pcap_file_net_chunk_data = PcapFileNetChunkData(
            pcap_file_stem=PcapFileStem("dbmgr-4001-172.18.0.6"),
            net_chunk_data=NetChunkData(
                time=datetime.datetime(
                    2026, 1, 25, 3, 33, 54, 473718, tzinfo=datetime.timezone.utc
                ),
                src=IPv4Address("172.18.0.6"),
                dst=IPv4Address("172.18.0.10"),
                tcp_src_port=PortValue(58399),
                tcp_dst_port=PortValue(49056),
                udp_src_port=PortValue(-1),
                udp_dst_port=PortValue(-1),
                data="2400d3070000070000000000000000000000000001",
            ),
        )
        net_chunk_parser.parse(pcap_file_net_chunk_data)
        await asyncio.sleep(0)

        assert len(net_chunk_parser._msgs_data) == 1
        msg_data = net_chunk_parser._msgs_data[0]

        assert msg_data.deserialize_msg_result.success
        assert msg_data.deserialize_msg_result.result.msg is not None
        assert (
            msg_data.deserialize_msg_result.result.msg.name
            == "Baseapp::onWriteToDBCallback"
        )
        assert not msg_data.deserialize_msg_result.result.data_tail
