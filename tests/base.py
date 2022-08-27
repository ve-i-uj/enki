import unittest

from enki import settings
from enki.kbeclient import Serializer
from enki.app.entitymgr import EntityMgr
from enki.app.appl import App
from enki.app.handlers import *


class EnkiTestCaseBase(unittest.TestCase):

    def setUp(self):
        super().setUp()
        login_app_addr = settings.AppAddr('0.0.0.0', 20013)
        self._app = App(login_app_addr, server_tick_period=5)
        self._entity_mgr = EntityMgr(self._app)

    def call_OnCreatedProxies(self):
        data = b'\xf8\x01\x13\x00\x00\x00\x07\x00\x95\x84\xfbb\x81\x08\x00\x00Avatar\x00'
        msg_504, _ = Serializer().deserialize(memoryview(data))
        assert msg_504 is not None
        res_504 = OnCreatedProxiesHandler(self._entity_mgr).handle(msg_504)
        assert res_504.success
