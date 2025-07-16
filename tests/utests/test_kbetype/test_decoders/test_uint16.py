"""Tests for KBEngine UINT16 encoder/decoder..."""

import sys

import pytest

from enki.kbetype import UINT16, KBEUInt16


class TestKBEUInt16Boundaries:
    """Тесты граничных значений для KBEUInt16."""

    @pytest.mark.parametrize(
        "value,expected",
        [
            (0, True),  # Нижняя граница
            (65535, True),  # Верхняя граница
            (-1, False),  # Ниже нижней границы
            (65536, False),  # Выше верхней границы
            (32768, True),  # Середина диапазона
            (0xFFFF, True),  # Верхняя граница (hex)
            (1 << 16, False),  # 2^16 (уже за границей)
            ((1 << 16) - 1, True),  # 2^16 - 1 (максимальное значение)
        ],
    )
    def test_boundary_values(self, value, expected):
        """Проверка обработки граничных значений."""
        if expected:
            result = KBEUInt16(value)
            assert int(result) == value
        else:
            with pytest.raises(ValueError):
                KBEUInt16(value)

    def test_max_system_int(self):
        """Проверка максимального значения для системного int."""
        max_int = sys.maxsize
        if max_int > 65535:
            with pytest.raises(ValueError):
                KBEUInt16(max_int)


class TestUINT16DecoderBoundaries:
    """Тесты граничных значений для декодера UINT16."""

    @pytest.mark.parametrize(
        "data,expected_value",
        [
            (b"\x00\x00", 0),  # Минимальное значение
            (b"\xff\xff", 65535),  # Максимальное значение
            (
                b"\x00\x80",
                32768,
            ),  # Граница положительных/отрицательных если бы было int16
            (b"\xff\x7f", 32767),  # Максимальное положительное если бы было int16
            (b"\x01\x00", 1),  # Минимальное положительное ненулевое
            (b"\xfe\xff", 65534),  # Максимальное -1
        ],
    )
    def test_decode_boundary_values(self, data, expected_value):
        """Проверка декодирования граничных значений."""
        mv = memoryview(data)
        result, offset = UINT16.decode(mv)
        assert int(result) == expected_value
        assert offset == 2
        assert isinstance(result, KBEUInt16)

    @pytest.mark.parametrize(
        "value,expected_bytes",
        [
            (KBEUInt16(0), b"\x00\x00"),  # Минимальное значение
            (KBEUInt16(65535), b"\xff\xff"),  # Максимальное значение
            (KBEUInt16(32768), b"\x00\x80"),  # Граница положительных/отрицательных
            (KBEUInt16(1), b"\x01\x00"),  # Минимальное ненулевое
            (KBEUInt16(65534), b"\xfe\xff"),  # Максимальное -1
        ],
    )
    def test_encode_boundary_values(self, value, expected_bytes):
        """Проверка кодирования граничных значений."""
        assert UINT16.encode(value) == expected_bytes

    def test_decode_empty_buffer(self):
        """Проверка обработки пустого буфера."""
        with pytest.raises(ValueError, match="Not enough data to decode UINT16"):
            UINT16.decode(memoryview(b""))

    def test_decode_partial_buffer(self):
        """Проверка обработки частичного буфера (1 байт)."""
        with pytest.raises(ValueError, match="Not enough data to decode UINT16"):
            UINT16.decode(memoryview(b"\xff"))

    @pytest.mark.parametrize(
        "invalid_value",
        [
            65536,  # Превышение на 1
            0x10000,  # 65536 в hex
            -1,  # Отрицательное значение
            sys.maxsize,  # Максимальное значение int
        ],
    )
    def test_encode_invalid_boundaries(self, invalid_value):
        """Проверка кодирования значений за границами допустимого."""
        with pytest.raises(ValueError):
            # Попытка создать KBEUInt16 с недопустимым значением
            value = KBEUInt16(invalid_value)

    @pytest.mark.parametrize(
        "invalid_value",
        [
            sys.maxsize,  # Максимальное значение int
            1.0,  # Float значение
            "65535",  # Строковое представление
        ],
    )
    def test_encode_invalid_type(self, invalid_value):
        """Прямая передача недопустимого типа."""
        # Прямая передача недопустимого типа
        with pytest.raises(TypeError):
            UINT16.encode(invalid_value)
