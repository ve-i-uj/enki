"""KBE type encoders / decoders."""

from __future__ import annotations

import abc
import collections
import collections.abc
import copy
import dataclasses
import pickle
import struct
from dataclasses import dataclass
from typing import Any, Generator, Tuple, Iterable, Optional, Type
from collections import OrderedDict

from enki.core.enkitype import EnkiType

from ..enkitype import NoValue
from ._collection import FixedDict as _BaseFixedDict
from ._collection import Array as _BaseArray
from ._vector import Vector2 as _BaseVector2
from ._vector import Vector3 as _BaseVector3
from ._vector import Vector4 as _BaseVector4


# В генераторе плагина для клиента есть логика, связанная с проверкой на EnkiType

class Vector2(EnkiType, _BaseVector2):
    pass


class Vector3(EnkiType, _BaseVector3):

    def merge(self, other: Vector3) -> Vector3:
        """Залить экземпляр другого вектора в этот экземпляр.

        От сервера могут прийти события, которые только частично обновляют
        позицию и направление, обновить же свойство можно только целиком.
        Поэтому нужно проверить на невыставленные значения.

        Вектор может быть "частично заполненым", но остаётся валидным.
        Невыставленное значение - это float константа.
        """
        res = Vector3(
            *[s if s is not NoValue.NO_POS_DIR_VALUE else o
              for s, o in zip(self, other)]
        )
        return res


class Position(Vector3):

    def merge(self, other: Position) -> Position:
        vec3 = super().merge(other)
        return Position(*list(vec3))


class Direction(Vector3):

    def merge(self, other: Direction) -> Direction:
        vec3 = super().merge(other)
        return Direction(*list(vec3))

    @property
    def yaw(self) -> float:
        return self.z

    @property
    def pitch(self) -> float:
        return self.y

    @property
    def roll(self) -> float:
        return self.x


class Vector4(EnkiType, _BaseVector4):
    pass


class Array(_BaseArray, EnkiType):
    """Plugin Array."""


class FixedDict(_BaseFixedDict, EnkiType):
    """Plugin FixedDict."""
