from enki import interface
from enki.kbeclient import Serializer
from enki.app.appl import App
from enki.app.handlers import *

import asynctest

from tests.data import demo_descr, entities


class EnkiBaseTestCase(asynctest.TestCase):

    def setUp(self):
        super().setUp()
        login_app_addr = interface.AppAddr('0.0.0.0', 20013)
        self._app = App(
            login_app_addr, 5, demo_descr.entity.DESC_BY_UID,
            entities.ENTITY_BY_UID,
            demo_descr.kbenginexml.root()
        )
        self._app._connected = True
        self._entity_mgr = self._app._entity_mgr

    def call_OnCreatedProxies(self):
        # entity_id = 2177 (Avatar)
        data = b'\xf8\x01\x13\x00\x00\x00\x07\x00\x95\x84\xfbb\x81\x08\x00\x00Avatar\x00'
        msg_504, _ = Serializer().deserialize(memoryview(data))
        assert msg_504 is not None
        res_504 = OnCreatedProxiesHandler(self._entity_mgr).handle(msg_504)
        assert res_504.success
