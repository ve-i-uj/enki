"""Тесты сообщений компонента Machine."""

import unittest

from enki.core import msgspec
from enki.net.client import MessageSerializer

from tools.msgreader import normalize_wireshark_data


class onBroadcastInterfaceTestCase(unittest.TestCase):

    def test_ok(self):
        hex_data = '08007100c76e0000726f6f74000a000000000005d4eb384f640100000000000000ffffffffffffffffffffffffac190003b9b1ac190003c56700bb000000000000000000000000201e010000000000000000000000000000000000000000000000000000000000d084000000000000ac190003504b'
        data = normalize_wireshark_data(hex_data)
        serializer = MessageSerializer(msgspec.app.machine.SPEC_BY_ID)
        msg, data_tail = serializer.deserialize(memoryview(data))

        assert msg is not None
        assert msg.id == msgspec.app.machine.onBroadcastInterface.id
        assert not data_tail
