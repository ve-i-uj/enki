"""Tests of KBEngine UINT8 encoder / decoder.."""

import sys

import pytest

from enki.kbetype import UINT8, KBEUInt8


class TestKBEUInt8Boundaries:
    """Тесты граничных значений для KBEUInt8."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (0, True),  # Нижняя граница
            (255, True),  # Верхняя граница
            (-1, False),  # Ниже нижней границы
            (256, False),  # Выше верхней границы
            (128, True),  # Середина диапазона
            (0xFF, True),  # Верхняя граница (hex)
            (1 << 8, False),  # 2^8 (уже за границей)
            ((1 << 8) - 1, True),  # 2^8 - 1 (максимальное значение)
        ],
    )
    def test_boundary_values(self, value, expected):
        """Проверка обработки граничных значений."""
        if expected:
            result = KBEUInt8(value)
            assert int(result) == value
        else:
            with pytest.raises(ValueError):
                KBEUInt8(value)

    def test_max_system_int(self):
        """Проверка максимального значения для системного int."""
        with pytest.raises(ValueError):
            KBEUInt8(sys.maxsize)


class TestUINT8DecoderBoundaries:
    """Тесты граничных значений для декодера UINT8."""

    @pytest.mark.parametrize(
        ("data", "expected_value"),
        [
            (b"\x00", 0),  # Минимальное значение
            (b"\xff", 255),  # Максимальное значение
            (b"\x80", 128),  # Граница
            (b"\x7f", 127),  # Максимальное 7-bit
            (b"\x01", 1),  # Минимальное положительное
            (b"\xfe", 254),  # Максимальное -1
        ],
    )
    def test_decode_boundary_values(self, data, expected_value):
        """Проверка декодирования граничных значений."""
        mv = memoryview(data)
        result, offset = UINT8.decode(mv)
        assert int(result) == expected_value
        assert offset == 1
        assert isinstance(result, KBEUInt8)

    @pytest.mark.parametrize(
        ("value", "expected_bytes"),
        [
            (KBEUInt8(0), b"\x00"),  # Минимальное значение
            (KBEUInt8(255), b"\xff"),  # Максимальное значение
            (KBEUInt8(128), b"\x80"),  # Граница
            (KBEUInt8(1), b"\x01"),  # Минимальное ненулевое
            (KBEUInt8(254), b"\xfe"),  # Максимальное -1
        ],
    )
    def test_encode_boundary_values(self, value, expected_bytes):
        """Проверка кодирования граничных значений."""
        assert UINT8.encode(value) == expected_bytes

    def test_decode_empty_buffer(self):
        """Проверка обработки пустого буфера."""
        with pytest.raises(ValueError, match="Not enough data to decode UINT8"):
            UINT8.decode(memoryview(b""))

    @pytest.mark.parametrize(
        "invalid_value",
        [
            256,  # Превышение на 1
            0x100,  # 256 в hex
            -1,  # Отрицательное значение
            sys.maxsize,  # Максимальное значение int
            1.0,  # Float значение
            "255",  # Строковое представление
        ],
    )
    def test_encode_invalid_boundaries(self, invalid_value):
        """Проверка кодирования значений за границами допустимого."""
        if isinstance(invalid_value, int):
            with pytest.raises(ValueError):
                KBEUInt8(invalid_value)
        else:
            with pytest.raises(TypeError):
                UINT8.encode(invalid_value)
