"""Абстрактные классы для декодеров / энкодеров коллекций KBEngine.

Типы ARRAY и FIXED_DICT напрямую не инстанцируются. По архитектуре KBEngine они
используются, как родительские классы для создания пользовательских типов слоя
бизнес-логики.
"""

from __future__ import annotations

from dataclasses import dataclass
import dataclasses
from typing import Generic, TypeAlias, TypeVar

from enki.kbetype.decoders.basic_data_type_decoders import UINT32
from enki.kbetype.decoders.idecoders import IKBETypeDecoder, Offset
from enki.kbetype.ikbetype import IKBEType
from enki.kbetype.pytypes.basic_data_types import KBEUInt32
from enki.kbetype.pytypes.collections import (
    KBEArray,
    KBEFixedDict,
)

_AET = TypeVar("_AET", bound=IKBEType)  # Array Element Type
_AEDT = TypeVar("_AEDT", bound=IKBETypeDecoder)  # Array Element Decoder Type


class ARRAY(
    IKBETypeDecoder[KBEArray[_AET]],
    Generic[_AET, _AEDT],
):
    """Родительский класс декодер для всех подтипов ARRAY."""

    _ARR_LEN_DECODER = UINT32

    _element_decoder: type[_AEDT]

    @classmethod
    def _get_element_decoder(cls) -> type[_AEDT]:
        """Возвращает декодер для элементов массива."""
        return cls._element_decoder

    @classmethod
    def decode(cls, data: memoryview) -> tuple[KBEArray[_AET], Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            tuple[KBEArray, Offset]: decoded data and offset

        """
        # number of bytes contained array data
        length, offset = cls._ARR_LEN_DECODER.decode(data)
        data = data[offset:]
        if length == 0:
            return KBEArray([]), offset

        result = []
        total_offset = offset
        for _ in range(length):
            value, offset = cls._get_element_decoder().decode(data)
            data = data[offset:]
            total_offset += offset
            result.append(value)

        return KBEArray(result), total_offset

    @classmethod
    def encode(cls, value: KBEArray[_AET]) -> bytes:
        """Encode a python type to bytes."""
        if len(value) == 0:
            return cls._ARR_LEN_DECODER.encode(KBEUInt32(0))

        return cls._ARR_LEN_DECODER.encode(KBEUInt32(len(value))) + b"".join(
            cls._get_element_decoder().encode(el) for el in value
        )


FixedDictKeyName: TypeAlias = str

# Подклассы KBEFixedDict описывают имена ключей и KBE-типов. Это будет то,
# что выходит из decode. Например:
#
# class EntityKBEFixedDict(KBEFixedDict):
#     entity_id: KBEEntityId
#     name: KBEString
#
# И есть TypedDict с декодерами
#
# class ENTITY_FIXED_DICT(TypedDict):
#     entity_id: ENTITY_ID
#     name: STRING


@dataclass
class FixedDictDecoders:

    def ordered_items(self) -> tuple[tuple[str, IKBETypeDecoder], ...]:
        return tuple(
            (f.name, getattr(self, f.name)) for f in dataclasses.fields(self)
        )


_FDT = TypeVar("_FDT", bound=KBEFixedDict)
_FDDT = TypeVar("_FDDT", bound=FixedDictDecoders)


class FIXED_DICT(IKBETypeDecoder[_FDT], Generic[_FDT, _FDDT]):
    """Родительский класс декодер для всех подтипов FIXED_DICT."""

    _result_type: type[_FDT]
    _decoders: type[_FDDT]

    @classmethod
    def _get_decoders(cls) -> _FDDT:
        return cls._decoders()

    @classmethod
    def _get_result_type(cls) -> type[_FDT]:
        return cls._result_type

    @classmethod
    def decode(cls, data: memoryview) -> tuple[_FDT, Offset]:
        """Decode bytes to a python type.

        Args:
            data (memoryview): bytes for decoding

        Returns:
            decoded data and offset

        """
        decoders_dict = cls._get_decoders()
        result_dict = {}

        total_offset = 0
        for key, kbe_type in decoders_dict.ordered_items():
            value, offset = kbe_type.decode(data)
            data = data[offset:]
            result_dict[key] = value
            total_offset += offset
        return cls._get_result_type()(**result_dict), total_offset

    @classmethod
    def encode(cls, value: _FDT) -> bytes:
        """Encode a python type to bytes."""
        data = b""
        decoders_dict = cls._get_decoders()
        for k, v in value.items():
            assert k in decoders_dict
            data += decoders_dict[k].encode(v)

        return data
