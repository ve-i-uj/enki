"""Tests of FixedDict encoder / decoder."""

import collections
import unittest

from enki import kbetype


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

    def test_decode_empty(self):
        """Test empty FD decoding."""
        data = memoryview(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        value, offset = self._fixed_dict.decode(data)
        self.assertNotEqual(offset, 0)
        self.assertIsInstance(value, dict)
        self.assertEqual(len(value), 3)  # three keys
        self.assertEqual({'name': '', 'uid': 0, 'dbid': 0}, value)

    def test_decode(self):
        """Test FD decoding."""
        data = memoryview(b'\x06\x00\x00\x00QWERTY\x01\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00')
        value, offset = self._fixed_dict.decode(data)
        self.assertNotEqual(offset, 0)
        self.assertIsInstance(value, dict)
        self.assertEqual(len(value), 3)  # three keys
        self.assertEqual({'name': 'QWERTY', 'uid': 1, 'dbid': 2}, value)
