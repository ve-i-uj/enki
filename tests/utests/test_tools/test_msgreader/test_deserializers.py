"""Тесты десериализаторов MsgReader."""

from enki import msgspec
from tools.msgreader.readers.deserializers import (
    deserialize_msg_without_id_and_len,
)


class TestDeserializeMsg:

    def test_tail_error(self):
        """Тест ситуации, когда остаётся хвост от сообщения."""
        # Это Machine::onLookApp
        str_data = "08000000010000000000000001"
        result = deserialize_msg_without_id_and_len(
            str_data, msgspec.machine.onLookApp.name
        )
        assert not result.result.data_tail
