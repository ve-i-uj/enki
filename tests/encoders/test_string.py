"""Tests of FixedDict encoder / decoder."""

import collections
import unittest

from enki import descr, kbetype, kbeenum

from enki.descr.entity import _entity
from enki.descr import _deftype
from enki.kbeclient import serializer


class FixedDictEmptyTestCase(unittest.TestCase):
    """Tests for FixedDict"""

    def setUp(self):
        super().setUp()
        # the real value from KBEngine

        self._fixed_dict = kbetype.FIXED_DICT.build(
            'AVATAR_INFO',
            collections.OrderedDict([
                ('name', kbetype.UNICODE),
                ('uid', kbetype.INT32),
                ('dbid', kbetype.UINT64)
            ])
        )
        self._data = memoryview(b'\x06\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf8\x01\x14\x00\x00\x00\x07\x00\x0ci\xec`\x06\x00\x00\x00Account\x00')

    def test_decode(self):
        """Test FD decoding."""
        value, offset = self._fixed_dict.decode(self._data)
        self.assertNotEqual(offset, 0)
        self.assertIsInstance(value, dict)
        self.assertEqual(len(value), 3)  # three keys
        self.assertEqual(value, {
            'name': '',
            'uid': 0,
            'dbid': 0
        })
