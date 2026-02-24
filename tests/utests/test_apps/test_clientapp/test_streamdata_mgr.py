"""Тесты менеджера стрима от Baseapp (сообщений Client::onStreamData*)."""

from enki import msgspec
from enki.apps.clientapp.streamdata_mgr import StreamDataMgr
from enki.msg.msg_serializer import MessageSerializer
from enki.msg_parser.client_msg_parser import (
    OnStreamDataCompletedMsgParser,
    OnStreamDataRecvMsgParser,
    OnStreamDataStartedMsgParser,
)


class TestStreamDataMgr:
    """Тесты менеджера стрима данных от Baseapp на клиент."""

    def test_stream_file(self):
        """Проверка, что стрим из 2-ух чанков работает."""
        stream_data_mgr = StreamDataMgr()

        serializer = MessageSerializer(msgspec.ClientMsgSpecByID)

        data_514 = (
            b"\x02\x02\x15\x00\x01\x00\x1c\x00\x00\x00unittest.data\x00\x01"
        )
        msg_onStreamDataStarted, data_tail = serializer.deserialize(
            memoryview(data_514)
        )
        assert msg_onStreamDataStarted is not None, "Invalid initial data"
        res_onStreamDataStarted = OnStreamDataStartedMsgParser().parse(
            msg_onStreamDataStarted
        )
        assert res_onStreamDataStarted.success is True
        assert res_onStreamDataStarted.result is not None
        pd_onStreamDataStarted = res_onStreamDataStarted.result  # noqa: N806

        data_515 = b"\x03\x02\x14\x00\x01\x00\x0e\x00\x00\x00Unittest data\n"
        msg_onStreamDataRecv, data_tail = serializer.deserialize(  # noqa: N806
            memoryview(data_515)
        )
        assert msg_onStreamDataRecv is not None, "Invalid initial data"
        res_onStreamDataRecv = OnStreamDataRecvMsgParser().parse(  # noqa: N806
            msg_onStreamDataRecv
        )
        assert res_onStreamDataRecv.success is True
        assert res_onStreamDataRecv.result is not None
        pd_onStreamDataRecv = res_onStreamDataRecv.result  # noqa: N806

        data_516 = b"\x04\x02\x01\x00"
        msg_onStreamDataCompleted, _data_tail = serializer.deserialize(
            memoryview(data_516)
        )
        assert msg_onStreamDataCompleted is not None, "Invalid initial data"
        res_onStreamDataCompleted = OnStreamDataCompletedMsgParser().parse(
            msg_onStreamDataCompleted
        )
        assert res_onStreamDataCompleted.success is True
        assert res_onStreamDataCompleted.result is not None
        pd_onStreamDataCompleted = res_onStreamDataCompleted.result

        # Стрим начался
        stream_data_mgr.on_stream_started(
            pd_onStreamDataStarted.stream_id,
            pd_onStreamDataStarted.stream_size,
            pd_onStreamDataStarted.descr,
            pd_onStreamDataStarted.stream_download_type,
        )

        # Стрим отправляет данные
        stream_data_mgr.on_data_received(
            pd_onStreamDataRecv.stream_id, pd_onStreamDataRecv.stream_chunk
        )
        # Стрим отправляет данные второй раз (для проверки чанков)
        stream_data_mgr.on_data_received(
            pd_onStreamDataRecv.stream_id, pd_onStreamDataRecv.stream_chunk
        )

        # Стрим завершился
        stream_data_mgr.on_stream_completed(pd_onStreamDataCompleted.stream_id)

        stream_data = stream_data_mgr.get_and_delete_stream_data(
            pd_onStreamDataStarted.stream_id
        )
        assert stream_data.is_completed is True
        # Данные два чанка
        sent_by_baseapp_data = pd_onStreamDataRecv.stream_chunk * 2
        assert stream_data.result_data == sent_by_baseapp_data
        # Длина такая, как в начале сообщалось
        assert pd_onStreamDataStarted.stream_size == len(sent_by_baseapp_data)
