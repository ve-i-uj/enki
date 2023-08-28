"""Tests of FixedDict encoder / decoder."""

import collections
import unittest

from enki.core import kbetype


class FixedDictTypeEmptyTestCase(unittest.TestCase):
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
        self.assertIsInstance(value, kbetype.FixedDict)
        self.assertEqual(len(value), 3)  # three keys
        self.assertEqual({'name': '', 'uid': 0, 'dbid': 0}, value)

    def test_decode(self):
        """Test FD decoding."""
        data = memoryview(b'\x06\x00\x00\x00QWERTY\x01\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00')
        value, offset = self._fixed_dict.decode(data)
        self.assertNotEqual(offset, 0)
        self.assertIsInstance(value, kbetype.FixedDict)
        self.assertEqual(len(value), 3)  # three keys
        self.assertEqual({'name': 'QWERTY', 'uid': 1, 'dbid': 2}, value)


class FixedDictInitTestCase(unittest.TestCase):
    """Initialization of FixedDict"""

    def setUp(self):
        super().setUp()

    def test_negative_no_args(self):
        with self.assertRaises(TypeError):
            kbetype.FixedDict()

    def test_init(self):
        fd = kbetype.FixedDict('UNITTEST_TYPE',
                               collections.OrderedDict([('x', 0), ('y', 0)]))
        self.assertEqual(fd._data, collections.OrderedDict([('x', 0), ('y', 0)]))

    def test_fd_is_plugin_type(self):
        """FixedDict should be a plugin type."""
        fd = kbetype.FixedDict('UNITTEST_TYPE',
                               collections.OrderedDict([('x', 0), ('y', 0)]))
        self.assertIsInstance(fd, kbetype.EnkiType)

    def test_negative_init_dict(self):
        """Dict in constructor."""
        with self.assertRaises(TypeError):
            kbetype.FixedDict('UNITTEST_TYPE', {'name': '', 'uid': 0, })


class FixedDictUpdateTestCase(unittest.TestCase):
    """Tests of FixedDict updating."""

    def test_change_value(self):
        fd = kbetype.FixedDict('UNITTEST_TYPE', collections.OrderedDict([
            ('name', 'name'),
            ('uid', 123),
            ('dbid', 56)
        ]))
        fd['uid'] = 0
        self.assertEqual(fd._data, collections.OrderedDict([
            ('name', 'name'),
            ('uid', 0),
            ('dbid', 56)
        ]))

    def test_negative_invalid_value_type(self):
        fd = kbetype.FixedDict('UNITTEST_TYPE', collections.OrderedDict([
            ('name', 'name'),
            ('uid', 123),
            ('dbid', 56)
        ]))
        with self.assertRaises(KeyError):
            fd['uid'] = 'string'
        # Values is the same
        self.assertEqual(fd._data, collections.OrderedDict([
            ('name', 'name'),
            ('uid', 123),
            ('dbid', 56)
        ]))
