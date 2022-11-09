"""Tests of the PYTHON encoder / decoder."""

import unittest

from enki.net.kbeclient import kbetype


class Vector2TestCase(unittest.TestCase):
    """Tests for the VECTOR2 type."""

    def setUp(self):
        super().setUp()
        self._decoder = kbetype.VECTOR2

    def test_decode_empty(self):
        """Test of the VECTOR2 type decoding (initial value)."""
        data = memoryview(b'\x00\x00\x00\x00\x00\x00\x00\x00')
        value, offset = self._decoder.decode(data)
        self.assertEqual(offset, 8)
        self.assertEqual(kbetype.Vector2Data(0.0, 0.0), value)

    def test_decode(self):
        """Test of the VECTOR2 type decoding."""
        data = memoryview(b'\x00\x00\x80?\x00\x00\x00@')
        value, offset = self._decoder.decode(data)
        self.assertEqual(offset, 8)
        self.assertEqual(kbetype.Vector2Data(1.0, 2.0), value)
