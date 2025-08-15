"""Tests of KBEngine UNICODE encoder / decoder."""

from enki.kbetype import UNICODE


def test_decode() -> None:
    """Test string decoding."""
    data = memoryview(b"\r\x00\x00\x00default_value")
    value, offset = UNICODE.decode(data)
    assert offset == 17
    assert isinstance(value, str)
    assert value == "default_value"


def test_decode_empty() -> None:
    """Test empty string decoding."""
    data = memoryview(b"\x00\x00\x00\x00")
    value, offset = UNICODE.decode(data)
    assert offset == 4
    assert isinstance(value, str)
    assert value == ""
