"""Интерфейс для типа KBEngine полученного от другого компонента."""

import abc
from typing import Generic, TypeAlias, TypeVar


class IKBEType(abc.ABC):  # noqa: B024
    """Интерфейс для всех типов, полученных из бинарного представления."""


Offset: TypeAlias = int

_T_IKBEType = TypeVar("_T_IKBEType", bound=IKBEType)  # pylint: disable=invalid-name


class IKBETypeDecoder(abc.ABC, Generic[_T_IKBEType]):
    """The interface of KBE KBEngine-message value decoder / encoder."""

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


__all__ = ["IKBEType"]
