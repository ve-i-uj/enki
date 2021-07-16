"""Tests of the PYTHON encoder / decoder."""

import unittest

from enki import kbetype


class PythonTestCase(unittest.TestCase):
    """Tests for the PYTHON type."""

    def setUp(self):
        super().setUp()
        self._decoder = kbetype.PYTHON

    def test_decode_empty(self):
        """Test of the python type decoding (initial value)."""
        data = memoryview(b'\x04\x00\x00\x00\x80\x03N.')
        value, offset = self._decoder.decode(data)
        self.assertEqual(offset, 8)
        self.assertIsNone(value)

    def test_decode(self):
        """Test of the python type decoding."""
        data = memoryview(b'#\x00\x00\x00\x80\x03}q\x00(X\x01\x00\x00\x00xq\x01K\x01X\x01\x00\x00\x00yq\x02X\x02\x00\x00\x0010q\x03u.')
        value, offset = self._decoder.decode(data)
        self.assertEqual(offset, 39)
        self.assertEqual({'x': 1, 'y': '10'}, value)
