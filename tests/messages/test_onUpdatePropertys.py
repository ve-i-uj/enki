import unittest

from damkina import apphandler, entitymgr, appl
from enki import kbeclient, descr, settings
from enki.interface import IMessage, IMsgReceiver


class _MsgReceiver(IMsgReceiver):

    def __init__(self) -> None:
        self.msgs: dict[int, IMessage] = {}

    def on_receive_msg(self, msg: IMessage) -> bool:
        self.msgs[msg.id] = msg


class OnUpdatePropertysTestCase(unittest.TestCase):
    """Test onUpdatePropertys"""

    def setUp(self):
        super().setUp()

        # msg_id (uint16, два байта) + MESSAGE_LENGTH (UINT16)
        data = b'\xff\x01\x0e\x00\x81\x08\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\xf8\x01\x14\x00\x00\x00\x07\x00\x95\x84\xfbb\x81\x08\x00\x00Account\x00'

        login_app_addr = settings.AppAddr('0.0.0.0', 20013)
        msg_receiver = _MsgReceiver()
        self._client = kbeclient.Client(login_app_addr)
        self._client.set_msg_receiver(msg_receiver)
        self._client.on_receive_data(memoryview(data))

        self._msg: IMessage = msg_receiver.msgs.get(
            descr.app.client.onUpdatePropertys.id
        )
        assert self._msg is not None, 'Invalid initial data'

        self._app = appl.App(login_app_addr, server_tick_period=5)
        self._entity_mgr: entitymgr.EntityMgr = entitymgr.EntityMgr(self._app)

    def test(self):
        self._entity_mgr.initialize_entity(2177, 'Account')
        handler = apphandler.OnUpdatePropertysHandler(self._entity_mgr)
        result: apphandler.HandlerResult = handler.handle(self._msg)
        assert result.success
