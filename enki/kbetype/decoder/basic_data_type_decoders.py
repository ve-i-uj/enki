"""Декодеры / энкодеры для простых типов данных KBEngine.

См. Basic data types в kbengine_api(en).chm .
"""

from __future__ import annotations

import pickle  # noqa: S403
import struct
import typing

from .decoded_types import (
    KBEBlob,
    KBEDouble,
    KBEFloat,
    KBEInt8,
    KBEInt16,
    KBEInt32,
    KBEInt64,
    KBEPython,
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
from .idecoder import IKBETypeDecoder, Offset


class UINT8(IKBETypeDecoder[KBEUInt8]):
    """Декодер для типа UINT8."""

    @staticmethod
    def decode(data: memoryview) -> tuple[KBEUInt8, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEUInt8, Offset]: decoded data and offset

        """
        offset = 1
        value: KBEUInt8 = struct.unpack("=B", data[:offset])[0]
        return value, offset

    @staticmethod
    def encode(value: KBEUInt8) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return struct.pack("=B", value)


class UINT16(IKBETypeDecoder[KBEUInt16]):
    """Декодер для типа UINT16."""

    @staticmethod
    def decode(data: memoryview) -> tuple[KBEUInt16, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEUInt16, Offset]: decoded data and offset

        """
        offset = 2
        value: KBEUInt16 = struct.unpack("=H", data[:offset])[0]
        return value, offset

    @staticmethod
    def encode(value: KBEUInt16) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return struct.pack("=H", value)


class UINT32(IKBETypeDecoder[KBEUInt32]):
    """Декодер для типа UINT32."""

    @staticmethod
    def decode(data: memoryview) -> tuple[KBEUInt32, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEUInt32, Offset]: decoded data and offset

        """
        offset = 4
        value: KBEUInt32 = struct.unpack("=I", data[:offset])[0]
        return value, offset

    @staticmethod
    def encode(value: KBEUInt32) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return struct.pack("=I", value)


class UINT64(IKBETypeDecoder[KBEUInt64]):
    """Декодер для типа UINT64."""

    @staticmethod
    def decode(data: memoryview) -> tuple[KBEUInt64, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEUInt64, Offset]: decoded data and offset

        """
        offset = 8
        value: KBEUInt64 = struct.unpack("=Q", data[:offset])[0]
        return value, offset

    @staticmethod
    def encode(value: KBEUInt64) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return struct.pack("=Q", value)


class INT8(IKBETypeDecoder[KBEInt8]):
    """Декодер для типа INT8."""

    @staticmethod
    def decode(data: memoryview) -> tuple[KBEInt8, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEInt8, Offset]: decoded data and offset

        """
        offset = 1
        value: KBEInt8 = struct.unpack("=b", data[:offset])[0]
        return value, offset

    @staticmethod
    def encode(value: KBEInt8) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return struct.pack("=b", value)


class INT16(IKBETypeDecoder[KBEInt16]):
    """Декодер для типа INT16."""

    @staticmethod
    def decode(data: memoryview) -> tuple[KBEInt16, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEInt16, Offset]: decoded data and offset

        """
        offset = 2
        value: KBEInt16 = struct.unpack("=h", data[:offset])[0]
        return value, offset

    @staticmethod
    def encode(value: KBEInt16) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return struct.pack("=h", value)


class INT32(IKBETypeDecoder[KBEInt32]):
    """Декодер для типа INT32."""

    @staticmethod
    def decode(data: memoryview) -> tuple[KBEInt32, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEInt32, Offset]: decoded data and offset

        """
        offset = 4
        value: KBEInt32 = struct.unpack("=i", data[:offset])[0]
        return value, offset

    @staticmethod
    def encode(value: KBEInt32) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return struct.pack("=i", value)


class INT64(IKBETypeDecoder[KBEInt64]):
    """Декодер для типа INT64."""

    @staticmethod
    def decode(data: memoryview) -> tuple[KBEInt64, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEInt64, Offset]: decoded data and offset

        """
        offset = 8
        value: KBEInt64 = struct.unpack("=q", data[:offset])[0]
        return value, offset

    @staticmethod
    def encode(value: KBEInt64) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return struct.pack("=q", value)


class FLOAT(IKBETypeDecoder[KBEFloat]):
    """Декодер для типа FLOAT."""

    @staticmethod
    def decode(data: memoryview) -> tuple[KBEFloat, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEFloat, Offset]: decoded data and offset

        """
        offset = 4
        value: KBEFloat = struct.unpack("=f", data[:offset])[0]
        return value, offset

    @staticmethod
    def encode(value: KBEFloat) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return struct.pack("=f", value)


class DOUBLE(IKBETypeDecoder[KBEDouble]):
    """Декодер для типа DOUBLE."""

    @staticmethod
    def decode(data: memoryview) -> tuple[KBEDouble, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEDouble, Offset]: decoded data and offset

        """
        offset = 8
        value: KBEDouble = struct.unpack("=d", data[:offset])[0]
        return value, offset

    @staticmethod
    def encode(value: KBEDouble) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return struct.pack("=d", value)


class VECTOR2(IKBETypeDecoder[KBEVector2]):
    """Декодер для типа VECTOR2."""

    @staticmethod
    def decode(data: memoryview) -> tuple[KBEVector2, Offset]:
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

    @staticmethod
    def encode(value: KBEVector2) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        # TODO: [burov_alexey@mail.ru 05.07.2025 15:26]
        # Возможно, что неправильно реализовано, т.к. до этого момента в обще
        # ничего не было.
        data = b""

        data += FLOAT.encode(KBEFloat(value.x))
        data += FLOAT.encode(KBEFloat(value.y))

        return data


class VECTOR3(IKBETypeDecoder[KBEVector3]):
    """Декодер для типа VECTOR3."""

    @staticmethod
    def decode(data: memoryview) -> tuple[KBEVector3, Offset]:
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

    @staticmethod
    def encode(value: KBEVector3) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        data = b""

        data += FLOAT.encode(KBEFloat(value.x))
        data += FLOAT.encode(KBEFloat(value.y))
        data += FLOAT.encode(KBEFloat(value.z))

        return data


class VECTOR4(IKBETypeDecoder[KBEVector4]):
    """Декодер для типа VECTOR4."""

    @staticmethod
    def decode(data: memoryview) -> tuple[KBEVector4, Offset]:
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

    @staticmethod
    def encode(value: KBEVector4) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        data = b""

        data += FLOAT.encode(KBEFloat(value.x))
        data += FLOAT.encode(KBEFloat(value.y))
        data += FLOAT.encode(KBEFloat(value.z))
        data += FLOAT.encode(KBEFloat(value.w))

        return data


class STRING(IKBETypeDecoder[KBEString]):
    """Декодер для типа STRING."""

    _NULL_TERMINATOR = int.from_bytes(b"\x00", "big")

    @staticmethod
    def decode(data: memoryview) -> tuple[KBEString, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEString, Offset]: decoded data and offset

        """
        index = 0
        for index, b in enumerate(data):  # noqa: B007
            if b == STRING._NULL_TERMINATOR:
                break
        size = index + 1  # string + null terminator
        value = data[:index].tobytes().decode()

        return KBEString(value), size

    @staticmethod
    def encode(value: KBEString) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        encoded = value.encode("utf-8")
        return struct.pack(f"={len(encoded) + 1}s", encoded)


class UNICODE(IKBETypeDecoder[KBEUnicode]):
    """Декодер для типа UNICODE."""

    @staticmethod
    def decode(data: memoryview) -> tuple[KBEUnicode, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEUnicode, Offset]: decoded data and offset

        """
        encoded, offset = BLOB.decode(data)
        return KBEUnicode(encoded.decode("utf-8")), offset

    @staticmethod
    def encode(value: KBEUnicode) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return BLOB.encode(KBEBlob(value.encode()))


class PYTHON(IKBETypeDecoder[KBEPython]):
    """Декодер для типа PYTHON."""

    @staticmethod
    def decode(data: memoryview) -> tuple[KBEPython, Offset]:
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

    @staticmethod
    def encode(value: KBEPython) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        bytes_ = pickle.dumps(value)
        return BLOB.encode(KBEBlob(bytes_))


class PY_DICT(PYTHON):  # noqa: N801 # pylint: disable=invalid-name
    """Декодер для типа PY_DICT."""


class PY_TUPLE(PYTHON):  # noqa: N801 # pylint: disable=invalid-name
    """Декодер для типа PY_TUPLE."""


class PY_LIST(PYTHON):  # noqa: N801 # pylint: disable=invalid-name
    """Декодер для типа PY_LIST."""


# TODO: [burov_alexey@mail.ru 05.07.2025 15:57]
# реализован не был до этого. Может и не нужен пока на клиенте.
class ENTITYCALL(IKBETypeDecoder):
    """Декодер для типа ENTITYCALL."""


class BLOB(IKBETypeDecoder[KBEBlob]):
    """Декодер для типа BLOB."""

    @staticmethod
    def decode(data: memoryview) -> tuple[KBEBlob, Offset]:
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

    @staticmethod
    def encode(value: KBEBlob) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return struct.pack(f"=I{len(value)}s", len(value), value)
