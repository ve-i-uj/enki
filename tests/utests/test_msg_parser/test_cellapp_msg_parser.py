
from enki import msgspec
from enki.msg.msg_serializer import MessageSerializer
from enki.msg_parser.cellapp_msg_parser import (
    OnBroadcastGlobalDataChangedMsgParser,
    OnCreateCellEntityFromBaseappMsgParser,
    OnDbmgrInitCompletedMsgParser,
)
from enki.msgspec import CellappMsgSpecByID


def normalize_wireshark_data(str_data: str) -> bytes:
    """Конвертирует скопированные из WireShark данные, как "as Hex String"."""
    return bytes.fromhex(str_data)


class TestCellapp_OnBroadcastGlobalDataChanged:

    msg_spec = msgspec.cellapp.onBroadcastGlobalDataChanged
    data = b"\x0e\x00E\x00\x00\x0c\x00\x00\x00VSpaces\np0\n.0\x00\x00\x00c_upf\nEntityCall\np0\n(I2001\nI7001\nI8\nI1\ntp1\nRp2\n."

    def test_onBroadcastGlobalDataChanged(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

        res = OnBroadcastGlobalDataChangedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        assert not res.result.isDelete
        assert res.result.key == "Spaces"
        assert res.result.value is not None


class TestCellapp_OnCreateCellEntityFromBaseapp:

    msg_spec = msgspec.cellapp.onCreateCellEntityFromBaseapp
    data = b"\x13\x00v\x00\xd3\x07\x00\x00SpawnPoint\x00\xe6\x07\x00\x00A\x1f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00@\x9cF\xae\x80\xc2\xc0<:CD$\xf2\xc2\x00\x00A\x9c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00.\xa0\x00\x00\x00\x00\x00\x00/\xa0\x01\x00\x00+\xa0\x00\x00\x00\x00\x00\x00>\x00\xec\x03\x00\x00\x00\x00,\xa0\x00\x00\x00\x00\x00\x00-\xa0\x00\x00\x00\x00"

    def test_onBroadcastGlobalDataChanged(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        # msg, _data_tail = serializer.deserialize_only_data(memoryview(self.data), self.msg_spec.id)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

        res = OnCreateCellEntityFromBaseappMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        pd = res.result

        assert pd.componentID == 8001
        assert pd.createToEntityID == 2003
        assert pd.entityID == 2022
        assert pd.entityType == "SpawnPoint"
        assert not pd.hasClient
        assert not pd.inRescore


class TestCellapp_onDbmgrInitCompleted:

    data = b"\r\x005\x00;\x0c\x00\x00\x01\x00\x00\x00\xd1\x07\x00\x00\x03\x00\x00\x00\x01\x00\x00\x0097FD10D9C332339BAE53A765BF8E35AA\x00"
    msg_spec = msgspec.cellapp.onDbmgrInitCompleted

    def test_onDbmgrInitCompleted(self):
        serializer = MessageSerializer(CellappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None

        res = OnDbmgrInitCompletedMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        pd = res.result

        assert pd.gametime == 3131
        assert pd.startID == 1
        assert pd.endID == 2001
        assert pd.startGlobalOrder == 3
        assert pd.startGroupOrder == 1
        assert pd.digest == "97FD10D9C332339BAE53A765BF8E35AA"
