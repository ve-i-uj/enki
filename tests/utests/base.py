"""???"""

from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock

from enki.apps.clientapp.clienthandler import *
from enki.apps.clientapp.clienthandler.ehelper import EntityHelper

from enki.apps.clientapp.layer import ilayer
from enki.net.client import MessageEncoder
from tests.data.descr import description, eserializer, kbenginexml


class EnkiBaseTestCase(IsolatedAsyncioTestCase):
    def setUp(self):
        super().setUp()
        ilayer.init(MagicMock(), MagicMock())
        self._entity_helper = EntityHelper(
            description.DESC_BY_UID,
            {
                cls.ENTITY_CLS_ID: cls
                for cls in eserializer.SERIAZER_BY_ECLS_NAME.values()
            },
            kbenginexml.root(),
        )

    def call_OnCreatedProxies(self):
        # entity_id = 2177 (Avatar)
        data = b"\xf8\x01\x13\x00\x00\x00\x07\x00\x95\x84\xfbb\x81\x08\x00\x00Avatar\x00"
        msg_504, _ = MessageEncoder(msgspec.client.SPEC_BY_ID).deserialize(
            memoryview(data)
        )
        assert msg_504 is not None
        res_504 = OnCreatedProxiesHandler(self._entity_helper).handle(msg_504)
        assert res_504.success
