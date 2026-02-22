"""Базовые типы из "kbengine_api.chm" (Basic data types)."""

from __future__ import annotations

from enki.kbetype.ikbetype import IKBEType
from enki.kbetype.pytypes.vectors import Vector2, Vector3, Vector4


class KBEUInt8(IKBEType, int):
    """UInt8 из бинарного представления (наследник 'int')."""

    def __new__(cls, value: int = 0):
        if not 0 <= value <= 255:  # noqa: PLR2004
            msg = f"KBEUInt8 value must be between 0 and 255, got {value}"
            raise ValueError(msg)
        return super().__new__(cls, value)


class KBEUInt16(IKBEType, int):
    """UInt16 из бинарного представления (наследник 'int')."""

    def __new__(cls, value: int = 0):
        if not 0 <= value <= 65535:  # noqa: PLR2004
            msg = f"KBEUInt16 value must be between 0 and 65535, got {value}"
            raise ValueError(msg)
        return super().__new__(cls, value)


class KBEUInt32(IKBEType, int):
    """UInt32 из бинарного представления (наследник 'int')."""

    def __new__(cls, value: int = 0):
        if not 0 <= value <= 4294967295:  # noqa: PLR2004
            msg = (
                f"KBEUInt32 value must be between 0 and 4294967295, got {value}"
            )
            raise ValueError(msg)
        return super().__new__(cls, value)


class KBEUInt64(IKBEType, int):
    """UInt64 из бинарного представления (наследник 'int')."""

    def __new__(cls, value: int = 0):
        if not 0 <= value <= 18446744073709551615:  # noqa: PLR2004
            msg = (
                f"KBEUInt64 value must be between 0 and "
                f"18446744073709551615, got {value}"
            )
            raise ValueError(msg)
        return super().__new__(cls, value)


class KBEInt8(IKBEType, int):
    """Int8 из бинарного представления (наследник 'int')."""

    def __new__(cls, value: int = 0):
        if not -128 <= value <= 127:  # noqa: PLR2004
            msg = f"KBEInt8 value must be between -128 and 127, got {value}"
            raise ValueError(msg)
        return super().__new__(cls, value)


class KBEInt16(IKBEType, int):
    """Int16 из бинарного представления (наследник 'int')."""

    def __new__(cls, value: int = 0):
        if not -32768 <= value <= 32767:  # noqa: PLR2004
            msg = (
                f"KBEInt16 value must be between -32768 and 32767, got {value}"
            )
            raise ValueError(msg)
        return super().__new__(cls, value)


class KBEInt32(IKBEType, int):
    """Int32 из бинарного представления (наследник 'int')."""

    def __new__(cls, value: int = 0):
        if not -2147483648 <= value <= 2147483647:  # noqa: PLR2004
            msg = (
                f"KBEInt32 value must be between -2147483648 and "
                f"2147483647, got {value}"
            )
            raise ValueError(msg)
        return super().__new__(cls, value)


class KBEInt64(IKBEType, int):
    """Int64 из бинарного представления (наследник 'int')."""

    def __new__(cls, value: int = 0):
        if not -9223372036854775808 <= value <= 9223372036854775807:
            msg = (
                f"KBEInt64 value must be between -9223372036854775808 and "
                f"9223372036854775807, got {value}"
            )
            raise ValueError(msg)
        return super().__new__(cls, value)


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


# *** Это небольшое расширение для удобства описания сообщений ***


class KBERowByteData(IKBEType, bytes):
    """Сырые данные до конца буфера (без фиксированной длины и декодирования)."""


class KBEBool(IKBEType, int):
    """Декодированный bool."""
