"""Container for deserialized KBEngine-message metadata and data."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from enki.kbeenum import ComponentType
    from tools.msgreader.readers.deserializers import (
        DeserializeMsgResult,
    )
    from tools.msgreader.readers.pcap_msg_reader.net_chunk.net_chunk import (
        NetChunkData,
    )

logger = logging.getLogger(__name__)


@dataclass
class MsgData:
    """Container for deserialized message metadata and data."""

    host_comp_type: ComponentType
    src_comp_type: ComponentType
    dst_comp_type: ComponentType
    deserialize_msg_result: DeserializeMsgResult
    net_chunk_data: NetChunkData
    component_id: int
