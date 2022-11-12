"""???"""

import asynctest

from enki.enkitype import AppAddr
from enki.net.kbeclient import MessageSerializer
from enki.app.appl import App
from enki.app.handler import *

from tests.data.demo_descr import description, kbenginexml


class EnkiBaseTestCase(asynctest.TestCase):

    def setUp(self):
        super().setUp()
        login_app_addr = AppAddr('0.0.0.0', 20013)
        self._app = App(
            login_app_addr,
            5,
            description.DESC_BY_UID,
            {},
            kbenginexml.root()
        )
        self._entity_helper = self._app._entity_helper

    def call_OnCreatedProxies(self):
        # entity_id = 2177 (Avatar)
        data = b'\xf8\x01\x13\x00\x00\x00\x07\x00\x95\x84\xfbb\x81\x08\x00\x00Avatar\x00'
        msg_504, _ = MessageSerializer().deserialize(memoryview(data))
        assert msg_504 is not None
        res_504 = OnCreatedProxiesHandler(self._app, self._entity_helper).handle(msg_504)
        assert res_504.success
