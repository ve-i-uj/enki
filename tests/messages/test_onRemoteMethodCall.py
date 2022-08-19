import unittest

from damkina import apphandler, entitymgr, appl
from enki import kbeclient, descr, settings, kbetype
from enki.interface import IMessage, IMsgReceiver


class _MsgReceiver(IMsgReceiver):

    def __init__(self) -> None:
        self.msgs: dict[int, IMessage] = {}

    def on_receive_msg(self, msg: IMessage) -> bool:
        self.msgs[msg.id] = msg


class OnRemoteMethodCallHandlerTestCase(unittest.TestCase):
    """Test onRemoteMethodCallHandler"""

    def setUp(self):
        super().setUp()
        data = b'\xfa\x01\n\x00\xbf\x00\x00\x00\x00\x03\x00\x00\x00\x00'
        login_app_addr = settings.AppAddr('0.0.0.0', 20013)
        msg_receiver = _MsgReceiver()
        self._client = kbeclient.Client(login_app_addr)
        self._client.set_msg_receiver(msg_receiver)
        self._client.on_receive_data(memoryview(data))

        self._msg: IMessage = msg_receiver.msgs.get(
            descr.app.client.onRemoteMethodCall.id
        )
        assert self._msg is not None, 'Invalid initial data'

        self._app = appl.App(login_app_addr, server_tick_period=5)
        self._entity_mgr: entitymgr.EntityMgr = entitymgr.EntityMgr(self._app)

    def test_ok(self):
        data, *_ = self._msg.get_values()
        entity_id, _ = kbetype.ENTITY_ID.decode(data)
        self._entity_mgr.initialize_entity(entity_id, 'Account')
        handler = apphandler.OnRemoteMethodCallHandler(self._entity_mgr)
        result: apphandler.HandlerResult = handler.handle(self._msg)
        assert result.success
