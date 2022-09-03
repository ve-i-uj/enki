"""Tests of string encoder / decoder."""

import unittest

from enki import kbetype


class StringTestCase(unittest.TestCase):
    """Tests for strings."""

    def setUp(self):
        super().setUp()
        self._decoder = kbetype.STRING

    def test_decode(self):
        """Test string decoding."""
        data = memoryview(b'2.5.10\x00')
        value, offset = self._decoder.decode(data)
        self.assertEqual(offset, 7)
        self.assertIsInstance(value, str)
        self.assertEqual(value, '2.5.10')

    def test_decode_empty(self):
        """Test empty string decoding."""
        data = memoryview(b'\x00')
        value, offset = self._decoder.decode(data)
        self.assertEqual(offset, 1)
        self.assertIsInstance(value, str)
        self.assertEqual(value, '')
