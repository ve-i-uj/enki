import unittest

from enki.app import handlers, appl
from enki import kbeclient, descr, kbetype, settings
from enki.app.managers import entitymgr
from enki.interface import IMessage, IMsgReceiver
from enki.app.handlers.ehandler import _OptimizedXYZReader

from tests.utests import base


class OnUpdateData_xz_optimizedTestCase(base.EnkiTestCaseBase):
    """Test onUpdateData_xz_optimized"""

    def test_ok(self):
        pass
