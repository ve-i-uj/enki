"""Интерфейс для типа KBEngine полученного от другого компонента."""

import abc
from typing import ClassVar, Generic, Self, TypeAlias, TypeVar

__all__ = ["IKBEType", "IKBETypeDecoder", "Offset"]


class IKBEType(abc.ABC):  # noqa: B024
    """Интерфейс для всех типов, полученных из бинарного представления."""


Offset: TypeAlias = int

_T_IKBEType = TypeVar("_T_IKBEType", bound=IKBEType)  # pylint: disable=invalid-name


class IKBETypeDecoder(abc.ABC, Generic[_T_IKBEType]):
    """The interface of KBE KBEngine-message value decoder / encoder."""

    _aliases: ClassVar[list[str]] = []

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

    @classmethod
    def create_alias(cls, alias_name: str) -> type[Self]:
        cls._aliases.append(alias_name)
        return cls
