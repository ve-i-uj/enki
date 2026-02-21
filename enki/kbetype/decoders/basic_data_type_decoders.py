"""Декодеры / энкодеры для простых типов данных KBEngine.

См. Basic data types в kbengine_api(en).chm .
"""

from __future__ import annotations

import logging
import pickle
import struct
import typing
from typing import TypeAlias

from enki.kbetype.decoders.idecoders import IKBETypeDecoder, Offset
from enki.kbetype.pytypes.basic_data_types import (
    KBEBlob,
    KBEBool,
    KBEDouble,
    KBEFloat,
    KBEInt8,
    KBEInt16,
    KBEInt32,
    KBEInt64,
    KBEPython,
    KBERowByteData,
    KBEString,
    KBEUInt8,
    KBEUInt16,
    KBEUInt32,
    KBEUInt64,
    KBEUnicode,
    KBEVector2,
    KBEVector3,
    KBEVector4,
)

logger = logging.getLogger(__name__)


__all__ = [
    "BLOB",
    "BOOL",
    "DOUBLE",
    "ENTITYCALL",
    "FLOAT",
    "INT8",
    "INT16",
    "INT32",
    "INT64",
    "KBE_DATATYPE2ID_MAX",
    "PYTHON",
    "PY_DICT",
    "PY_LIST",
    "PY_TUPLE",
    "STRING",
    "UINT8",
    "UINT8_ARRAY",
    "UINT16",
    "UINT32",
    "UINT64",
    "UNICODE",
    "VECTOR2",
    "VECTOR3",
    "VECTOR4",
]


class UINT8(IKBETypeDecoder[KBEUInt8]):
    """Декодер для типа UINT8."""

    _kbe_type = KBEUInt8

    @classmethod
    def get_kbe_type(cls) -> type[KBEUInt8]:
        """Возвращает тип KBE."""
        return cls._kbe_type

    @classmethod
    def decode(cls, data: memoryview) -> tuple[KBEUInt8, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Raises:
            ValueError: не получается декодировать

        Returns:
            tuple[KBEUInt8, Offset]: decoded data and offset

        """
        if len(data) < 1:
            msg = "Not enough data to decode UINT8 (needs 1 byte)"
            raise ValueError(msg)

        try:
            value = struct.unpack("<B", data[:1])[0]
            return KBEUInt8(value), 1
        except struct.error as err:
            logger.exception("Failed to decode UINT8")
            msg = "Failed to decode UINT8"
            raise ValueError(msg) from err

    @classmethod
    def encode(cls, value: KBEUInt8) -> bytes:
        """Encode a python type to bytes.

        Args:
            value (KBEUInt8): значение

        Raises:
            struct.error: ошибка кодирования

        Returns:
            bytes: закодированное значение

        """
        try:
            return struct.pack("<B", value)
        except struct.error as err:
            logger.exception("value = %s", value)
            raise TypeError from err


class UINT16(IKBETypeDecoder[KBEUInt16]):
    """Декодер для типа UINT16."""

    _kbe_type = KBEUInt16

    @classmethod
    def get_kbe_type(cls) -> type[KBEUInt16]:
        """Возвращает тип KBE."""
        return cls._kbe_type

    @classmethod
    def decode(cls, data: memoryview) -> tuple[KBEUInt16, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Raises:
            ValueError: не получается декодировать или недостаточно данных

        Returns:
            tuple[KBEUInt16, Offset]: decoded data and offset

        """
        if len(data) < 2:
            msg = "Not enough data to decode UINT16 (needs 2 bytes)"
            raise ValueError(msg)

        try:
            value = struct.unpack("<H", data[:2])[0]
            return KBEUInt16(value), 2
        except struct.error as err:
            logger.exception("Failed to decode UINT16")
            msg = "Failed to decode UINT16"
            raise ValueError(msg) from err

    @classmethod
    def encode(cls, value: KBEUInt16) -> bytes:
        """Encode a python type to bytes.

        Args:
            value (KBEUInt16): значение для кодирования

        Raises:
            struct.error: ошибка кодирования

        Returns:
            bytes: закодированное значение

        """
        try:
            return struct.pack("<H", value)
        except struct.error as err:
            logger.exception("value = %s", value)
            raise TypeError from err


class UINT32(IKBETypeDecoder[KBEUInt32]):
    """Декодер для типа UINT32."""

    _kbe_type = KBEUInt32

    @classmethod
    def get_kbe_type(cls) -> type[KBEUInt32]:
        """Возвращает тип KBE."""
        return cls._kbe_type

    @classmethod
    def decode(cls, data: memoryview) -> tuple[KBEUInt32, Offset]:
        """Декодировать UINT32.

        Args:
            data (memoryview): bytes for decoding

        Raises:
            ValueError: не получается декодировать или недостаточно данных

        Returns:
            tuple[KBEUInt32, Offset]: decoded data and offset

        """
        if len(data) < 4:
            msg = "Not enough data to decode UINT32 (needs 4 bytes)"
            raise ValueError(msg)

        try:
            value = struct.unpack("<I", data[:4])[0]
            return KBEUInt32(value), 4
        except struct.error as err:
            logger.exception("Failed to decode UINT32")
            msg = "Failed to decode UINT32"
            raise ValueError(msg) from err

    @classmethod
    def encode(cls, value: KBEUInt32) -> bytes:
        """Encode a python type to bytes.

        Args:
            value (KBEUInt32): значение для кодирования

        Raises:
            struct.error: ошибка кодирования

        Returns:
            bytes: закодированное значение

        """
        try:
            return struct.pack("<I", value)
        except struct.error:
            logger.exception("value = %s", value)
            raise


class UINT64(IKBETypeDecoder[KBEUInt64]):
    """Декодер для типа UINT64."""

    _kbe_type = KBEUInt64

    @classmethod
    def get_kbe_type(cls) -> type[KBEUInt64]:
        """Возвращает тип KBE."""
        return cls._kbe_type

    @classmethod
    def decode(cls, data: memoryview) -> tuple[KBEUInt64, Offset]:
        """Декодировать UINT64.

        Args:
            data (memoryview): bytes for decoding

        Raises:
            ValueError: не получается декодировать или недостаточно данных

        Returns:
            tuple[KBEUInt64, Offset]: decoded data and offset

        """
        if len(data) < 8:
            msg = "Not enough data to decode UINT64 (needs 8 bytes)"
            raise ValueError(msg)

        try:
            value = struct.unpack("<Q", data[:8])[0]
            return KBEUInt64(value), 8
        except struct.error as err:
            logger.exception("Failed to decode UINT64")
            msg = "Failed to decode UINT64"
            raise ValueError(msg) from err

    @classmethod
    def encode(cls, value: KBEUInt64) -> bytes:
        """Encode a python type to bytes.

        Args:
            value (KBEUInt64): значение для кодирования

        Raises:
            struct.error: ошибка кодирования

        Returns:
            bytes: закодированное значение

        """
        try:
            return struct.pack("<Q", value)
        except struct.error:
            logger.exception("value = %s", value)
            raise


class INT8(IKBETypeDecoder[KBEInt8]):
    """Декодер для типа INT8."""

    _kbe_type = KBEInt8

    @classmethod
    def get_kbe_type(cls) -> type[KBEInt8]:
        """Возвращает тип KBE."""
        return cls._kbe_type

    @classmethod
    def decode(cls, data: memoryview) -> tuple[KBEInt8, Offset]:
        """Декодировать INT8.

        Args:
            data (memoryview): bytes for decoding

        Raises:
            ValueError: не получается декодировать или недостаточно данных

        Returns:
            tuple[KBEInt8, Offset]: decoded data and offset

        """
        if len(data) < 1:
            msg = "Not enough data to decode INT8 (needs 1 byte)"
            raise ValueError(msg)

        try:
            value = struct.unpack("<b", data[:1])[0]
            return KBEInt8(value), 1
        except struct.error as err:
            logger.exception("Failed to decode INT8")
            msg = "Failed to decode INT8"
            raise ValueError(msg) from err

    @classmethod
    def encode(cls, value: KBEInt8) -> bytes:
        """Encode a python type to bytes.

        Args:
            value (KBEInt8): значение для кодирования

        Raises:
            struct.error: ошибка кодирования

        Returns:
            bytes: закодированное значение

        """
        try:
            return struct.pack("<b", value)
        except struct.error:
            logger.exception("value = %s", value)
            raise


class INT16(IKBETypeDecoder[KBEInt16]):
    """Декодер для типа INT16."""

    _kbe_type = KBEInt16

    @classmethod
    def get_kbe_type(cls) -> type[KBEInt16]:
        """Возвращает тип KBE."""
        return cls._kbe_type

    @classmethod
    def decode(cls, data: memoryview) -> tuple[KBEInt16, Offset]:
        """Декодировать INT16.

        Args:
            data (memoryview): bytes for decoding

        Raises:
            ValueError: не получается декодировать или недостаточно данных

        Returns:
            tuple[KBEInt16, Offset]: decoded data and offset

        """
        if len(data) < 2:
            msg = "Not enough data to decode INT16 (needs 2 bytes)"
            raise ValueError(msg)

        try:
            value = struct.unpack("<h", data[:2])[0]
            return KBEInt16(value), 2
        except struct.error as err:
            logger.exception("Failed to decode INT16")
            msg = "Failed to decode INT16"
            raise ValueError(msg) from err

    @classmethod
    def encode(cls, value: KBEInt16) -> bytes:
        """Encode a python type to bytes.

        Args:
            value (KBEInt16): значение для кодирования

        Raises:
            struct.error: ошибка кодирования

        Returns:
            bytes: закодированное значение

        """
        try:
            return struct.pack("<h", value)
        except struct.error:
            logger.exception("value = %s", value)
            raise


class INT32(IKBETypeDecoder[KBEInt32]):
    """Декодер для типа INT32."""

    _kbe_type = KBEInt32

    @classmethod
    def get_kbe_type(cls) -> type[KBEInt32]:
        """Возвращает тип KBE."""
        return cls._kbe_type

    @classmethod
    def decode(cls, data: memoryview) -> tuple[KBEInt32, Offset]:
        """Декодировать INT32.

        Args:
            data (memoryview): bytes for decoding

        Raises:
            ValueError: не получается декодировать или недостаточно данных

        Returns:
            tuple[KBEInt32, Offset]: decoded data and offset

        """
        if len(data) < 4:
            msg = "Not enough data to decode INT32 (needs 4 bytes)"
            raise ValueError(msg)

        try:
            value = struct.unpack("<i", data[:4])[0]
            return KBEInt32(value), 4
        except struct.error as err:
            logger.exception("Failed to decode INT32")
            msg = "Failed to decode INT32"
            raise ValueError(msg) from err

    @classmethod
    def encode(cls, value: KBEInt32) -> bytes:
        """Encode a python type to bytes.

        Args:
            value (KBEInt32): значение для кодирования

        Raises:
            struct.error: ошибка кодирования

        Returns:
            bytes: закодированное значение

        """
        try:
            return struct.pack("<i", value)
        except struct.error:
            logger.exception("value = %s", value)
            raise


class INT64(IKBETypeDecoder[KBEInt64]):
    """Декодер для типа INT64."""

    _kbe_type = KBEInt64

    @classmethod
    def get_kbe_type(cls) -> type[KBEInt64]:
        """Возвращает тип KBE."""
        return cls._kbe_type

    @classmethod
    def decode(cls, data: memoryview) -> tuple[KBEInt64, Offset]:
        """Декодировать INT64.

        Args:
            data (memoryview): bytes for decoding

        Raises:
            ValueError: не получается декодировать или недостаточно данных

        Returns:
            tuple[KBEInt64, Offset]: decoded data and offset

        """
        if len(data) < 8:
            msg = "Not enough data to decode INT64 (needs 8 bytes)"
            raise ValueError(msg)

        try:
            value = struct.unpack("<q", data[:8])[0]
            return KBEInt64(value), 8
        except struct.error as err:
            logger.exception("Failed to decode INT64")
            msg = "Failed to decode INT64"
            raise ValueError(msg) from err

    @classmethod
    def encode(cls, value: KBEInt64) -> bytes:
        """Encode a python type to bytes.

        Args:
            value (KBEInt64): значение для кодирования

        Raises:
            struct.error: ошибка кодирования

        Returns:
            bytes: закодированное значение

        """
        try:
            return struct.pack("<q", value)
        except struct.error:
            logger.exception("value = %s", value)
            raise


class FLOAT(IKBETypeDecoder[KBEFloat]):
    """Декодер для типа FLOAT."""

    _kbe_type = KBEFloat

    @classmethod
    def get_kbe_type(cls) -> type[KBEFloat]:
        """Возвращает тип KBE."""
        return cls._kbe_type

    @classmethod
    def decode(cls, data: memoryview) -> tuple[KBEFloat, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEFloat, Offset]: decoded data and offset

        """
        offset = 4
        value: KBEFloat = struct.unpack("<f", data[:offset])[0]
        return value, offset

    @classmethod
    def encode(cls, value: KBEFloat) -> bytes:
        """Encode a python type to bytes."""
        return struct.pack("<f", value)


class DOUBLE(IKBETypeDecoder[KBEDouble]):
    """Декодер для типа DOUBLE."""

    _kbe_type = KBEDouble

    @classmethod
    def get_kbe_type(cls) -> type[KBEDouble]:
        """Возвращает тип KBE."""
        return cls._kbe_type

    @classmethod
    def decode(cls, data: memoryview) -> tuple[KBEDouble, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEDouble, Offset]: decoded data and offset

        """
        offset = 8
        value: KBEDouble = struct.unpack("<d", data[:offset])[0]
        return value, offset

    @classmethod
    def encode(cls, value: KBEDouble) -> bytes:
        """Encode a python type to bytes."""
        return struct.pack("<d", value)


class VECTOR2(IKBETypeDecoder[KBEVector2]):
    """Декодер для типа VECTOR2."""

    _kbe_type = KBEVector2

    @classmethod
    def get_kbe_type(cls) -> type[KBEVector2]:
        """Возвращает тип KBE."""
        return cls._kbe_type

    @classmethod
    def decode(cls, data: memoryview) -> tuple[KBEVector2, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEVector2, Offset]: decoded data and offset

        """
        total_offset = 0

        x_value, offset = FLOAT.decode(data)
        data = data[offset:]
        total_offset += offset

        y_value, offset = FLOAT.decode(data)
        data = data[offset:]
        total_offset += offset

        return KBEVector2(x_value, y_value), total_offset

    @classmethod
    def encode(cls, value: KBEVector2) -> bytes:
        """Encode a python type to bytes."""
        # TODO: [burov_alexey@mail.ru 05.07.2025 15:26]
        # Возможно, что неправильно реализовано, т.к. до этого момента в обще
        # ничего не было.
        data = b""

        data += FLOAT.encode(KBEFloat(value.x))
        data += FLOAT.encode(KBEFloat(value.y))

        return data


class VECTOR3(IKBETypeDecoder[KBEVector3]):
    """Декодер для типа VECTOR3."""

    _kbe_type = KBEVector3

    @classmethod
    def get_kbe_type(cls) -> type[KBEVector3]:
        """Возвращает тип KBE."""
        return cls._kbe_type

    @classmethod
    def decode(cls, data: memoryview) -> tuple[KBEVector3, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEVector3, Offset]: decoded data and offset

        """
        total_offset = 0

        x_value, offset = FLOAT.decode(data)
        data = data[offset:]
        total_offset += offset

        y_value, offset = FLOAT.decode(data)
        data = data[offset:]
        total_offset += offset

        z_value, offset = FLOAT.decode(data)
        data = data[offset:]
        total_offset += offset

        return KBEVector3(x_value, y_value, z_value), total_offset

    @classmethod
    def encode(cls, value: KBEVector3) -> bytes:
        """Encode a python type to bytes."""
        data = b""

        data += FLOAT.encode(KBEFloat(value.x))
        data += FLOAT.encode(KBEFloat(value.y))
        data += FLOAT.encode(KBEFloat(value.z))

        return data


class VECTOR4(IKBETypeDecoder[KBEVector4]):
    """Декодер для типа VECTOR4."""

    _kbe_type = KBEVector4

    @classmethod
    def get_kbe_type(cls) -> type[KBEVector4]:
        """Возвращает тип KBE."""
        return cls._kbe_type

    @classmethod
    def decode(cls, data: memoryview) -> tuple[KBEVector4, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEVector4, Offset]: decoded data and offset

        """
        total_offset = 0

        x_value, offset = FLOAT.decode(data)
        data = data[offset:]
        total_offset += offset

        y_value, offset = FLOAT.decode(data)
        data = data[offset:]
        total_offset += offset

        z_value, offset = FLOAT.decode(data)
        data = data[offset:]
        total_offset += offset

        w_value, offset = FLOAT.decode(data)
        data = data[offset:]
        total_offset += offset

        return KBEVector4(x_value, y_value, z_value, w_value), total_offset

    @classmethod
    def encode(cls, value: KBEVector4) -> bytes:
        """Encode a python type to bytes."""
        data = b""

        data += FLOAT.encode(KBEFloat(value.x))
        data += FLOAT.encode(KBEFloat(value.y))
        data += FLOAT.encode(KBEFloat(value.z))
        data += FLOAT.encode(KBEFloat(value.w))

        return data


class STRING(IKBETypeDecoder[KBEString]):
    """Декодер для типа STRING."""

    _kbe_type = KBEString
    _NULL_TERMINATOR = int.from_bytes(b"\x00", "big")

    @classmethod
    def get_kbe_type(cls) -> type[KBEString]:
        """Возвращает тип KBE."""
        return cls._kbe_type

    @classmethod
    def decode(cls, data: memoryview) -> tuple[KBEString, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEString, Offset]: decoded data and offset

        """
        if not data:
            logger.debug("!!! There is not any data for string decoding")
            return KBEString(""), 0

        index = 0
        for index, b in enumerate(data):  # noqa: B007
            if b == STRING._NULL_TERMINATOR:
                break
        else:
            # Анамольное поведение, нет терминатора
            logger.debug(
                "!!! There is not null terminator charachter in the data"
            )
            size = len(data)
            return KBEString(data.tobytes().decode()), size

        size = index + 1  # string + null terminator
        value = data[:index].tobytes().decode()

        return KBEString(value), size

    @classmethod
    def encode(cls, value: KBEString) -> bytes:
        """Encode a python type to bytes."""
        try:
            encoded = value.encode("utf-8")
        except AttributeError as err:
            logger.exception("Encode STRING error")
            raise TypeError from err

        return struct.pack(f"<{len(encoded) + 1}s", encoded)


class UNICODE(IKBETypeDecoder[KBEUnicode]):
    """Декодер для типа UNICODE."""

    _kbe_type = KBEUnicode

    @classmethod
    def get_kbe_type(cls) -> type[KBEUnicode]:
        """Возвращает тип KBE."""
        return cls._kbe_type

    @classmethod
    def decode(cls, data: memoryview) -> tuple[KBEUnicode, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEUnicode, Offset]: decoded data and offset

        """
        encoded, offset = BLOB.decode(data)
        return KBEUnicode(encoded.decode("utf-8")), offset

    @classmethod
    def encode(cls, value: KBEUnicode) -> bytes:
        """Encode a python type to bytes."""
        return BLOB.encode(KBEBlob(value.encode()))


class PYTHON(IKBETypeDecoder[KBEPython]):
    """Декодер для типа PYTHON."""

    _kbe_type = KBEPython

    @classmethod
    def get_kbe_type(cls) -> type[KBEPython]:
        """Возвращает тип KBE."""
        return cls._kbe_type

    @classmethod
    def decode(cls, data: memoryview) -> tuple[KBEPython, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEPython, Offset]: decoded data and offset

        """
        bytes_, offset = BLOB.decode(data)
        obj = pickle.loads(bytes_)  # noqa: S301

        obj = typing.cast("KBEPython", obj)
        return obj, offset

    @classmethod
    def encode(cls, value: KBEPython) -> bytes:
        """Encode a python type to bytes."""
        bytes_ = pickle.dumps(value)
        return BLOB.encode(KBEBlob(bytes_))


class PY_DICT(PYTHON):  # noqa: N801 # pylint: disable=invalid-name
    """Декодер для типа PY_DICT."""

    _kbe_type = KBEPython

    @classmethod
    def get_kbe_type(cls) -> type[KBEPython]:
        """Возвращает тип KBE."""
        return cls._kbe_type


class PY_TUPLE(PYTHON):  # noqa: N801 # pylint: disable=invalid-name
    """Декодер для типа PY_TUPLE."""

    _kbe_type = KBEPython

    @classmethod
    def get_kbe_type(cls) -> type[KBEPython]:
        """Возвращает тип KBE."""
        return cls._kbe_type


class PY_LIST(PYTHON):  # noqa: N801 # pylint: disable=invalid-name
    """Декодер для типа PY_LIST."""

    _kbe_type = KBEPython

    @classmethod
    def get_kbe_type(cls) -> type[KBEPython]:
        """Возвращает тип KBE."""
        return cls._kbe_type


# TODO: [burov_alexey@mail.ru 05.07.2025 15:57]
# реализован не был до этого. Может и не нужен пока на клиенте.
class _NOT_IMPLEMENTED(IKBETypeDecoder[KBEUInt8]):  # noqa: N801
    """Декодер не реализован для этого типа."""

    _kbe_type = KBEUInt8

    @classmethod
    def get_kbe_type(cls) -> type[KBEUInt8]:
        """Возвращает тип KBE."""
        return cls._kbe_type

    @classmethod
    def decode(cls, data: memoryview) -> tuple[KBEUInt8, Offset]:
        """Decode bytes to a python type.

        Returns decoded data and offset.
        """
        raise NotImplementedError

    @classmethod
    def encode(cls, value: KBEUInt8) -> bytes:
        """Encode a python type to bytes."""
        raise NotImplementedError


ENTITYCALL: TypeAlias = _NOT_IMPLEMENTED
KBE_DATATYPE2ID_MAX: TypeAlias = _NOT_IMPLEMENTED


class BLOB(IKBETypeDecoder[KBEBlob]):
    """Декодер для типа BLOB (бинарные данные с длинной)."""

    _kbe_type = KBEBlob

    @classmethod
    def get_kbe_type(cls) -> type[KBEBlob]:
        """Возвращает тип KBE."""
        return cls._kbe_type

    @classmethod
    def decode(cls, data: memoryview) -> tuple[KBEBlob, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEBlob, Offset]: decoded data and offset

        """
        length, offset = UINT32.decode(data)
        if length == 0:
            return KBEBlob(b""), offset
        size = offset + length

        return struct.unpack(f"={length}s", data[offset:size])[0], size

    @classmethod
    def encode(cls, value: KBEBlob) -> bytes:
        """Encode a python type to bytes."""
        return struct.pack(f"=I{len(value)}s", len(value), value)


# *** Это небольшое расширение для удобства описания сообщений ***


class UINT8_ARRAY(
    IKBETypeDecoder[KBERowByteData]
):  # pylint: disable=invalid-name
    """Декодер для сырых данных без длины до конца буфера."""

    _kbe_type = KBERowByteData

    @classmethod
    def get_kbe_type(cls) -> type[KBERowByteData]:
        """Возвращает тип KBE."""
        return cls._kbe_type

    @classmethod
    def decode(cls, data: memoryview) -> tuple[KBERowByteData, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBERowByteData, Offset]: decoded data and offset

        """
        return KBERowByteData(data.tobytes()), len(data)

    @classmethod
    def encode(cls, value: KBERowByteData) -> bytes:
        """Encode a python type to bytes."""
        return bytes(value)


class BOOL(IKBETypeDecoder[KBEBool]):
    """Декодер для типа BOOL."""

    _kbe_type = KBEBool

    @classmethod
    def get_kbe_type(cls) -> type[KBEBool]:
        """Возвращает тип KBE."""
        return cls._kbe_type

    @classmethod
    def decode(cls, data: memoryview) -> tuple[KBEBool, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEBool, Offset]: decoded data and offset

        """
        return KBEBool(1 if INT8.decode(data)[0] > 0 else 0), 1

    @classmethod
    def encode(cls, value: KBEBool) -> bytes:
        """Encode a python type to bytes."""
        return INT8.encode(KBEInt8(1 if value else 0))
