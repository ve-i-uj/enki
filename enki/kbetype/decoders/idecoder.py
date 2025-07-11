"""Декодеры / энкодеры для данные message типов KBEngine."""

from __future__ import annotations

import abc
from typing import Generic, TypeAlias, TypeVar

from enki.kbetype.ikbetype import (
    IKBEType,
)

Offset: TypeAlias = int

_T_IKBEType = TypeVar("_T_IKBEType", bound=IKBEType)  # pylint: disable=invalid-name


class IKBETypeDecoder(abc.ABC, Generic[_T_IKBEType]):
    """The interface of KBE данные message-type decoder / encoder."""

    @staticmethod
    @abc.abstractmethod
    def decode(data: memoryview) -> tuple[_T_IKBEType, Offset]:
        """Decode bytes to a python type.

        Returns decoded data and offset.
        """

    @staticmethod
    @abc.abstractmethod
    def encode(value: _T_IKBEType) -> bytes:
        """Encode a python type to bytes."""


__all__ = ["IKBETypeDecoder", "Offset"]
