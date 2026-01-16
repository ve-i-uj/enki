"""Тесты десериализаторов MsgReader."""

from enki import msgspec
from tools.msgreader.readers.deserializers import (
    deserialize_msg_without_id_and_len,
)
from tools.msgreader.readers.hex_str_to_bytes import normalize_wireshark_data


class TestDeserializeMsg:

    def test_tail_error(self):
        """Тест ситуации, когда остаётся хвост от сообщения."""
        # Это Machine::onLookApp
        str_data = "08000000010000000000000001"
        data = normalize_wireshark_data(str_data)
        result = deserialize_msg_without_id_and_len(
            data, msgspec.machine.onLookApp.name
        )
        assert not result.result.data_tail
