import unittest

from enki.app import handler, appl
from enki import kbeclient, msgspec, settings
from enki.app import ehelper
from enki.interface import IMessage, IMsgReceiver
from enki.app.handler.ehandler import _OptimizedXYZReader
from enki.net.kbeclient import kbetype

from tests.utests import base


class OnUpdateData_xz_optimizedTestCase(base.EnkiBaseTestCase):
    """Test onUpdateData_xz_optimized"""

    def test_ok(self):
        pass
