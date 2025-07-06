"""Декодеры / энкодеры для данные message типов KBEngine."""

from __future__ import annotations

import abc
import struct
from typing import TypeAlias

from enki.core.kbetype.libtypes.decoded_types import (
    DecodedArray,
    DecodedBool,
    DecodedEndlessBlob,
    DecodedFixedDict,
    DecodedInt8,
    DecodedRowByteData,
    DecodedUInt32,
)

from .basic_data_types import INT8, INT32, UINT16, UINT32, UINT64
from .idecoder import IKBETypeDecoder, Offset


class ARRAY(IKBETypeDecoder[DecodedArray]):
    """Родительский класс декодер для всех подтипов ARRAY."""

    @classmethod
    @abc.abstractmethod
    def get_element_decoder(cls) -> type[IKBETypeDecoder]:
        """Возвращает декодер для элементов массива."""

    @classmethod
    def decode(cls, data: memoryview) -> tuple[DecodedArray, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[DecodedArray, Offset]: decoded data and offset

        """
        # number of bytes contained array data
        length, offset = UINT32.decode(data)
        data = data[offset:]
        if length == 0:
            return DecodedArray([]), offset

        result = []
        total_offset = offset
        for _ in range(length):
            value, offset = cls.get_element_decoder().decode(data)
            data = data[offset:]
            total_offset += offset
            result.append(value)

        return DecodedArray(result), total_offset

    @classmethod
    def encode(cls, value: DecodedArray) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        if len(value) == 0:
            return UINT32.encode(DecodedUInt32(0))

        return UINT32.encode(DecodedUInt32(len(value))) + b"".join(
            cls.get_element_decoder().encode(el) for el in value
        )


FixedDictKeyName: TypeAlias = str


class FIXED_DICT(IKBETypeDecoder[DecodedFixedDict]):  # noqa: N801 # pylint: disable=invalid-name
    """Родительский класс декодер для всех подтипов FIXED_DICT."""

    @classmethod
    @abc.abstractmethod
    def get_pairs_dectoders(cls) -> dict[FixedDictKeyName, IKBETypeDecoder]:
        """Возвращает декодеры для значений ключей."""

    @classmethod
    def decode(cls, data: memoryview) -> tuple[DecodedFixedDict, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[DecodedFixedDict, Offset]: decoded data and offset

        """
        result = DecodedFixedDict()
        total_offset = 0
        for key, kbe_type in cls.get_pairs_dectoders().items():
            value, offset = kbe_type.decode(data)
            data = data[offset:]
            result[key] = value
            total_offset += offset
        return result, total_offset

    @classmethod
    def encode(cls, value: DecodedFixedDict) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        data = b""
        for k, v in value.values():
            assert k in cls.get_pairs_dectoders()
            data += cls.get_pairs_dectoders()[k].encode(v)

        return data


class UINT8_ARRAY(IKBETypeDecoder[DecodedRowByteData]):  # noqa: N801 # pylint: disable=invalid-name
    """Родительский класс декодер для FIXED_DICT."""

    @classmethod
    def decode(cls, data: memoryview) -> tuple[DecodedRowByteData, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[DecodedRowByteData, Offset]: decoded data and offset

        """
        return DecodedRowByteData(data.obj), len(data)

    @classmethod
    def encode(cls, value: DecodedRowByteData) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return bytes(value)


class ENDLESS_BLOB(IKBETypeDecoder[DecodedEndlessBlob]):  # noqa: N801 # pylint: disable=invalid-name
    """Родительский класс декодер для ENDLESS_BLOB."""

    @classmethod
    def decode(cls, data: memoryview) -> tuple[DecodedEndlessBlob, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[DecodedEndlessBlob, Offset]: decoded data and offset

        """
        length = len(data)
        if length == 0:
            return DecodedEndlessBlob(b""), 0

        return struct.unpack(f"={length}s", data)[0], length

    @classmethod
    def encode(cls, value: DecodedEndlessBlob) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return struct.pack(f"={len(value)}", value)


class BOOL(IKBETypeDecoder[DecodedBool]):
    """Декодер для типа UINT8."""

    @staticmethod
    def decode(data: memoryview) -> tuple[DecodedBool, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[DecodedBool, Offset]: decoded data and offset

        """
        return DecodedBool(1 if INT8.decode(data)[0] > 0 else 0), 1

    @staticmethod
    def encode(value: DecodedBool) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return INT8.encode(DecodedInt8(1 if value else 0))


# TODO: [burov_alexey@mail.ru 06.07.2025 05:43]
# Хз
# KBE_DATATYPE2ID_MAX: _TODOType = _TODOType("KBE_DATATYPE2ID_MAX")
# ENTITY_COMPONENT: _EntityComponent = _EntityComponent("ENTITY_COMPONENT")

# TODO: [burov_alexey@mail.ru 06.07.2025 05:44]
# Если это относится к парсингу сущностей, то туда в этот пакет и нужно убрать эти декодеры


# pylint: disable=invalid-name

# Id of type from types.xml
DATATYPE_UID: TypeAlias = UINT16
ENTITY_ID: TypeAlias = INT32

# *** Application defined types ***

SPACE_ID: TypeAlias = UINT32
SERVER_ERROR: TypeAlias = UINT16
ENTITY_PROPERTY_UID: TypeAlias = UINT16
ENTITY_METHOD_UID: TypeAlias = UINT16
MESSAGE_ID: TypeAlias = UINT16
MESSAGE_LENGTH: TypeAlias = UINT16
COMPONENT_TYPE: TypeAlias = INT32
COMPONENT_ID: TypeAlias = UINT64
COMPONENT_ORDER: TypeAlias = INT32
COMPONENT_GUS: TypeAlias = INT32
SHUTDOWN_STATE: TypeAlias = INT8
GAME_TIME: TypeAlias = UINT32
CALLBACK_ID: TypeAlias = UINT32
ENTITY_SCRIPT_UID: TypeAlias = UINT16
DBID: TypeAlias = UINT64

# pylint: enable=invalid-name
