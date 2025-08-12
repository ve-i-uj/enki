"""Тесты на парсинг сообщений от компонента BaseappMgr."""


from enki import msgspec
from enki.msg.msg_serializer import MessageSerializer
from enki.msg_parser.baseappmgr_msg_parser import OnAppActiveTickMsgParser, OnRegisterNewAppMsgParser
from enki.msgspec import BaseappMgrMsgSpecByID


def normalize_wireshark_data(str_data: str) -> bytes:
    """Конвертирует скопированные из WireShark данные, как "as Hex String"."""
    return bytes.fromhex(str_data)


class TestBaseappMgr_onAppActiveTick:
    """Тесты сообщения BaseappMgr::onAppActiveTick."""
    
    msg_spec = msgspec.baseappmgr.onAppActiveTick
    data = b'A\xd7\n\x00\x00\x00\xd1\x07\x00\x00\x00\x00\x00\x00'
        
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, _data_tail = serializer.deserialize_only_data(memoryview(self.data),
                                                           self.msg_spec.id)
        assert msg is not None
        
        result = OnAppActiveTickMsgParser().parse(msg)
        
        assert result.success is True
        assert result.result is not None

        # Проверка нейминга, чтобы не было опечаток и т.п. 
        assert result.msg_id == self.msg_spec.id
        assert result.__class__.__name__ == \
            f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        assert result.result.__class__.__name__ == \
            f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        assert result.msg_id == self.msg_spec.id


class TestInterfaces_onRegisterNewApp:
    """Тесты сообщения Interfaces::onRegisterNewApp."""
    
    msg_spec = msgspec.baseappmgr.onRegisterNewApp
    data = b'\x08\x00*\x00\xe8\x03\x00\x00root\x00\x04\x00\x00\x00q\x17\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xac\x12\x00\x08\xb6\x17\x00\x00\x00\x00\x00\x00\x00'
        
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(BaseappMgrMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        
        result = OnRegisterNewAppMsgParser().parse(msg)
        
        assert result.success is True
        assert result.result is not None

        # Проверка нейминга, чтобы не было опечаток и т.п. 
        assert result.msg_id == self.msg_spec.id
        assert result.__class__.__name__ == \
            f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        assert result.result.__class__.__name__ == \
            f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        assert result.msg_id == self.msg_spec.id
