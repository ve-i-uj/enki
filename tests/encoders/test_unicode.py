"""Tests of string encoder / decoder."""

import collections
import unittest

from enki import descr, kbetype, kbeenum

from enki.descr.entity import _entity
from enki.descr import deftype
from enki.kbeclient import serializer


class UnicodeEmptyTestCase(unittest.TestCase):
    """Tests for strings."""

    def setUp(self):
        super().setUp()
        self._decoder = kbetype.UNICODE

    def test_decode(self):
        """Test string decoding."""
        data = memoryview(b'\r\x00\x00\x00default_value')
        value, offset = self._decoder.decode(data)
        self.assertEqual(offset, 17)
        self.assertIsInstance(value, str)
        self.assertEqual(value, 'default_value')

    def test_decode_empty(self):
        """Test empty string decoding."""
        data = memoryview(b'\x00\x00\x00\x00')
        value, offset = self._decoder.decode(data)
        self.assertEqual(offset, 4)
        self.assertIsInstance(value, str)
        self.assertEqual(value, '')
