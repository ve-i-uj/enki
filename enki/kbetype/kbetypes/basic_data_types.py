"""Базовые типы из "kbengine_api.chm" (Basic data types)."""

from __future__ import annotations

from enki.kbetype.vectors import Vector2, Vector3, Vector4

from .ikbetype import IKBEType


class KBEUInt8(IKBEType, int):
    """UInt8 из бинарного представления (наследник 'int')."""


class KBEUInt16(IKBEType, int):
    """UInt16 из бинарного представления (наследник 'int')."""


class KBEUInt32(IKBEType, int):
    """UInt32 из бинарного представления (наследник 'int')."""


class KBEUInt64(IKBEType, int):
    """UInt64 из бинарного представления (наследник 'int')."""


class KBEInt8(IKBEType, int):
    """Int8 из бинарного представления (наследник 'int')."""


class KBEInt16(IKBEType, int):
    """Int16 из бинарного представления (наследник 'int')."""


class KBEInt32(IKBEType, int):
    """Int32 из бинарного представления (наследник 'int')."""


class KBEInt64(IKBEType, int):
    """Int64 из бинарного представления (наследник 'int')."""


class KBEFloat(IKBEType, float):
    """Float из бинарного представления (наследник 'float')."""


class KBEDouble(IKBEType, float):
    """Double из бинарного представления (наследник 'float')."""


class KBEVector2(IKBEType, Vector2):
    """Двумерный вектор, представляющий данные из бинарного представления."""


class KBEVector3(IKBEType, Vector3):
    """Трёхмерный вектор, представляющий данные из бинарного представления."""


class KBEVector4(IKBEType, Vector4):
    """Четырёхмерный вектор, представляющий данные из бинарного представления."""


class KBEString(IKBEType, str):
    """Строка из бинарного представления."""

    __slots__ = ()


class KBEUnicode(IKBEType, str):
    """Unicode из бинарного представления (в стиле python2.7)."""

    __slots__ = ()


class KBEPython(IKBEType):
    """Любой объект python полученный из pickle."""


class KBEPyDict(IKBEType, dict):
    """Словарь из бинарного представления (наследник dict)."""


class KBEPyTuple(IKBEType, tuple):
    """Кортеж из бинарного представления (наследник tuple)."""

    __slots__ = ()


class KBEPyList(IKBEType, list):
    """Список из бинарного представления (наследник list)."""


class KBEEntityCall(IKBEType):
    """Вызов удалённого метода сущности из бинарного представления."""


class KBEBlob(IKBEType, bytes):
    """Сырые байты из бинарного представления (наследник bytes)."""
