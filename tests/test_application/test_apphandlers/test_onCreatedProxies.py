import unittest

from enki.application import apphandler, entitymgr, appl
from enki import kbeclient, descr, settings
from enki.interface import IMessage, IMsgReceiver


class _MsgReceiver(IMsgReceiver):

    def __init__(self) -> None:
        self.msgs: dict[int, IMessage] = {}

    def on_receive_msg(self, msg: IMessage) -> bool:
        self.msgs[msg.id] = msg


class OnCreatedProxiesTestCase(unittest.TestCase):
    """Test onCreatedProxies"""

    def setUp(self):
        super().setUp()
        data = b'\xff\x01\x0e\x00\x81\x08\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\xf8\x01\x14\x00\x00\x00\x07\x00\x95\x84\xfbb\x81\x08\x00\x00Account\x00'

        login_app_addr = settings.AppAddr('0.0.0.0', 20013)
        self._msg_receiver = _MsgReceiver()
        self._client = kbeclient.Client(login_app_addr)
        self._client.set_msg_receiver(self._msg_receiver)
        self._client.on_receive_data(memoryview(data))

        self._msg: IMessage = self._msg_receiver.msgs.get(
            descr.app.client.onUpdatePropertys.id
        )
        assert self._msg is not None, 'Invalid initial data'

        self._app = appl.App(login_app_addr, server_tick_period=5)
        self._entity_mgr: entitymgr.EntityMgr = entitymgr.EntityMgr(self._app)

    def test_on_update_and_on_created_proxy(self):
        data = b'\xff\x01\x0e\x00\xf3\x00\x00\x00\x00\x04\x02\x00\x00\x00\x00\x00\x00\x00\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00'
        self._client.on_receive_data(memoryview(data))
        msg_511: IMessage = self._msg_receiver.msgs.get(
            descr.app.client.onUpdatePropertys.id
        )
        handler = apphandler.OnUpdatePropertysHandler(self._entity_mgr)
        result: apphandler.HandlerResult = handler.handle(msg_511)

        msg_504: IMessage = self._msg_receiver.msgs.get(
            descr.app.client.onCreatedProxies.id
        )
        handler = apphandler.OnCreatedProxiesHandler(self._entity_mgr)
        result: apphandler.HandlerResult = handler.handle(msg_504)
        assert result.success
