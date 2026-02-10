"""Tests for encoder/decoder of PYTHON KBEngine types."""

import math
import struct

from enki.kbetype.decoders.basic_data_type_decoders import (
    VECTOR2,
    VECTOR3,
    VECTOR4,
)
from enki.kbetype.pytypes.basic_data_types import (
    KBEVector2,
    KBEVector3,
    KBEVector4,
)


class TestKBEVector2:
    """Tests for the VECTOR2 type."""

    def test_decode_empty(self):
        """Test VECTOR2 type decoding (initial/zero values)."""
        data = memoryview(b"\x00\x00\x00\x00\x00\x00\x00\x00")
        value, offset = VECTOR2.decode(data)
        assert offset == 8
        assert KBEVector2(0.0, 0.0) == value

    def test_decode(self):
        """Test VECTOR2 type decoding."""
        data = memoryview(b"\x00\x00\x80?\x00\x00\x00@")
        value, offset = VECTOR2.decode(data)
        assert offset == 8
        assert KBEVector2(1.0, 2.0) == value

    def test_encode(self):
        """Test VECTOR2 type encoding."""
        vector = KBEVector2(1.0, 2.0)
        encoded = VECTOR2.encode(vector)
        expected = struct.pack("ff", 1.0, 2.0)
        assert encoded == expected

    def test_encode_empty(self):
        """Test VECTOR2 type encoding with zero values."""
        vector = KBEVector2(0.0, 0.0)
        encoded = VECTOR2.encode(vector)
        expected = struct.pack("ff", 0.0, 0.0)
        assert encoded == expected

    def test_encode_decode_roundtrip(self):
        """Test VECTOR2 encode/decode roundtrip."""
        original = KBEVector2(3.14, -2.71)
        encoded = VECTOR2.encode(original)
        decoded, offset = VECTOR2.decode(memoryview(encoded))
        assert offset == 8

        # Compare with tolerance for floating-point precision
        assert math.isclose(decoded.x, original.x, rel_tol=1e-6)
        assert math.isclose(decoded.y, original.y, rel_tol=1e-6)


class TestKBEVector3:
    """Tests for the VECTOR3 type."""

    def test_decode_empty(self):
        """Test VECTOR3 type decoding (initial/zero values)."""
        data = memoryview(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        value, offset = VECTOR3.decode(data)
        assert offset == 12
        assert KBEVector3(0.0, 0.0, 0.0) == value

    def test_decode(self):
        """Test VECTOR3 type decoding."""
        data = memoryview(b"\x00\x00\x80?\x00\x00\x00@\x00\x00@@")
        value, offset = VECTOR3.decode(data)
        assert offset == 12
        assert KBEVector3(1.0, 2.0, 3.0) == value

    def test_encode(self):
        """Test VECTOR3 type encoding."""
        vector = KBEVector3(1.0, 2.0, 3.0)
        encoded = VECTOR3.encode(vector)
        expected = struct.pack("fff", 1.0, 2.0, 3.0)
        assert encoded == expected

    def test_encode_empty(self):
        """Test VECTOR3 type encoding with zero values."""
        vector = KBEVector3(0.0, 0.0, 0.0)
        encoded = VECTOR3.encode(vector)
        expected = struct.pack("fff", 0.0, 0.0, 0.0)
        assert encoded == expected

    def test_encode_decode_roundtrip(self):
        """Test VECTOR3 encode/decode roundtrip."""
        original = KBEVector3(3.14, -2.71, 42.0)
        encoded = VECTOR3.encode(original)
        decoded, offset = VECTOR3.decode(memoryview(encoded))
        assert offset == 12

        assert math.isclose(decoded.x, original.x, rel_tol=1e-6)
        assert math.isclose(decoded.y, original.y, rel_tol=1e-6)
        assert math.isclose(decoded.z, original.z, rel_tol=1e-6)


class TestKBEVector4:
    """Tests for the VECTOR4 type."""

    def test_decode_empty(self):
        """Test VECTOR4 type decoding (initial/zero values)."""
        data = memoryview(
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        )
        value, offset = VECTOR4.decode(data)
        assert offset == 16
        assert KBEVector4(0.0, 0.0, 0.0, 0.0) == value

    def test_decode(self):
        """Test VECTOR4 type decoding."""
        data = memoryview(b"\x00\x00\x80?\x00\x00\x00@\x00\x00@@\x00\x00\x80@")
        value, offset = VECTOR4.decode(data)
        assert offset == 16
        assert KBEVector4(1.0, 2.0, 3.0, 4.0) == value

    def test_encode(self):
        """Test VECTOR4 type encoding."""
        vector = KBEVector4(1.0, 2.0, 3.0, 4.0)
        encoded = VECTOR4.encode(vector)
        expected = struct.pack("ffff", 1.0, 2.0, 3.0, 4.0)
        assert encoded == expected

    def test_encode_empty(self):
        """Test VECTOR4 type encoding with zero values."""
        vector = KBEVector4(0.0, 0.0, 0.0, 0.0)
        encoded = VECTOR4.encode(vector)
        expected = struct.pack("ffff", 0.0, 0.0, 0.0, 0.0)
        assert encoded == expected

    def test_encode_decode_roundtrip(self):
        """Test VECTOR4 encode/decode roundtrip."""
        original = KBEVector4(3.14, -2.71, 42.0, 0.5)
        encoded = VECTOR4.encode(original)
        decoded, offset = VECTOR4.decode(memoryview(encoded))
        assert offset == 16

        assert math.isclose(decoded.x, original.x, rel_tol=1e-6)
        assert math.isclose(decoded.y, original.y, rel_tol=1e-6)
        assert math.isclose(decoded.z, original.z, rel_tol=1e-6)
        assert math.isclose(decoded.w, original.w, rel_tol=1e-6)
