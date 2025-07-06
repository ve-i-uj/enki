"""Декодеры / энкодеры для данные message типов KBEngine."""

from __future__ import annotations

import abc
from typing import Generic, TypeAlias, TypeVar

from enki.core.kbetype.decoder.decoded_types import (
    IDecodedType,
)

Offset: TypeAlias = int

T_IDecodedType = TypeVar("T_IDecodedType", bound=IDecodedType)  # pylint: disable=invalid-name
DecodedValueType: TypeAlias = T_IDecodedType

DecodedValueInfo = tuple[Offset, DecodedValueType]


class IKBETypeDecoder(abc.ABC, Generic[T_IDecodedType]):
    """The interface of KBE данные message-type decoder / encoder."""

    @staticmethod
    @abc.abstractmethod
    def decode(data: memoryview) -> tuple[T_IDecodedType, Offset]:
        """Decode bytes to a python type.

        Returns decoded data and offset.
        """

    @staticmethod
    @abc.abstractmethod
    def encode(value: T_IDecodedType) -> bytes:
        """Encode a python type to bytes."""
