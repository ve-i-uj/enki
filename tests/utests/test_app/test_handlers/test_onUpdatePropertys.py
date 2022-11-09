import asyncio
import unittest

import pytest

from enki.app import handler, appl
from enki import settings
from enki.net import kbeclient, msgspec

from enki.app import ehelper
from enki.interface import IMessage, IMsgReceiver

from tests.utests.base import EnkiBaseTestCase


class OnUpdatePropertysTestCase(EnkiBaseTestCase):
    """Test onUpdatePropertys"""

    async def test_ok(self):
        data = b'\xff\x01\x0e\x00\x81\x08\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\xf8\x01\x14\x00\x00\x00\x07\x00\x95\x84\xfbb\x81\x08\x00\x00Account\x00'
        msg, data_tail = kbeclient.MessageSerializer().deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        self._entity_mgr.create_entity(2177, 'Account', True)
        handler = handler.OnUpdatePropertysHandler(self._entity_mgr)
        result: handler.HandlerResult = handler.handle(msg)
        assert result.success

    async def test_on_update_before_on_created_proxy(self):
        data = b'\xff\x01\x0e\x00\xf3\x00\x00\x00\x00\x04\x02\x00\x00\x00\x00\x00\x00\x00\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00'
        msg_511, data = kbeclient.MessageSerializer().deserialize(memoryview(data))
        msg_504, data_tail = kbeclient.MessageSerializer().deserialize(memoryview(data))
        assert msg_511 and msg_504, 'Invalid initial data'

        handler.OnUpdatePropertysHandler(self._entity_mgr).handle(msg_511)

        handler = handler.OnCreatedProxiesHandler(self._entity_mgr)
        result: handler.HandlerResult = handler.handle(msg_504)
        assert result.success
