import unittest

from enki.app import handler, appl
from enki import settings
from enki.net import kbeclient, msgspec

from enki.app import ehelper
from enki.interface import IMessage, IMsgReceiver

from tests.utests.base import EnkiBaseTestCase


class OnSetEntityPosAndDirTestCase(EnkiBaseTestCase):
    """Test onSetEntityPosAndDir"""

    async def test_ok(self):
        data = b'\x0c\x00\x1c\x00\xc7\x00\x00\x00\x81\xe5@D\x83\x00SC3#BD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfd\x01\t\x00\xc7\x00\x00\x00\x01\x00\x00\x00\x00'
        msg, data_tail = kbeclient.MessageSerializer().deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        self._entity_mgr.create_entity(199, 'Avatar', True)
        handler = handler.OnSetEntityPosAndDirHandler(self._entity_mgr)
        result: handler.HandlerResult = handler.handle(msg)
        assert result.success
        assert result.result.direction.x == 0
        assert result.result.direction.y == 0
        assert result.result.direction.z == 0
        assert result.result.position.x != 0
        assert result.result.position.y != 0
        assert result.result.position.z != 0
