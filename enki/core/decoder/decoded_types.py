"""Типы данных, полученные из бинарного представления."""

from __future__ import annotations

import abc

from ..libtypes.vector import Vector2, Vector3, Vector4


class IDecodedType(abc.ABC):  # noqa: B024
    """Родительский класс для всех типов, полученных из бинарного представления."""


class DecodedUInt8(IDecodedType, int):
    """UInt8 из бинарного представления (наследник 'int')."""


class DecodedUInt16(IDecodedType, int):
    """UInt16 из бинарного представления (наследник 'int')."""


class DecodedUInt32(IDecodedType, int):
    """UInt32 из бинарного представления (наследник 'int')."""


class DecodedUInt64(IDecodedType, int):
    """UInt64 из бинарного представления (наследник 'int')."""


class DecodedInt8(IDecodedType, int):
    """Int8 из бинарного представления (наследник 'int')."""


class DecodedInt16(IDecodedType, int):
    """Int16 из бинарного представления (наследник 'int')."""


class DecodedInt32(IDecodedType, int):
    """Int32 из бинарного представления (наследник 'int')."""


class DecodedInt64(IDecodedType, int):
    """Int64 из бинарного представления (наследник 'int')."""


class DecodedFloat(IDecodedType, float):
    """Float из бинарного представления (наследник 'float')."""


class DecodedDouble(IDecodedType, float):
    """Double из бинарного представления (наследник 'float')."""


class DecodedVector2(IDecodedType, Vector2):
    """Двумерный вектор, представляющий данные из бинарного представления."""


class DecodedVector3(IDecodedType, Vector3):
    """Трёхмерный вектор, представляющий данные из бинарного представления."""


class DecodedVector4(IDecodedType, Vector4):
    """Четырёхмерный вектор, представляющий данные из бинарного представления."""


class DecodedString(IDecodedType, str):
    """Строка из бинарного представления."""

    __slots__ = ()


class DecodedUnicode(IDecodedType, str):
    """Unicode из бинарного представления (в стиле python2.7)."""

    __slots__ = ()


class DecodedPython(IDecodedType):
    """Любой объект python полученный из pickle."""


class DecodedPyDict(IDecodedType, dict):
    """Словарь из бинарного представления (наследник dict)."""


class DecodedPyTuple(IDecodedType, tuple):
    """Кортеж из бинарного представления (наследник tuple)."""

    __slots__ = ()


class DecodedPyList(IDecodedType, list):
    """Список из бинарного представления (наследник list)."""


class DecodedEntityCall(IDecodedType):
    """Вызов удалённого метода сущности из бинарного представления."""


class DecodedBlob(IDecodedType, bytes):
    """Сырые байты из бинарного представления (наследник bytes)."""


class DecodedArray(IDecodedType, list):
    """KBEngine-массив из бинарного представления."""


class DecodedFixedDict(IDecodedType, dict):
    """KBEngine-dict with the fixed [non-deletable] keys."""


class DecodedRowByteData(IDecodedType, bytes):
    """Сырые данные до конца буфера (без фиксированной длины и декодирования)."""


class DecodedEndlessBlob(IDecodedType, bytes):
    """Сырые данные байты до конца буфера (без фиксированной длины)."""


class DecodedBool(IDecodedType, int):
    """Декодированный bool."""


# TODO: [burov_alexey@mail.ru 05.07.2025 10:29]
# Это нужно только уже в обработки entityCall и когда меняются свойства
# сущности. А сам тип вектор же нельзя частично передать.

# NO_POS_DIR_VALUE = -1589.123409871

# @abc.abstractmethod
# def merge(self, other: V) -> V:
#     """Залить экземпляр другого вектора в этот экземпляр.

#     От сервера могут прийти события, которые только частично обновляют
#     позицию и направление, но обновить свойство можно только целиком.
#     Поэтому нужно проверить на невыставленные значения.

#     Вектор может быть "частично заполненым", но остаётся валидным.
#     Невыставленное значение - это float константа.
#     """

# TODO: [2025-06-19 02:05 burov_alexey@mail.ru]:
# Эта реализация должна быть общей для всех векторов и быть или
# на дженериках, или объектно. И должна быть в реализации! Здесь только интерфейс.

# TODO: [2025-06-19 02:14 burov_alexey@mail.ru]:
# И реализация совмещения векторов нужна только для сериализации. Это
# другой вектор, не игрвой тогда получается.

# def merge(self, other: IGameVector) -> IGameVector:
#     res = IGameVector(
#         *[s if s is not self.NO_POS_DIR_VALUE else o for s, o in zip(self, other)]
#     )
#     return res
