"""Абстрактные классы для декодеров / энкодеров коллекций KBEngine.

Типы ARRAY и FIXED_DICT напрямую не инстанцируются. По архитектуре KBEngine они
используются, как родительские классы для создания пользовательских типов слоя
бизнес-логики.
"""

from __future__ import annotations

import abc
from typing import Generic, TypeAlias, TypeVar

from enki.kbetype.ikbetype import IKBETypeDecoder, Offset
from enki.kbetype.pytypes.basic_data_types import KBEUInt32
from enki.kbetype.pytypes.collections import KBEArray, KBEFixedDict

from .basic_data_type_decoders import UINT32

_T_IKBETypeDecoderOfArrayElement = TypeVar(
    "_T_IKBETypeDecoderOfArrayElement", bound=IKBETypeDecoder
)


class ARRAY(Generic[_T_IKBETypeDecoderOfArrayElement]):
    """Родительский класс декодер для всех подтипов ARRAY."""

    @classmethod
    @abc.abstractmethod
    def get_element_decoder(cls) -> type[_T_IKBETypeDecoderOfArrayElement]:
        """Возвращает декодер для элементов массива."""

    @classmethod
    def _decode(cls, data: memoryview) -> tuple[KBEArray, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEArray, Offset]: decoded data and offset

        """
        # number of bytes contained array data
        length, offset = UINT32.decode(data)
        data = data[offset:]
        if length == 0:
            return KBEArray([]), offset

        result = []
        total_offset = offset
        for _ in range(length):
            value, offset = cls.get_element_decoder().decode(data)
            data = data[offset:]
            total_offset += offset
            result.append(value)

        return KBEArray(result), total_offset

    @classmethod
    def _encode(cls, value: KBEArray) -> bytes:
        """Encode a python type to bytes."""
        if len(value) == 0:
            return UINT32.encode(KBEUInt32(0))

        return UINT32.encode(KBEUInt32(len(value))) + b"".join(
            cls.get_element_decoder().encode(el) for el in value
        )


# DBID_DESCR = DataTypeDescr(
#     id=3,
#     base_type_name="UINT64",
#     name="DBID",
#     kbetype=UINT64.create_alias("DBID"),
# )
# DBID: TypeAlias = UINT64


# class KBEArrayOfDdid(KBEArray):
#     """Тип элемента KBEngine-массива типа 'ARRAY_23'."""


# class ARRAY_23(ARRAY):
#     """Декодер типа 'ARRAY_23'."""

#     @classmethod
#     def get_element_decoder(cls) -> type[DBID]:
#         """Возвращает декодер для элементов массива."""
#         return DBID

#     @staticmethod
#     def decode(data: memoryview) -> tuple[KBEArrayOfDdid, Offset]:
#         """Decode bytes to a python type.

#         Returns decoded data and offset.
#         """
#         kbe_arr, offset = ARRAY_23._decode(data)
#         res_arr = KBEArrayOfDdid(kbe_arr)
#         return res_arr, offset

#     @staticmethod
#     def encode(value: KBEArrayOfDdid) -> bytes:
#         """Encode a python type to bytes."""
#         return ARRAY_23._encode(value)


# # ARRAY_23_DESCR = DataTypeDescr(
#     id=23,
#     base_type_name="ARRAY",
#     name="ARRAY_23",
#     of=DBID_DESCR.kbetype,
#     kbetype=ARRAY.build("ARRAY_23", DBID_DESCR.kbetype),
# )


FixedDictKeyName: TypeAlias = str


class FIXED_DICT(IKBETypeDecoder[KBEFixedDict]):  # noqa: N801 # pylint: disable=invalid-name
    """Родительский класс декодер для всех подтипов FIXED_DICT."""

    @classmethod
    @abc.abstractmethod
    def get_values_decoders(cls) -> dict[FixedDictKeyName, IKBETypeDecoder]:
        """Возвращает декодеры для значений ключей."""

    @classmethod
    def _decode(cls, data: memoryview) -> tuple[KBEFixedDict, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEFixedDict, Offset]: decoded data and offset

        """
        result = KBEFixedDict()
        total_offset = 0
        for key, kbe_type in cls.get_values_decoders().items():
            value, offset = kbe_type.decode(data)
            data = data[offset:]
            result[key] = value
            total_offset += offset
        return result, total_offset

    @classmethod
    def _encode(cls, value: KBEFixedDict) -> bytes:
        """Encode a python type to bytes."""
        data = b""
        for k, v in value.values():
            assert k in cls.get_values_decoders()
            data += cls.get_values_decoders()[k].encode(v)

        return data


__all__ = [
    "ARRAY",
    "FIXED_DICT",
]
