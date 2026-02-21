"""Tests of the PYTHON encoder / decoder."""

from enki.kbetype.decoders.basic_data_type_decoders import PYTHON


class TestPython:
    """Tests for the PYTHON type."""

    def test_decode_empty(self):
        """Test of the python type decoding (initial value)."""
        data = memoryview(b"\x04\x00\x00\x00\x80\x03N.")
        value, offset = PYTHON.decode(data)
        assert offset == 8
        assert value is None

    def test_decode(self):
        """Test of the python type decoding."""
        data = memoryview(
            b"#\x00\x00\x00\x80\x03}q\x00(X\x01\x00\x00\x00xq\x01K\x01X\x01\x00\x00\x00yq\x02X\x02\x00\x00\x0010q\x03u."
        )
        value, offset = PYTHON.decode(data)
        assert offset == 39
        assert value == {"x": 1, "y": "10"}
