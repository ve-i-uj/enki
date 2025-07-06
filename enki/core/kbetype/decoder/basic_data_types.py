"""Декодеры / энкодеры для данные message типов KBEngine."""

from __future__ import annotations

import pickle  # noqa: S403
import struct
import typing

from enki.core.kbetype.libtypes.decoded_types import (
    DecodedBlob,
    DecodedDouble,
    DecodedFloat,
    DecodedInt8,
    DecodedInt16,
    DecodedInt32,
    DecodedInt64,
    DecodedPython,
    DecodedString,
    DecodedUInt8,
    DecodedUInt16,
    DecodedUInt32,
    DecodedUInt64,
    DecodedUnicode,
    DecodedVector2,
    DecodedVector3,
    DecodedVector4,
)

from .idecoder import IKBETypeDecoder, Offset


class UINT8(IKBETypeDecoder[DecodedUInt8]):
    """Декодер для типа UINT8."""

    @staticmethod
    def decode(data: memoryview) -> tuple[DecodedUInt8, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[DecodedUInt8, Offset]: decoded data and offset

        """
        offset = 1
        value: DecodedUInt8 = struct.unpack("=B", data[:offset])[0]
        return value, offset

    @staticmethod
    def encode(value: DecodedUInt8) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return struct.pack("=B", value)


class UINT16(IKBETypeDecoder[DecodedUInt16]):
    """Декодер для типа UINT16."""

    @staticmethod
    def decode(data: memoryview) -> tuple[DecodedUInt16, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[DecodedUInt16, Offset]: decoded data and offset

        """
        offset = 2
        value: DecodedUInt16 = struct.unpack("=H", data[:offset])[0]
        return value, offset

    @staticmethod
    def encode(value: DecodedUInt16) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return struct.pack("=H", value)


class UINT32(IKBETypeDecoder[DecodedUInt32]):
    """Декодер для типа UINT32."""

    @staticmethod
    def decode(data: memoryview) -> tuple[DecodedUInt32, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[DecodedUInt32, Offset]: decoded data and offset

        """
        offset = 4
        value: DecodedUInt32 = struct.unpack("=I", data[:offset])[0]
        return value, offset

    @staticmethod
    def encode(value: DecodedUInt32) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return struct.pack("=I", value)


class UINT64(IKBETypeDecoder[DecodedUInt64]):
    """Декодер для типа UINT64."""

    @staticmethod
    def decode(data: memoryview) -> tuple[DecodedUInt64, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[DecodedUInt64, Offset]: decoded data and offset

        """
        offset = 8
        value: DecodedUInt64 = struct.unpack("=Q", data[:offset])[0]
        return value, offset

    @staticmethod
    def encode(value: DecodedUInt64) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return struct.pack("=Q", value)


class INT8(IKBETypeDecoder[DecodedInt8]):
    """Декодер для типа INT8."""

    @staticmethod
    def decode(data: memoryview) -> tuple[DecodedInt8, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[DecodedInt8, Offset]: decoded data and offset

        """
        offset = 1
        value: DecodedInt8 = struct.unpack("=b", data[:offset])[0]
        return value, offset

    @staticmethod
    def encode(value: DecodedInt8) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return struct.pack("=b", value)


class INT16(IKBETypeDecoder[DecodedInt16]):
    """Декодер для типа INT16."""

    @staticmethod
    def decode(data: memoryview) -> tuple[DecodedInt16, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[DecodedInt16, Offset]: decoded data and offset

        """
        offset = 2
        value: DecodedInt16 = struct.unpack("=h", data[:offset])[0]
        return value, offset

    @staticmethod
    def encode(value: DecodedInt16) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return struct.pack("=h", value)


class INT32(IKBETypeDecoder[DecodedInt32]):
    """Декодер для типа INT32."""

    @staticmethod
    def decode(data: memoryview) -> tuple[DecodedInt32, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[DecodedInt32, Offset]: decoded data and offset

        """
        offset = 4
        value: DecodedInt32 = struct.unpack("=i", data[:offset])[0]
        return value, offset

    @staticmethod
    def encode(value: DecodedInt32) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return struct.pack("=i", value)


class INT64(IKBETypeDecoder[DecodedInt64]):
    """Декодер для типа INT64."""

    @staticmethod
    def decode(data: memoryview) -> tuple[DecodedInt64, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[DecodedInt64, Offset]: decoded data and offset

        """
        offset = 8
        value: DecodedInt64 = struct.unpack("=q", data[:offset])[0]
        return value, offset

    @staticmethod
    def encode(value: DecodedInt64) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return struct.pack("=q", value)


class FLOAT(IKBETypeDecoder[DecodedFloat]):
    """Декодер для типа FLOAT."""

    @staticmethod
    def decode(data: memoryview) -> tuple[DecodedFloat, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[DecodedFloat, Offset]: decoded data and offset

        """
        offset = 4
        value: DecodedFloat = struct.unpack("=f", data[:offset])[0]
        return value, offset

    @staticmethod
    def encode(value: DecodedFloat) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return struct.pack("=f", value)


class DOUBLE(IKBETypeDecoder[DecodedDouble]):
    """Декодер для типа DOUBLE."""

    @staticmethod
    def decode(data: memoryview) -> tuple[DecodedDouble, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[DecodedDouble, Offset]: decoded data and offset

        """
        offset = 8
        value: DecodedDouble = struct.unpack("=d", data[:offset])[0]
        return value, offset

    @staticmethod
    def encode(value: DecodedDouble) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return struct.pack("=d", value)


class VECTOR2(IKBETypeDecoder[DecodedVector2]):
    """Декодер для типа VECTOR2."""

    @staticmethod
    def decode(data: memoryview) -> tuple[DecodedVector2, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[DecodedVector2, Offset]: decoded data and offset

        """
        total_offset = 0

        x_value, offset = FLOAT.decode(data)
        data = data[offset:]
        total_offset += offset

        y_value, offset = FLOAT.decode(data)
        data = data[offset:]
        total_offset += offset

        return DecodedVector2(x_value, y_value), total_offset

    @staticmethod
    def encode(value: DecodedVector2) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        # TODO: [burov_alexey@mail.ru 05.07.2025 15:26]
        # Возможно, что неправильно реализовано, т.к. до этого момента в обще
        # ничего не было.
        data = b""

        data += FLOAT.encode(DecodedFloat(value.x))
        data += FLOAT.encode(DecodedFloat(value.y))

        return data


class VECTOR3(IKBETypeDecoder[DecodedVector3]):
    """Декодер для типа VECTOR3."""

    @staticmethod
    def decode(data: memoryview) -> tuple[DecodedVector3, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[DecodedVector3, Offset]: decoded data and offset

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

        return DecodedVector3(x_value, y_value, z_value), total_offset

    @staticmethod
    def encode(value: DecodedVector3) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        data = b""

        data += FLOAT.encode(DecodedFloat(value.x))
        data += FLOAT.encode(DecodedFloat(value.y))
        data += FLOAT.encode(DecodedFloat(value.z))

        return data


class VECTOR4(IKBETypeDecoder[DecodedVector4]):
    """Декодер для типа VECTOR4."""

    @staticmethod
    def decode(data: memoryview) -> tuple[DecodedVector4, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[DecodedVector4, Offset]: decoded data and offset

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

        return DecodedVector4(x_value, y_value, z_value, w_value), total_offset

    @staticmethod
    def encode(value: DecodedVector4) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        data = b""

        data += FLOAT.encode(DecodedFloat(value.x))
        data += FLOAT.encode(DecodedFloat(value.y))
        data += FLOAT.encode(DecodedFloat(value.z))
        data += FLOAT.encode(DecodedFloat(value.w))

        return data


class STRING(IKBETypeDecoder[DecodedString]):
    """Декодер для типа STRING."""

    _NULL_TERMINATOR = int.from_bytes(b"\x00", "big")

    @staticmethod
    def decode(data: memoryview) -> tuple[DecodedString, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[DecodedString, Offset]: decoded data and offset

        """
        index = 0
        for index, b in enumerate(data):  # noqa: B007
            if b == STRING._NULL_TERMINATOR:
                break
        size = index + 1  # string + null terminator
        value = data[:index].tobytes().decode()

        return DecodedString(value), size

    @staticmethod
    def encode(value: DecodedString) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        encoded = value.encode("utf-8")
        return struct.pack(f"={len(encoded) + 1}s", encoded)


class UNICODE(IKBETypeDecoder[DecodedUnicode]):
    """Декодер для типа UNICODE."""

    @staticmethod
    def decode(data: memoryview) -> tuple[DecodedUnicode, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[DecodedUnicode, Offset]: decoded data and offset

        """
        encoded, offset = BLOB.decode(data)
        return DecodedUnicode(encoded.decode("utf-8")), offset

    @staticmethod
    def encode(value: DecodedUnicode) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return BLOB.encode(DecodedBlob(value.encode()))


class PYTHON(IKBETypeDecoder[DecodedPython]):
    """Декодер для типа PYTHON."""

    @staticmethod
    def decode(data: memoryview) -> tuple[DecodedPython, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[DecodedPython, Offset]: decoded data and offset

        """
        bytes_, offset = BLOB.decode(data)
        obj = pickle.loads(bytes_)  # noqa: S301

        obj = typing.cast("DecodedPython", obj)
        return obj, offset

    @staticmethod
    def encode(value: DecodedPython) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        bytes_ = pickle.dumps(value)
        return BLOB.encode(DecodedBlob(bytes_))


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


class BLOB(IKBETypeDecoder[DecodedBlob]):
    """Декодер для типа BLOB."""

    @staticmethod
    def decode(data: memoryview) -> tuple[DecodedBlob, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[DecodedBlob, Offset]: decoded data and offset

        """
        length, offset = UINT32.decode(data)
        if length == 0:
            return DecodedBlob(b""), offset
        size = offset + length

        return struct.unpack(f"={length}s", data[offset:size])[0], size

    @staticmethod
    def encode(value: DecodedBlob) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return struct.pack(f"=I{len(value)}s", len(value), value)


# # TODO: [burov_alexey@mail.ru 05.07.2025 14:50]
# # Алиасы выдаются уже в entity-rpc. Это не относится к декодированию.
# @classmethod
# def create_alias(cls, alias_name: str) -> type[UINT8]:
#     """Create alias of the "self" type."""

# TODO: [2022-11-18 15:54 burov_alexey@mail.ru]:
# Сервер может прислать потенциально число, которое больше,
# чем Python может поменять по формату "f". Пока так.
# if value > 2147483647 or value < -2147483647:
#     value = 0


# @dataclass
# class EntityComponentData:
#     component_type: int
#     owner_id: int
#     component_ent_id: int
#     count: int
#     entity_component_property_id: Optional[int] = None
#     name: Optional[str] = None
#     properties: dict[Any, Any] = dataclasses.field(default_factory=dict)


# class _EntityComponent(_BaseKBEType):
#     @property
#     def default(self) -> EntityComponentData:
#         return EntityComponentData(0, 0, 0, 0)

#     def decode(self, data: memoryview) -> Tuple[EntityComponentData, int]:
#         shift = 0
#         component_type, offset = UINT32.decode(data)
#         shift += offset
#         # TODO: [2022-08-27 10:31 burov_alexey@mail.ru]:
#         # Тут падает. Может быть из-за того, что если прокси создана
#         owner_id, offset = INT32.decode(data[shift:])
#         shift += offset

#         # UInt16 ComponentDescrsType ???
#         component_ent_id, offset = UINT16.decode(data[shift:])
#         shift += offset

#         count, offset = UINT16.decode(data[shift:])
#         shift += offset

#         inst = EntityComponentData(component_type, owner_id, component_ent_id, count)
#         return inst, shift

#     def encode(self, value: Any) -> bytes:
#         raise NotImplementedError
