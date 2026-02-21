"""Интерфейс энкодера/декодера типа данных KBEngine от другого компонента."""

from abc import ABC, abstractmethod
from typing import ClassVar, Generic, Self, TypeAlias, TypeVar

from enki.kbetype.ikbetype import IKBEType

Offset: TypeAlias = int

_T = TypeVar("_T", bound=IKBEType)


class IKBETypeDecoder(ABC, Generic[_T]):
    """The interface of KBE KBEngine-message value decoder / encoder."""

    _aliases: ClassVar[list[str]] = []
    _kbe_type: type[_T]

    @classmethod
    def get_kbe_type(cls) -> type[_T]:
        return cls._kbe_type

    @classmethod
    @abstractmethod
    def decode(cls, data: memoryview) -> tuple[_T, Offset]:
        """Decode bytes to a python type.

        Returns decoded data and offset.
        """

    @classmethod
    @abstractmethod
    def encode(cls, value: _T) -> bytes:
        """Encode a python type to bytes."""

    # [2026-02-05 12:24 burov_alexey@mail.ru]:
    # Если нужны алиасы, то он по сложнее должен быть
    @classmethod
    def create_alias(cls, alias_name: str) -> type[Self]:
        cls._aliases.append(alias_name)
        return cls
