"""KBE type encoders / decoders."""

from __future__ import annotations


class Vector2(_BaseVector2):
    pass


class Vector3(_BaseVector3):

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
