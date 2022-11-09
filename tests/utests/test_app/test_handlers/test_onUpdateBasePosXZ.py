import unittest

from enki.app import handler, appl
from enki import kbeclient, settings
from enki.app import ehelper

from tests.utests.base import EnkiBaseTestCase


class OnUpdateBasePosXZTestCase(EnkiBaseTestCase):
    """Test onUpdateBaseXZPos"""

    def test_ok(self):
        data = b'\x0f\x00\x81\xe5@D3#BD'
        msg, data_tail = kbeclient.Serializer().deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        entity = self._entity_mgr.create_entity(199, 'Avatar', True)
        self._entity_mgr.set_player_id(entity.id)

        handler = handler.OnUpdateBasePosXZHandler(self._entity_mgr)
        result: handler.HandlerResult = handler.handle(msg)
        assert result.success
        assert result.result.x == 771.5859985351562
        assert result.result.z == 776.5499877929688
