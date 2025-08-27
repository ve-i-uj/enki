"""Tests of the PYTHON encoder / decoder."""

import unittest

from enki.kbetype.decoders.basic_data_type_decoders import VECTOR2
from enki.kbetype.pytypes.vectors import Vector2


class Vector2TestCase(unittest.TestCase):
    """Tests for the VECTOR2 type."""

    def setUp(self):
        super().setUp()
        self._decoder = VECTOR2

    def test_decode_empty(self):
        """Test of the VECTOR2 type decoding (initial value)."""
        data = memoryview(b"\x00\x00\x00\x00\x00\x00\x00\x00")
        value, offset = self._decoder.decode(data)
        assert offset == 8
        assert Vector2(0.0, 0.0) == value

    def test_decode(self):
        """Test of the VECTOR2 type decoding."""
        data = memoryview(b"\x00\x00\x80?\x00\x00\x00@")
        value, offset = self._decoder.decode(data)
        assert offset == 8
        assert Vector2(1.0, 2.0) == value
