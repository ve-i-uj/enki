"""Декодеры / энкодеры для данные message типов KBEngine."""

from __future__ import annotations

import struct
from typing import TypeAlias

from enki.kbetype.basic_data_types import (
    KBEFloat,
    KBEInt32,
    KBEInt8,
    KBEString,
    KBEUInt16,
    KBEUInt32,
    KBEUInt64,
)
from enki.kbetype.ikbetype import IKBEType

from .basic_data_type_decoders import FLOAT, INT8, INT32, STRING, UINT16, UINT32, UINT64
from .idecoder import IKBETypeDecoder, Offset

# TODO: [burov_alexey@mail.ru 06.07.2025 07:49]
# Модуль, возможно, стоит перенести в его предметную область. Где он будет
# расширять пакет.


class KBERowByteData(IKBEType, bytes):
    """Сырые данные до конца буфера (без фиксированной длины и декодирования)."""


class UINT8_ARRAY(IKBETypeDecoder[KBERowByteData]):  # noqa: N801 # pylint: disable=invalid-name
    """Родительский класс декодер для FIXED_DICT."""

    @classmethod
    def decode(cls, data: memoryview) -> tuple[KBERowByteData, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBERowByteData, Offset]: decoded data and offset

        """
        return KBERowByteData(data.obj), len(data)

    @classmethod
    def encode(cls, value: KBERowByteData) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return bytes(value)


class KBEEndlessBlob(IKBEType, bytes):
    """Сырые данные байты до конца буфера (без фиксированной длины)."""


class ENDLESS_BLOB(IKBETypeDecoder[KBEEndlessBlob]):  # noqa: N801 # pylint: disable=invalid-name
    """Родительский класс декодер для ENDLESS_BLOB."""

    @classmethod
    def decode(cls, data: memoryview) -> tuple[KBEEndlessBlob, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEEndlessBlob, Offset]: decoded data and offset

        """
        length = len(data)
        if length == 0:
            return KBEEndlessBlob(b""), 0

        return struct.unpack(f"={length}s", data)[0], length

    @classmethod
    def encode(cls, value: KBEEndlessBlob) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return struct.pack(f"={len(value)}", value)


class KBEBool(IKBEType, int):
    """Декодированный bool."""


class BOOL(IKBETypeDecoder[KBEBool]):
    """Декодер для типа UINT8."""

    @staticmethod
    def decode(data: memoryview) -> tuple[KBEBool, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEBool, Offset]: decoded data and offset

        """
        return KBEBool(1 if INT8.decode(data)[0] > 0 else 0), 1

    @staticmethod
    def encode(value: KBEBool) -> bytes:
        """Encode a python type to bytes."""  # noqa: DOC201
        return INT8.encode(KBEInt8(1 if value else 0))


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

# id типа компонента
COMPONENT_TYPE: TypeAlias = INT32
KBEComponentTypeId: TypeAlias = KBEInt32

# id компонентов
COMPONENT_ID: TypeAlias = UINT64
KBEComponentId: TypeAlias = KBEUInt64

# TODO: [burov_alexey@mail.ru 13.07.2025 18:55]
# Хз что это
COMPONENT_ORDER: TypeAlias = INT32
KBEComponentOrderId: TypeAlias = KBEInt32

# TODO: [burov_alexey@mail.ru 13.07.2025 18:55]
# Хз что это
COMPONENT_GUS: TypeAlias = INT32
KBEComponentGusId: TypeAlias = KBEInt32

SHUTDOWN_STATE: TypeAlias = INT8
KBEShutdownState: TypeAlias = KBEInt8

GAME_TIME: TypeAlias = UINT32
CALLBACK_ID: TypeAlias = UINT32
ENTITY_SCRIPT_UID: TypeAlias = UINT16
DBID: TypeAlias = UINT64

UID: TypeAlias = INT32
KBEUid: TypeAlias = KBEInt32

USERNAME: TypeAlias = STRING
KBEUsername: TypeAlias = KBEString

INTADDR: TypeAlias = UINT32
KBEIntAddr: TypeAlias = KBEUInt32

INTPORT: TypeAlias = UINT16
KBEIntPort: TypeAlias = KBEUInt16

EXTADDREX: TypeAlias = STRING
KBEExtAddrEx: TypeAlias = KBEString

PID: TypeAlias = UINT32
KBEPid: TypeAlias = KBEUInt32

CPU: TypeAlias = FLOAT
KBECpu: TypeAlias = KBEFloat

MEM: TypeAlias = FLOAT
KBEMem: TypeAlias = KBEFloat

USEDMEM: TypeAlias = UINT32
KBEUsedMem: TypeAlias = KBEUInt32

STATE: TypeAlias = INT8
KBEStateId: TypeAlias = KBEInt8

MACHINEID: TypeAlias = UINT32
KBEMachineId: TypeAlias = KBEUInt32

EXTRADATA: TypeAlias = UINT64
KBEExtraData: TypeAlias = KBEUInt64

MACMD5 = INT32
KBEMacMd5 = KBEInt32

# pylint: enable=invalid-name
