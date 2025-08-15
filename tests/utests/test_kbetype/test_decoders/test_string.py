"""Tests of KBEngine STRING encoder / decoder.."""

import pytest

from enki.kbetype import STRING
from enki.kbetype.pytypes.basic_data_types import KBEString


class TestKBEString:
    """Тесты для KBEString."""

    @pytest.mark.parametrize(
        "value",
        [
            "",
            "hello",
            "привет",
            "123",
            " ",
            "a" * 1000,
            "null\0terminated",  # строка с нулевым байтом внутри
        ],
    )
    def test_valid_strings(self, value):
        """Проверка создания KBEString с корректными значениями."""
        result = KBEString(value)
        assert str(result) == value
        assert isinstance(result, KBEString)
        assert isinstance(result, str)


class TestSTRINGDecoder:
    """Тесты для декодера STRING."""

    @pytest.mark.parametrize(
        "data,expected_str,expected_size",
        [
            (b"2.5.10\x00", "2.5.10", 7),  # Пустая строка
            (b"\x00", "", 1),  # Пустая строка
            (b"hello\x00", "hello", 6),
            (b"test\x00extra", "test", 5),
            (b"\x00remaining", "", 1),
            # (b'привет\x00', "привет", 13),  # UTF-8 строка (7 байт + 6 байт кириллица)
            (b"\x01\x02\x03\x00", "\x01\x02\x03", 4),
            (b"no_null_terminator", "no_null_terminator", 18),  # Без терминатора
        ],
    )
    def test_decode_valid(self, data, expected_str, expected_size):
        """Проверка декодирования корректных строк."""
        mv = memoryview(data)
        result, size = STRING.decode(mv)
        assert str(result) == expected_str
        assert size == expected_size
        assert isinstance(result, KBEString)

    def test_decode_empty_buffer(self):
        """Проверка обработки пустого буфера."""
        value, offset = STRING.decode(memoryview(b""))
        assert value == ""
        assert offset == 0

    @pytest.mark.parametrize(
        "data",
        [
            b"\x01\x02\x03",  # Без терминатора
            b"long_string_without_terminator" * 10,
        ],
    )
    def test_decode_no_terminator(self, data):
        """Проверка строк без нулевого терминатора."""
        mv = memoryview(data)
        result, size = STRING.decode(mv)
        # Ожидается, что будет возвращена вся строка до конца буфера
        assert size == len(data)
        assert str(result) == data.decode("utf-8")


class TestSTRINGEncoder:
    """Тесты для кодировщика STRING."""

    @pytest.mark.parametrize(
        "value,expected_bytes",
        [
            (KBEString(""), b"\x00"),
            (KBEString("hello"), b"hello\x00"),
            (KBEString("привет"), "привет\x00".encode()),
            (KBEString("\x01\x02\x03"), b"\x01\x02\x03\x00"),
            (KBEString(" "), b" \x00"),
            (KBEString("2.5.10"), b"2.5.10\x00"),
        ],
    )
    def test_encode_valid(self, value, expected_bytes):
        """Проверка кодирования корректных строк."""
        assert STRING.encode(value) == expected_bytes

    @pytest.mark.parametrize(
        "invalid_value",
        [
            123,
            b"bytes",
            None,
            ["not", "a", "string"],
            {"key": "value"},
        ],
    )
    def test_encode_invalid_type(self, invalid_value):
        """Проверка кодирования неверного типа."""
        with pytest.raises(TypeError):
            STRING.encode(invalid_value)

    def test_encode_large_string(self):
        """Проверка кодирования большой строки."""
        large_str = KBEString("a" * 10_000)
        encoded = STRING.encode(large_str)
        assert encoded.endswith(b"\x00")
        assert len(encoded) == 10_001


def test_decode():
    """Test string decoding.."""
    data = memoryview(b"2.5.10\x00")
    value, offset = STRING.decode(data)
    assert offset == 7
    assert isinstance(value, str)
    assert value == "2.5.10"


def test_decode_empty():
    """Test empty string decoding.."""
    data = memoryview(b"\x00")
    value, offset = STRING.decode(data)
    assert offset == 1
    assert isinstance(value, str)
    assert value == ""


def test_encode():
    """Test string encoding.."""
    value = KBEString("2.5.10")
    data = STRING.encode(value)
    assert data == b"2.5.10\x00"


def test_encode_empty():
    """Test string encoding.."""
    value = KBEString("")
    data = STRING.encode(value)
    assert data == b"\x00"
