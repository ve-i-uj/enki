"""Тесты парсинга сообщения Client::onCreatedProxies."""

from enki import msgspec
from enki.msg.msg_serializer import MessageSerializer
from enki.msg_parser.client_msg_parser.entity_msg_parser import (
    OnCreatedProxiesMsgParser,
)


class TestOnCreatedProxies:
    """Test Client::onCreatedProxies."""

    data = (
        b"\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00"
    )
    msg_spec = msgspec.client.onCreatedProxies

    async def test_on_created_proxy_no_components(self):
        serializer = MessageSerializer(msgspec.ClientappMsgSpecByID)
        msg, _ = serializer.deserialize(memoryview(self.data))
        assert msg is not None, "Invalid initial data"

        res = OnCreatedProxiesMsgParser().parse(msg)

        assert res.success is True
        assert res.result is not None

        assert res.result.entity_cls_name == "Account"
        assert res.result.entity_id == 243

        # Проверка нейминга, чтобы не было опечаток и т.п.
        assert (
            res.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        )
        assert (
            res.result.__class__.__name__
            == f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        )
        assert res.msg_id == self.msg_spec.id
