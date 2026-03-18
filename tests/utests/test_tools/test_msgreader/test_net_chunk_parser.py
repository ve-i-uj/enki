import asyncio
import datetime
from ipaddress import IPv4Address
from pathlib import Path

import pytest

from enki import msgspec
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
    async def test_parse_Supervisor_onLookApp(self, supervisor_mapping_config_file):
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
        assert msg_data.deserialize_msg_result.result.msg.name == "Machine::onLookApp"
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
        assert msg_data.deserialize_msg_result.result.msg.name == "Logger::onLookApp"
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
        assert msg_data.deserialize_msg_result.result.msg.name == "Loginapp::hello"
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
        assert msg_data.deserialize_msg_result.result.msg.name == "Client::onHelloCB"
        assert not msg_data.deserialize_msg_result.result.data_tail

    @pytest.mark.timeout(5)
    async def test_parse_DBMgr_onEntityOffline(self, dbmgr_mapping_config_file):
        """Сообщение Dbmgr::onEntityOffline -> .

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
            == msgspec.dbmgr.onEntityOffline.name
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

    @pytest.mark.timeout(5)
    async def test_parse_CellappMgr(self, mapping_config_file):
        """Сообщение от Cellapp -> CellappMgr.

        Не парсилось. Два сообщения Cellappmgr::updateCellapp в пакете (был
        хвост данных после парсинга).
        """
        ip2comp_type = Ip2ComponentType(Path(mapping_config_file))
        ip2comp_type.load_mapping()
        net_chunk_parser = NetChunk2MsgDataParser(ip2comp_type)

        pcap_file_net_chunk_data = PcapFileNetChunkData(
            pcap_file_stem=PcapFileStem("cellappmgr-5001-172.18.0.7"),
            net_chunk_data=NetChunkData(
                time=datetime.datetime(
                    2026, 1, 25, 11, 1, 29, 400932, tzinfo=datetime.timezone.utc
                ),
                src=IPv4Address("172.18.0.9"),
                dst=IPv4Address("172.18.0.7"),
                tcp_src_port=PortValue(44206),
                tcp_dst_port=PortValue(52679),
                udp_src_port=PortValue(-1),
                udp_dst_port=PortValue(-1),
                data="0f00591b00000000000000000000d4c0b03e000000000f00591b000000000000000000000f1bb43e00000000",
            ),
        )
        net_chunk_parser.parse(pcap_file_net_chunk_data)
        await asyncio.sleep(0)

        # Два сообщения в пакете
        assert len(net_chunk_parser._msgs_data) == 2
        for msg_data in net_chunk_parser._msgs_data:

            assert msg_data.deserialize_msg_result.success
            assert msg_data.deserialize_msg_result.result.msg is not None
            assert (
                msg_data.deserialize_msg_result.result.msg.name
                == "Cellappmgr::updateCellapp"
            )
            assert not msg_data.deserialize_msg_result.result.data_tail

    @pytest.mark.timeout(5)
    async def test_parse_queryComponentID(self, mapping_config_file):
        """Сообщение Machine::onBroadcastInterface (Supervisor --> Cellappmgr).

        Определялось, как Machine::queryComponentID
        """
        ip2comp_type = Ip2ComponentType(Path(mapping_config_file))
        ip2comp_type.load_mapping()
        net_chunk_parser = NetChunk2MsgDataParser(ip2comp_type)

        pcap_file_net_chunk_data = PcapFileNetChunkData(
            pcap_file_stem=PcapFileStem("supervisor-1001-172.18.0.3"),
            net_chunk_data=NetChunkData(
                time=datetime.datetime(
                    2026,
                    1,
                    25,
                    11,
                    1,
                    8,
                    616864,
                    tzinfo=datetime.timezone.utc,
                ),
                src=IPv4Address("172.18.0.3"),
                dst=IPv4Address("172.18.0.7"),
                tcp_src_port=PortValue(-1),
                tcp_dst_port=PortValue(-1),
                udp_src_port=PortValue(49426),
                udp_dst_port=PortValue(20977),
                data="e8030000726f6f74000a000000d1070000000000008913000000000000ffffffffffffffffffffffffac120004bc07ac120004928b0094000000000000000000000000605f010000000000000000000000000000000000000000000000000000000000d084000000000000ac12000450c5",
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
            == "Machine::onBroadcastInterface"
        )
        assert not msg_data.deserialize_msg_result.result.data_tail

    @pytest.mark.timeout(5)
    async def test_parse_req_onQueryAllInterfaceInfos(self, mapping_config_file):
        """Запрос Machine::onQueryAllInterfaceInfos.

        Не отображалось. Фильтрация от хоста срабатывала.
        """
        ip2comp_type = Ip2ComponentType(Path(mapping_config_file))
        ip2comp_type.load_mapping()
        net_chunk_parser = NetChunk2MsgDataParser(ip2comp_type)

        pcap_file_net_chunk_data = PcapFileNetChunkData(
            pcap_file_stem=PcapFileStem("supervisor-1001-172.18.0.3"),
            net_chunk_data=NetChunkData(
                time=datetime.datetime(
                    2026, 1, 26, 8, 31, 58, 178949, tzinfo=datetime.timezone.utc
                ),
                src=IPv4Address("172.18.0.1"),
                dst=IPv4Address("172.18.0.3"),
                tcp_src_port=PortValue(-1),
                tcp_dst_port=PortValue(-1),
                udp_src_port=PortValue(35345),
                udp_dst_port=PortValue(20086),
                data="0400070000000000000000",
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
            == "Machine::onQueryAllInterfaceInfos"
        )
        assert not msg_data.deserialize_msg_result.result.data_tail

    @pytest.mark.timeout(5)
    async def test_parse_resp_onQueryAllInterfaceInfos(self, mapping_config_file):
        """Ответ на Machine::onQueryAllInterfaceInfos.

        Не отображалось.
        """
        ip2comp_type = Ip2ComponentType(Path(mapping_config_file))
        ip2comp_type.load_mapping()
        net_chunk_parser = NetChunk2MsgDataParser(ip2comp_type)

        pcap_file_net_chunk_data = PcapFileNetChunkData(
            pcap_file_stem=PcapFileStem("supervisor-1001-172.18.0.3"),
            net_chunk_data=NetChunkData(
                time=datetime.datetime(
                    2026, 1, 26, 8, 31, 58, 200486, tzinfo=datetime.timezone.utc
                ),
                src=IPv4Address("172.18.0.3"),
                dst=IPv4Address("172.18.0.1"),
                tcp_src_port=PortValue(-1),
                tcp_dst_port=PortValue(-1),
                udp_src_port=PortValue(20086),
                udp_dst_port=PortValue(35345),
                data="e8030000726f6f74000a000000d1070000000000000200000000000000ffffffffffffffffffffffffac120004e59fac1200048b9b0035000000000000000000000000805f010000000000000000000000000000000000000000000000000000000000d084000000000000ac1200044edf",
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
            == "Machine::onBroadcastInterface"
        )
        assert not msg_data.deserialize_msg_result.result.data_tail

    @pytest.mark.timeout(5)
    async def test_parse_resp_Loginapp_login(self, mapping_config_file):
        """Сообщение на Loginapp::login.

        Не отображалось.
        """
        ip2comp_type = Ip2ComponentType(Path(mapping_config_file))
        ip2comp_type.load_mapping()
        net_chunk_parser = NetChunk2MsgDataParser(ip2comp_type)

        pcap_file_net_chunk_data = PcapFileNetChunkData(
            pcap_file_stem=PcapFileStem("loginapp-9001-172.18.0.11"),
            net_chunk_data=NetChunkData(
                time=datetime.datetime(
                    2026, 2, 1, 2, 12, 6, 630551, tzinfo=datetime.timezone.utc
                ),
                src=IPv4Address("172.18.0.1"),
                dst=IPv4Address("172.18.0.11"),
                tcp_src_port=PortValue(33036),
                tcp_dst_port=PortValue(20013),
                udp_src_port=PortValue(-1),
                udp_dst_port=PortValue(-1),
                data="030024000300000000756d6f464c4f4976586b004f455054556c756e687300736164666173660000",
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
            == msgspec.loginapp.login.name
        )
        assert not msg_data.deserialize_msg_result.result.data_tail

    @pytest.mark.timeout(5)
    async def test_parse_resp_Interfaces_reqCreateAccount(self, mapping_config_file):
        """Сообщение на Interfaces::reqCreateAccount.

        Не отображалось.
        """
        ip2comp_type = Ip2ComponentType(Path(mapping_config_file))
        ip2comp_type.load_mapping()
        net_chunk_parser = NetChunk2MsgDataParser(ip2comp_type)

        pcap_file_net_chunk_data = PcapFileNetChunkData(
            pcap_file_stem=PcapFileStem("dbmgr-4001-172.19.0.6"),
            net_chunk_data=NetChunkData(
                time=datetime.datetime(
                    2026, 2, 27, 7, 4, 47, 728554, tzinfo=datetime.timezone.utc
                ),
                src=IPv4Address("172.19.0.6"),
                dst=IPv4Address("172.19.0.5"),
                tcp_src_port=PortValue(37444),
                tcp_dst_port=PortValue(30099),
                udp_src_port=PortValue(-1),
                udp_dst_port=PortValue(-1),
                data="0900230029230000000000004e426b4d744f57536244007266726265623834334f000100000000",
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
            == msgspec.interfaces.reqCreateAccount.name
        )
        assert not msg_data.deserialize_msg_result.result.data_tail

    @pytest.mark.timeout(5)
    async def test_parse_resp_Dbmgr_onCreateAccountCBFromInterfaces(
        self, mapping_config_file
    ):
        """Сообщение на Dbmgr::onCreateAccountCBFromInterfaces.

        Не отображалось.
        """
        ip2comp_type = Ip2ComponentType(Path(mapping_config_file))
        ip2comp_type.load_mapping()
        net_chunk_parser = NetChunk2MsgDataParser(ip2comp_type)

        pcap_file_net_chunk_data = PcapFileNetChunkData(
            pcap_file_stem=PcapFileStem("dbmgr-4001-172.19.0.6"),
            net_chunk_data=NetChunkData(
                time=datetime.datetime(
                    2026, 2, 27, 7, 4, 47, 728858, tzinfo=datetime.timezone.utc
                ),
                src=IPv4Address("172.19.0.5"),
                dst=IPv4Address("172.19.0.6"),
                tcp_src_port=PortValue(30099),
                tcp_dst_port=PortValue(37444),
                udp_src_port=PortValue(-1),
                udp_dst_port=PortValue(-1),
                data="0e00330029230000000000004e426b4d744f57536244004e426b4d744f57536244007266726265623834334f0000000000000000000000",
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
            == msgspec.dbmgr.onCreateAccountCBFromInterfaces.name
        )
        assert not msg_data.deserialize_msg_result.result.data_tail

    @pytest.mark.timeout(5)
    async def test_parse_resp_Dbmgr_reqCreateAccount(self, mapping_config_file):
        """Сообщение на Dbmgr::reqCreateAccount.

        Не отображалось.
        """
        ip2comp_type = Ip2ComponentType(Path(mapping_config_file))
        ip2comp_type.load_mapping()
        net_chunk_parser = NetChunk2MsgDataParser(ip2comp_type)

        pcap_file_net_chunk_data = PcapFileNetChunkData(
            pcap_file_stem=PcapFileStem("dbmgr-4001-172.19.0.6"),
            net_chunk_data=NetChunkData(
                time=datetime.datetime(
                    2026, 2, 27, 9, 14, 47, 873399, tzinfo=datetime.timezone.utc
                ),
                src=IPv4Address("172.19.0.11"),
                dst=IPv4Address("172.19.0.6"),
                tcp_src_port=PortValue(54730),
                tcp_dst_port=PortValue(60059),
                udp_src_port=PortValue(-1),
                udp_dst_port=PortValue(-1),
                data="0d00200075736572406578616d706c652e636f6d00000209000000746573745f64617461",
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
            == msgspec.dbmgr.reqCreateAccount.name
        )
        assert not msg_data.deserialize_msg_result.result.data_tail

    @pytest.mark.timeout(5)
    async def test_parse_resp_Cellapp_onLookApp(self, mapping_config_file):
        """Сообщение на Cellapp::onLookApp.

        Не отображалось, т.к. сообщение не было определено отдельно для Cellapp.
        """
        ip2comp_type = Ip2ComponentType(Path(mapping_config_file))
        ip2comp_type.load_mapping()
        net_chunk_parser = NetChunk2MsgDataParser(ip2comp_type)

        pcap_file_net_chunk_data = PcapFileNetChunkData(
            pcap_file_stem=PcapFileStem("cellapp-7001-172.18.0.9"),
            net_chunk_data=NetChunkData(
                time=datetime.datetime(
                    2026, 3, 16, 10, 11, 1, 927543, tzinfo=datetime.timezone.utc
                ),
                src=IPv4Address("172.18.0.9"),
                dst=IPv4Address("172.18.0.9"),
                tcp_src_port=PortValue(36757),
                tcp_dst_port=PortValue(43762),
                udp_src_port=PortValue(-1),
                udp_dst_port=PortValue(-1),
                data="05000000591b00000000000001120100000600000050c30000",
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
            == msgspec.cellapp.onLookApp.name
        )
        assert not msg_data.deserialize_msg_result.result.data_tail
    @pytest.mark.timeout(5)
    async def test_parse_resp_Client_onImportClientMessages(self, mapping_config_file):
        """Сообщение на Cellapp::onImportClientMessages.

        Не отображалось, т.к. оно сырое приходит.
        """
        ip2comp_type = Ip2ComponentType(Path(mapping_config_file))
        ip2comp_type.load_mapping()
        net_chunk_parser = NetChunk2MsgDataParser(ip2comp_type)

        pcap_file_net_chunk_data = PcapFileNetChunkData(
            pcap_file_stem=PcapFileStem("loginapp-9001-172.18.0.11"),
            net_chunk_data=NetChunkData(
                time=datetime.datetime(
                    2026, 3, 16, 11, 4, 48, 263287, tzinfo=datetime.timezone.utc
                ),
                src=IPv4Address("172.18.0.11"),
                dst=IPv4Address("172.18.0.1"),
                tcp_src_port=PortValue(20013),
                tcp_dst_port=PortValue(42766),
                udp_src_port=PortValue(-1),
                udp_dst_port=PortValue(-1),
                data="0602f00c600008000200436c69656e745f6f6e52656c6f67696e426173656170704661696c6564000001030900ffff436c69656e745f6f6e456e746974794c65617665576f726c644f7074696d697a656400ff000a00ffff436c69656e745f6f6e52656d6f74654d6574686f6443616c6c4f7074696d697a656400ff000b00ffff436c69656e745f6f6e55706461746550726f7065727479734f7074696d697a656400ff000c00ffff436c69656e745f6f6e536574456e74697479506f73416e6444697200ff000d000c00436c69656e745f6f6e55706461746542617365506f730000030d0d0d0e00ffff436c69656e745f6f6e5570646174654261736544697200ff000f000800436c69656e745f6f6e55706461746542617365506f73585a0000020d0d1000ffff436c69656e745f6f6e5570646174654461746100ff001100ffff436c69656e745f6f6e557064617465446174615f79707200ff001200ffff436c69656e745f6f6e557064617465446174615f797000ff001300ffff436c69656e745f6f6e557064617465446174615f797200ff001400ffff436c69656e745f6f6e557064617465446174615f707200ff001500ffff436c69656e745f6f6e557064617465446174615f7900ff001600ffff436c69656e745f6f6e557064617465446174615f7000ff001700ffff436c69656e745f6f6e557064617465446174615f7200ff001800ffff436c69656e745f6f6e557064617465446174615f787a00ff001900ffff436c69656e745f6f6e557064617465446174615f787a5f79707200ff001a00ffff436c69656e745f6f6e557064617465446174615f787a5f797000ff001b00ffff436c69656e745f6f6e557064617465446174615f787a5f797200ff001c00ffff436c69656e745f6f6e557064617465446174615f787a5f707200ff001d00ffff436c69656e745f6f6e557064617465446174615f787a5f7900ff001e00ffff436c69656e745f6f6e557064617465446174615f787a5f7000ff001f00ffff436c69656e745f6f6e557064617465446174615f787a5f7200ff002000ffff436c69656e745f6f6e557064617465446174615f78797a00ff002100ffff436c69656e745f6f6e557064617465446174615f78797a5f79707200ff002200ffff436c69656e745f6f6e557064617465446174615f78797a5f797000ff002300ffff436c69656e745f6f6e557064617465446174615f78797a5f797200ff002400ffff436c69656e745f6f6e557064617465446174615f78797a5f707200ff002500ffff436c69656e745f6f6e557064617465446174615f78797a5f7900ff002600ffff436c69656e745f6f6e557064617465446174615f78797a5f7000ff002700ffff436c69656e745f6f6e557064617465446174615f78797a5f7200ff002800ffff436c69656e745f6f6e557064617465446174615f7970725f6f7074696d697a656400ff002900ffff436c69656e745f6f6e557064617465446174615f79705f6f7074696d697a656400ff002a00ffff436c69656e745f6f6e557064617465446174615f79725f6f7074696d697a656400ff002b00ffff436c69656e745f6f6e557064617465446174615f70725f6f7074696d697a656400ff002c00ffff436c69656e745f6f6e557064617465446174615f795f6f7074696d697a656400ff002d00ffff436c69656e745f6f6e557064617465446174615f705f6f7074696d697a656400ff002e00ffff436c69656e745f6f6e557064617465446174615f725f6f7074696d697a656400ff002f00ffff436c69656e745f6f6e557064617465446174615f787a5f6f7074696d697a656400ff003000ffff436c69656e745f6f6e557064617465446174615f787a5f7970725f6f7074696d697a656400ff003100ffff436c69656e745f6f6e557064617465446174615f787a5f79705f6f7074696d697a656400ff003200ffff436c69656e745f6f6e557064617465446174615f787a5f79725f6f7074696d",
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
            == msgspec.client.onImportClientMessages.name
        )
        assert not msg_data.deserialize_msg_result.result.data_tail

