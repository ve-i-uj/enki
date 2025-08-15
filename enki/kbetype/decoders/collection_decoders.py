"""Абстрактные классы для декодеров / энкодеров коллекций KBEngine.

Типы ARRAY и FIXED_DICT напрямую не инстанцируются. По архитектуре KBEngine они
используются, как родительские классы для создания пользовательских типов слоя
бизнес-логики.
"""

from __future__ import annotations

import abc
from typing import TypeAlias

from enki.kbetype.ikbetype import IKBETypeDecoder, Offset
from enki.kbetype.pytypes.basic_data_types import KBEUInt32
from enki.kbetype.pytypes.collections import KBEArray, KBEFixedDict

from .basic_data_type_decoders import UINT32


class ARRAY(IKBETypeDecoder[KBEArray]):
    """Родительский класс декодер для всех подтипов ARRAY."""

    @classmethod
    @abc.abstractmethod
    def get_element_decoder(cls) -> type[IKBETypeDecoder]:
        """Возвращает декодер для элементов массива."""

    @classmethod
    def decode(cls, data: memoryview) -> tuple[KBEArray, Offset]:
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
    def encode(cls, value: KBEArray) -> bytes:
        """Encode a python type to bytes."""
        if len(value) == 0:
            return UINT32.encode(KBEUInt32(0))

        return UINT32.encode(KBEUInt32(len(value))) + b"".join(
            cls.get_element_decoder().encode(el) for el in value
        )


FixedDictKeyName: TypeAlias = str


class FIXED_DICT(IKBETypeDecoder[KBEFixedDict]):  # noqa: N801 # pylint: disable=invalid-name
    """Родительский класс декодер для всех подтипов FIXED_DICT."""

    @classmethod
    @abc.abstractmethod
    def get_values_decoders(cls) -> dict[FixedDictKeyName, IKBETypeDecoder]:
        """Возвращает декодеры для значений ключей."""

    @classmethod
    def decode(cls, data: memoryview) -> tuple[KBEFixedDict, Offset]:
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
    def encode(cls, value: KBEFixedDict) -> bytes:
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
