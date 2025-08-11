"""Тесты на парсинг сообщений от компонента DBMgr."""


from enki import msgspec
from enki.msg.msg_serializer import MessageSerializer
from enki.msg_parser.dbmgr_msg_parser import OnAppActiveTickMsgParser, OnRegisterNewAppMsgParser
from enki.msgspec import DBMgrMsgSpecByID


def normalize_wireshark_data(str_data: str) -> bytes:
    """Конвертирует скопированные из WireShark данные, как "as Hex String"."""
    return bytes.fromhex(str_data)


class TestDBMgr_onAppActiveTick:
    """Тесты сообщения DBMgr::onAppActiveTick."""
    
    msg_spec = msgspec.dbmgr.onAppActiveTick
    data = b'A\xd7\n\x00\x00\x00\xd1\x07\x00\x00\x00\x00\x00\x00'
        
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
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
    
    msg_spec = msgspec.dbmgr.onRegisterNewApp
    data = b'\x08\x00*\x00\xe8\x03\x00\x00root\x00\r\x00\x00\x00\xb9\x0b\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xac\x12\x00\x05u\x93\x00\x00\x00\x00\x00\x00\x00'
        
    def test_success(self):
        """Удачный парсинг сообщения."""
        serializer = MessageSerializer(DBMgrMsgSpecByID)
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
