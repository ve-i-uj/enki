"""Тесты для парсеров собщений компонента Loginapp."""

from enki import msgspec
from enki.msg.msg_serializer import MessageSerializer
from enki.msgspec import LoginappMsgSpecByID
from enki.msg_parser.loginapp_msg_parser import OnAppActiveTickMsgParser, OnBaseappInitProgressMsgParser, OnDbmgrInitCompletedMsgParser


class TestOnDbmgrInitCompletedTestCase:
    
    data = b'\x0e\x00)\x00\x05\x00\x00\x00\x01\x00\x00\x0006E15F102B481ACF8CA19E2F410D1B64\x00'
    msg_spec = msgspec.loginapp.onDbmgrInitCompleted
    
    def test_onDbmgrInitCompleted(self):
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        
        res = OnDbmgrInitCompletedMsgParser().parse(msg)
        
        assert res.success is True
        assert res.result is not None

        # Проверка нейминга, чтобы не было опечаток и т.п. 
        assert res.msg_id == self.msg_spec.id
        assert res.__class__.__name__ == \
            f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        assert res.result.__class__.__name__ == \
            f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        assert res.msg_id == self.msg_spec.id

        pd = res.result

        assert pd.startID == 1
        assert pd.endID == 826619440
        assert pd.startGlobalOrder == 808535605
        assert pd.startGroupOrder == 942948914
        assert pd.digest == "1ACF8CA19E2F410D1B64"


class TestOnBaseappInitProgressTestCase:
    
    data = b'\x18\x00\x00\x00\xc8B'
    msg_spec = msgspec.loginapp.onBaseappInitProgress

    def test_OnBaseappInitProgressHandler(self):
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        
        res = OnBaseappInitProgressMsgParser().parse(msg)
        
        assert res.success is True
        assert res.result is not None

        # Проверка нейминга, чтобы не было опечаток и т.п. 
        assert res.msg_id == self.msg_spec.id
        assert res.__class__.__name__ == \
            f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        assert res.result.__class__.__name__ == \
            f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        assert res.msg_id == self.msg_spec.id

        pd = res.result

        assert pd.progress == 100.0


class OnAppActiveTickTestCase:

    data = b'B\xd7\n\x00\x00\x00\xd1\x07\x00\x00\x00\x00\x00\x00'
    msg_spec = msgspec.loginapp.onAppActiveTick

    def test_OnAppActiveTickHandler(self):
        serializer = MessageSerializer(LoginappMsgSpecByID)
        msg, _data_tail = serializer.deserialize(memoryview(self.data))
        assert msg is not None
        
        res = OnAppActiveTickMsgParser().parse(msg)
        
        assert res.success is True
        assert res.result is not None

        # Проверка нейминга, чтобы не было опечаток и т.п. 
        assert res.msg_id == self.msg_spec.id
        assert res.__class__.__name__ == \
            f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}MsgParserResult"
        assert res.result.__class__.__name__ == \
            f"{self.msg_spec.short_name[0].upper() + self.msg_spec.short_name[1:]}ParsedMsgData"
        assert res.msg_id == self.msg_spec.id

        pd = res.result

        assert pd.componentType == 10
        assert pd.componentID == 2001
