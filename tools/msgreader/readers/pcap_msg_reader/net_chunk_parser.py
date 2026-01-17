"""Parser for converting network chunks to deserialized message data."""

from __future__ import annotations

import logging
from asyncio import CancelledError, Event
from collections import deque
from ipaddress import IPv4Address
from typing import TYPE_CHECKING, Self

from enki import msgspec
from enki.kbeenum import ComponentType
from enki.misc import devonly
from tools.msgreader.readers.deserializers import (
    deserialize_msg,
    deserialize_msg_without_id_and_len,
)
from tools.msgreader.readers.hex_bites_reader import normalize_wireshark_data

from .msg_data import MsgData

if TYPE_CHECKING:
    from tools.msgreader.readers.pcap_msg_reader.ip2component import (
        Ip2ComponentType,
    )
    from tools.msgreader.readers.pcap_msg_reader.pcap_file_chunker.net_chunk_consumer import (
        PcapFileNetChunkData,
    )

logger = logging.getLogger(__name__)


class NetChunk2MsgDataParser:
    """Service that produces deserialized KBEngine messages from packet data.

    This parser processes network chunks from pcap files and converts them
    into structured message data with component type information.
    """

    def __init__(self, ip2component_type: Ip2ComponentType) -> None:
        """Initialize the parser.

        Args:
            ip2component_type: Mapping from IP addresses to component types.

        """
        self._ip2component_type = ip2component_type
        self._msgs_data: deque[MsgData] = deque()
        self._stoped = False
        self._stoped_event = Event()

    def parse(self, pcap_file_net_chunk_data: PcapFileNetChunkData) -> None:
        """Parse a network chunk and store the resulting message data.

        Args:
            pcap_file_net_chunk_data: Container with network chunk data
                and associated file metadata.

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        net_chunk_data = pcap_file_net_chunk_data.net_chunk_data
        host_ip_addr = pcap_file_net_chunk_data.pcap_file_stem.host_ip_addr
        str_data = pcap_file_net_chunk_data.net_chunk_data.data
        component_id = pcap_file_net_chunk_data.pcap_file_stem.component_id

        data = normalize_wireshark_data(str_data)

        comp_type = ComponentType.UNKNOWN_COMPONENT

        host_comp_type = self._ip2component_type.get_component_type_by_ip_addr(
            host_ip_addr
        )
        if host_comp_type.is_unknow:
            logger.warning(
                "[%s] The component type of the host ip '%s' is unknown. Check "
                "the mapping config. Skip parsing",
                self,
                host_ip_addr,
            )
            return

        src_comp_type = self._ip2component_type.get_component_type_by_ip_addr(
            net_chunk_data.src
        )
        dst_comp_type = self._ip2component_type.get_component_type_by_ip_addr(
            net_chunk_data.dst
        )

        comp_type_in_filename = (
            pcap_file_net_chunk_data.pcap_file_stem.component_type
        )

        # Sanity check to prevent confusion between file variables.
        # Ensure the component name in the filename matches its IP mapping.
        if comp_type_in_filename != host_comp_type:
            logger.warning(
                "[%s] The component type in the mapping file ('%s') and the "
                "component type by ip from file ('%s') are not equal. Check "
                "the mapping config. Skip parsing",
                self,
                comp_type_in_filename,
                host_comp_type,
            )
            return

        if host_ip_addr == net_chunk_data.dst:
            # Incoming message to the component. The message serializer
            # is needed for the component where the pcap file was captured.
            comp_type = comp_type_in_filename
        elif net_chunk_data.dst == IPv4Address("255.255.255.255"):
            # This could be a broadcast message within the container.
            # Broadcast messages are sent to Machine/Supervisor during service startup.
            # Switch serializer to Machine component.
            comp_type = ComponentType.SUPERVISOR
        else:
            # This can only be an outgoing message to another component.
            # Find which component it is by its IP address.
            comp_type = self._ip2component_type.get_component_type_by_ip_addr(
                net_chunk_data.dst
            )

        result = deserialize_msg(data, comp_type)
        if not result.success:
            # This might be a message without envelope containing msgId.
            # Try to read it "bare". There aren't many such messages.
            msgs = (
                msgspec.machine.onLookApp,
                msgspec.machine.queryComponentID,
                msgspec.machine.onBroadcastInterface,
            )
            for msg in msgs:
                result = deserialize_msg_without_id_and_len(data, msg.name)
                if result.success and not result.result.data_tail:
                    logger.debug(
                        "[%s] The message without envelope has been parsed",
                        self,
                    )
                    break

            # Если не получилось и назначение Logger, то это может быть
            # Logger::writeLog в нескольких пакетах.
            if not result.success and dst_comp_type == ComponentType.LOGGER:
                logger.debug(
                    "[%s] The data cannot be decoded. Logger::writeLog? (data = '%s')",
                    self,
                    data,
                )
                return

        if not result.success:
            logger.warning(
                "[%s] The message cannot be parsed. Logic error! "
                "(comp_type = %s, data = %s)",
                self,
                comp_type.name,
                data,
            )

        msg_data = MsgData(
            host_comp_type,
            src_comp_type,
            dst_comp_type,
            result,
            net_chunk_data,
            component_id,
        )
        self._msgs_data.append(msg_data)

        self._stoped_event.set()

    def stop(self) -> None:
        """Signal the iterator to stop.

        This method should be called when no more data will be added
        to the parser, allowing the async iterator to complete.
        """
        self._stoped = True
        self._stoped_event.set()

    def __aiter__(self) -> Self:
        """Return the async iterator instance.

        Returns:
            The parser instance itself, which is also an async iterator.

        """
        return self

    async def __anext__(self) -> MsgData:
        """Get the next parsed message asynchronously.

        Returns:
            The next MsgData object from the parsed messages queue.

        Raises:
            StopAsyncIteration: When there are no more messages and
                stop() has been called.

        """
        if self._msgs_data:
            return self._msgs_data.popleft()

        if self._stoped:
            raise StopAsyncIteration

        self._stoped_event.clear()

        try:
            await self._stoped_event.wait()
        except CancelledError as err:
            raise StopAsyncIteration from err

        return await self.__anext__()

    def __str__(self) -> str:
        """String representation of the parser instance."""
        return f"{self.__class__.__name__}()"
