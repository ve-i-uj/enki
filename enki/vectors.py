"""Реализация типов векторов, используемые в игровой логике KBEngine.

Повторяет API модуля Math из KBEngine.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Iterator


class UnsupportedArgumentTypeError(Exception):
    """Операция использует неподдерживаемый тип."""


class Vector2(Iterable):
    """Реализация типа двумерного вектора."""

    def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
        """Двумерный вектор.

        Args:
            x (float, optional): Значение по оси 'x'. Defaults to 0.0.
            y (float, optional): Значение по оси 'y'. Defaults to 0.0.

        """
        self._x = x
        self._y = y

    @property
    def x(self) -> float:
        """Значение по оси 'x'."""
        return self._x

    @x.setter
    def x(self, value: float) -> None:
        self._x = value

    @property
    def y(self) -> float:
        """Значение по оси 'y'."""
        return self._y

    @y.setter
    def y(self, value: float) -> None:
        self._y = value

    def __iter__(self) -> Iterator[float]:
        """Возвращает итератор по компонентам вектора."""
        return (v for v in (self.x, self.y))

    def __add__(self, v: Vector2) -> Vector2:
        """Сложение двух векторов."""
        return Vector2(self._x + v.x, self._y + v.y)

    def __sub__(self, v: Vector2) -> Vector2:
        """Вычитание векторов."""
        return Vector2(self._x - v.x, self._y - v.y)

    def __mul__(self, other: float | Vector2) -> Vector2:
        """Умножение вектора на число или другой вектор."""
        if isinstance(other, (float, int)):
            return Vector2(self._x * other, self._y * other)

        if isinstance(other, Vector2):
            return Vector2(self._x * other.x, self._y * other.y)

        raise UnsupportedArgumentTypeError

    __rmul__ = __mul__

    def __truediv__(self, value: float) -> Vector2:
        """Деление вектора на число."""
        return Vector2(self._x / value, self._y / value)

    def __neg__(self) -> Vector2:
        """Отрицание вектора."""
        return Vector2(self._x * -1, self._y * -1)

    def __eq__(self, other: object) -> bool:
        """Проверка на равенство двух векторов."""
        if isinstance(other, Vector2):
            return self._x == other.x and self._y == other.y

        raise UnsupportedArgumentTypeError

    def __str__(self) -> str:
        """Строковое представление вектора."""
        return f"{self.__class__.__name__}({self._x}, {self._y})"

    def __hash__(self) -> int:
        """Хэш вектора."""
        return hash(str(self))

    __repr__ = __str__

    @property
    def length(self) -> float:
        """Длина вектора."""
        return math.sqrt(self.lengthSquared)

    @property
    def lengthSquared(self) -> float:  # noqa: N802
        """Квадрат длины вектора."""
        return self._x * self._x + self._y * self._y

    def cross2D(
        self, other: Vector2
    ) -> float:  # pylint: disable=invalid-name
        """Возвращает величину векторного произведения между двумя векторами.

        Args:
            other (Vector2): другой вектор

        Returns:
            float: величина векторного произведения между двумя векторами

        """
        return self._x * other.y - self._y * other.x

    def distSqrTo(
        self, other: Vector2
    ) -> float:  # pylint: disable=invalid-name
        """Квадрат расстояния до другого вектора.

        Args:
            other (Vector2): другой вектор

        Returns:
            float: квадрат расстояния

        """
        v = Vector2(self._x - other.x, self._y - other.y)
        return v.lengthSquared

    def distTo(
        self, other: Vector2
    ) -> float:  # pylint: disable=invalid-name
        """Расстояние до другого вектора.

        Args:
            other (Vector2): другой вектор

        Returns:
            float: расстояние

        """
        return math.sqrt(self.distSqrTo(other))

    def scale(self, scale: float) -> Vector2:
        """Масштабирование вектора.

        Args:
            scale (float): коэффициент масштабирования

        Returns:
            Vector2: новый масштабированный вектор

        """
        return Vector2(self._x * scale, self._y * scale)

    def dot(self, other: Vector2) -> float:
        """Скалярное произведение двух векторов.

        Args:
            other (Vector2): другой вектор

        Returns:
            float: результат скалярного произведения

        """
        return self._x * other.x + self._y * other.y

    def normalise(self) -> None:
        """Нормализация вектора (приведение к длине 1)."""
        if self.length == 0:
            return
        length = self.length
        self._x /= length
        self._y /= length

    def list(self) -> list[float]:
        """Представление вектора в виде списка.

        Returns:
            list[float]: список компонентов вектора

        """
        return [self._x, self._y]

    def set(self, value: Vector2 | tuple[float, float] | float) -> None:
        """Установка значений вектора.

        Args:
            value: новое значение (вектор, кортеж или число)

        Raises:
            UnsupportedArgumentTypeError: неподдерживаемый тип аргумента

        """
        if isinstance(value, Vector2):
            self._x = value.x
            self._y = value.y
        elif isinstance(value, tuple):
            assert len(value) == 2  # noqa: PLR2004
            self._x = value[0]
            self._y = value[1]
        elif isinstance(value, float):
            self._x = value
            self._y = value
        else:
            msg = f'The type "{type(value)}" is unsupported'
            raise UnsupportedArgumentTypeError(msg)

    def tuple(self) -> tuple[float, float]:
        """Представление вектора в виде кортежа.

        Returns:
            tuple[float, float]: кортеж компонентов вектора

        """
        return self._x, self._y


class Vector3(Iterable):
    """Реализация трёхмерного вектора."""

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        """Трёхмерный вектор.

        Args:
            x (float, optional): значение x. Defaults to 0.0.
            y (float, optional): значение y. Defaults to 0.0.
            z (float, optional): значение z. Defaults to 0.0.

        """
        self._x = x
        self._y = y
        self._z = z

    @property
    def x(self) -> float:
        """Значение x."""
        return self._x

    @x.setter
    def x(self, value: float) -> None:
        self._x = value

    @property
    def y(self) -> float:
        """Значение y."""
        return self._y

    @y.setter
    def y(self, value: float) -> None:
        self._y = value

    @property
    def z(self) -> float:
        """Значение z."""
        return self._z

    @z.setter
    def z(self, value: float) -> None:
        self._z = value

    def clone(self) -> Vector3:
        """Создать копию вектора.

        Returns:
            Vector3: новый вектор

        """
        return self.__class__(self.x, self.y, self.z)

    def __iter__(self) -> Iterator[float]:
        """Возвращает итератор по компонентам вектора."""
        return (v for v in (self.x, self.y, self.z))

    def __eq__(self, other: object) -> bool:
        """Проверка на равенство двух векторов."""
        if isinstance(other, Vector3):
            return self.x == other.x and self.y == other.y and self.z == other.z

        raise UnsupportedArgumentTypeError

    def __add__(self, v: Vector3) -> Vector3:
        """Сложение двух векторов."""
        return Vector3(self._x + v.x, self._y + v.y, self._z + v.z)

    def __sub__(self, v: Vector3) -> Vector3:
        """Вычитание векторов."""
        return Vector3(self._x - v.x, self._y - v.y, self._z - v.z)

    def __mul__(self, other: float | Vector3) -> Vector3:
        """Умножение вектора на число или другой вектор."""
        if isinstance(other, (float, int)):
            return Vector3(self._x * other, self._y * other, self._z * other)

        if isinstance(other, Vector3):
            return Vector3(
                self._x * other.x, self._y * other.y, self._z * other.z
            )

        raise UnsupportedArgumentTypeError

    def __hash__(self) -> int:
        """Хэш вектора."""
        return hash(str(self))

    __rmul__ = __mul__

    def __truediv__(self, value: float) -> Vector3:
        """Деление вектора на число."""
        return Vector3(self._x / value, self._y / value, self._z / value)

    def __neg__(self) -> Vector3:
        """Отрицание вектора."""
        return Vector3(self._x * -1, self._y * -1, self._z * -1)

    def cross2D(
        self, v: Vector3
    ) -> float:  # pylint: disable=invalid-name
        """Возвращает величину векторного произведения между двумя Vector3.

        Формула: v1.x * v2.z - v1.z * v2.x

        Args:
            v (Vector3): вектор для правой части векторного произведения

        Returns:
            float: величина векторного произведения


        """
        return self._x * v.z - self._z * v.x

    def distSqrTo(
        self, v: Vector3
    ) -> float:  # pylint: disable=invalid-name
        """Возвращает квадрат расстояния между двумя векторами.

        Часто используется для сравнения расстояний, так как позволяет
        избежать вычислительных затрат на вычисление квадратного корня.

        Args:
            v (Vector3): вектор, до которого вычисляется расстояние

        Returns:
            float: квадрат расстояния между векторами


        """
        return (self - v).lengthSquared

    def distTo(
        self, v: Vector3
    ) -> float:  # pylint: disable=invalid-name
        """Возвращает расстояние между двумя векторами.

        Args:
            v (Vector3): вектор, до которого вычисляется расстояние

        Returns:
            float: расстояние между векторами

        """
        return (self - v).length

    def dot(self, rhs: Vector3) -> float:
        """Скалярное произведение этого вектора с указанным вектором.

        Args:
            rhs (Vector3): вектор для скалярного произведения

        Returns:
            float: результат скалярного произведения

        """
        return float(self._x * rhs.x + self._y * rhs.y + self._z * rhs.z)

    def flatDistSqrTo(self, v: Vector3) -> float:  # noqa: N802
        """Вычисляет квадрат расстояния между точками в плоскости XZ.

        Args:
            v (Vector3): вектор, до которого вычисляется расстояние

        Returns:
            float: квадрат расстояния в плоскости XZ

        """
        x = self._x - v.x
        z = self._z - v.z
        return x * x + z * z

    def flatDistTo(self, v: Vector3) -> float:  # noqa: N802
        """Вычисляет расстояние между точками в плоскости XZ.

        Args:
            v (Vector3): вектор, до которого вычисляется расстояние

        Returns:
            float: расстояние в плоскости XZ

        """
        x = self._x - v.x
        z = self._z - v.z
        return math.sqrt(x * x + z * z)

    def list(self) -> list[float]:
        """Возвращает вектор в виде списка из 3 элементов.

        Returns:
            list[float]: список компонентов вектора

        """
        return [self._x, self._y, self._z]

    def normalise(self) -> None:
        """Нормализация вектора (приведение к длине 1)."""
        if self.length == 0:
            return
        length = self.length
        self._x /= length
        self._y /= length
        self._z /= length

    def scale(self, s: float) -> Vector3:
        """Масштабирование вектора.

        Args:
            s (float): коэффициент масштабирования

        Returns:
            Vector3: новый масштабированный вектор

        """
        return self * s

    def set(self, value: Vector3 | tuple[float, float, float] | float) -> None:
        """Установка значений вектора.

        Args:
            value: новое значение (вектор, кортеж или число)

        Raises:
            UnsupportedArgumentTypeError: неподдерживаемый тип аргумента

        """
        if isinstance(value, Vector3):
            self._x = value.x
            self._y = value.y
            self._z = value.z
        elif isinstance(value, tuple):
            assert len(value) == 3  # noqa: PLR2004
            self._x = value[0]
            self._y = value[1]
            self._z = value[2]
        elif isinstance(value, float):
            self._x = value
            self._y = value
            self._z = value
        else:
            msg = f'The type "{type(value)}" is unsupported'
            raise UnsupportedArgumentTypeError(msg)

    def tuple(self) -> tuple[float, float, float]:
        """Возвращает вектор в виде кортежа из 3 элементов.

        Returns:
            tuple[float, float, float]: кортеж компонентов вектора

        """
        return (self._x, self._y, self._z)

    @property
    def length(self) -> float:
        """Длина вектора."""
        return float(
            math.sqrt(self._x * self._x + self._y * self._y + self._z * self._z)
        )

    @property
    def lengthSquared(self) -> float:  # noqa: N802
        """Квадрат длины вектора."""
        return float(self._x * self._x + self._y * self._y + self._z * self._z)

    def __str__(self) -> str:
        """Строковое представление вектора."""
        return f"{self.__class__.__name__}({', '.join(str(round(v, 2)) for v in self)})"  # noqa: E501

    __repr__ = __str__


class Vector4(Iterable):
    """Реализация четырёхмерного вектора."""

    def __init__(
        self, x: float = 0.0, y: float = 0.0, z: float = 0.0, w: float = 0.0
    ) -> None:
        """Четырёхмерный вектор.

        Args:
            x (float, optional): значение x. Defaults to 0.0.
            y (float, optional): значение y. Defaults to 0.0.
            z (float, optional): значение z. Defaults to 0.0.
            w (float, optional): значение w. Defaults to 0.0.

        """
        self._x = x
        self._y = y
        self._z = z
        self._w = w

    @property
    def x(self) -> float:
        """Значение x."""
        return self._x

    @x.setter
    def x(self, value: float) -> None:
        self._x = value

    @property
    def y(self) -> float:
        """Значение y."""
        return self._y

    @y.setter
    def y(self, value: float) -> None:
        self._y = value

    @property
    def z(self) -> float:
        """Значение z."""
        return self._z

    @z.setter
    def z(self, value: float) -> None:
        self._z = value

    @property
    def w(self) -> float:
        """Значение w."""
        return self._w

    @w.setter
    def w(self, value: float) -> None:
        self._w = value

    def __iter__(self) -> Iterator[float]:
        """Возвращает итератор по компонентам вектора."""
        return (v for v in (self.x, self.y, self.z, self.w))

    def __add__(self, v: Vector4) -> Vector4:
        """Сложение двух векторов."""
        return Vector4(
            self._x + v.x, self._y + v.y, self._z + v.z, self._w + v.w
        )

    def __sub__(self, v: Vector4) -> Vector4:
        """Вычитание векторов."""
        return Vector4(
            self._x - v.x, self._y - v.y, self._z - v.z, self._w - v.w
        )

    def __mul__(self, other: float | Vector4) -> Vector4:
        """Умножение вектора на число или другой вектор."""
        if isinstance(other, (float, int)):
            return Vector4(
                self._x * other,
                self._y * other,
                self._z * other,
                self._w * other,
            )

        if isinstance(other, Vector4):
            return Vector4(
                self._x * other.x,
                self._y * other.y,
                self._z * other.z,
                self._w * other.w,
            )

        raise UnsupportedArgumentTypeError

    def __hash__(self) -> int:
        """Хэш вектора."""
        return hash(str(self))

    __rmul__ = __mul__

    def __truediv__(self, value: float) -> Vector4:
        """Деление вектора на число."""
        return Vector4(
            self._x / value, self._y / value, self._z / value, self._w / value
        )

    def __neg__(self) -> Vector4:
        """Отрицание вектора."""
        return Vector4(self._x * -1, self._y * -1, self._z * -1, self._w * -1)

    def __eq__(self, other: object) -> bool:
        """Проверка на равенство двух векторов."""
        if isinstance(other, Vector4):
            return (
                self._x == other.x
                and self._y == other.y
                and self._z == other.z
                and self._w == other.w
            )

        raise UnsupportedArgumentTypeError

    def __str__(self) -> str:
        """Строковое представление вектора."""
        return f"{self.__class__.__name__}({self._x}, {self._y}, {self._z}, {self._w})"  # noqa: E501

    __repr__ = __str__

    @property
    def length(self) -> float:
        """Длина вектора."""
        return math.sqrt(self.lengthSquared)

    @property
    def lengthSquared(self) -> float:  # noqa: N802
        """Квадрат длины вектора."""
        return (
            self._x * self._x
            + self._y * self._y
            + self._z * self._z
            + self._w * self._w
        )

    def distTo(self, other: Vector4) -> float:  # noqa: N802
        """Расстояние до другого вектора.

        Args:
            other (Vector4): другой вектор

        Returns:
            float: расстояние

        """
        return math.sqrt(self.distSqrTo(other))

    def distSqrTo(self, other: Vector4) -> float:  # noqa: N802
        """Квадрат расстояния до другого вектора.

        Args:
            other (Vector4): другой вектор

        Returns:
            float: квадрат расстояния

        """
        v = Vector4(
            self._x - other.x,
            self._y - other.y,
            self._z - other.z,
            self._w - other.w,
        )
        return v.lengthSquared

    def scale(self, scale: float) -> Vector4:
        """Масштабирование вектора.

        Args:
            scale (float): коэффициент масштабирования

        Returns:
            Vector4: новый масштабированный вектор

        """
        return self * scale

    def dot(self, other: Vector4) -> float:
        """Скалярное произведение двух векторов.

        Args:
            other (Vector4): другой вектор

        Returns:
            float: результат скалярного произведения

        """
        return (
            self._x * other.x
            + self._y * other.y
            + self._z * other.z
            + self._w * other.w
        )

    def normalise(self) -> None:
        """Нормализация вектора (приведение к длине 1)."""
        if self.length == 0:
            return
        length = self.length
        self._x /= length
        self._y /= length
        self._z /= length
        self._w /= length

    def list(self) -> list[float]:
        """Представление вектора в виде списка.

        Returns:
            list[float]: список компонентов вектора

        """
        return [self._x, self._y, self._z, self._w]

    def set(
        self, value: Vector4 | tuple[float, float, float, float] | float
    ) -> None:
        """Установка значений вектора.

        Args:
            value: новое значение (вектор, кортеж или число)

        Raises:
            UnsupportedArgumentTypeError: неподдерживаемый тип аргумента

        """
        if isinstance(value, Vector4):
            self._x = value.x
            self._y = value.y
            self._z = value.z
            self._w = value.w
        elif isinstance(value, tuple):
            assert len(value) == 4
            self._x = value[0]
            self._y = value[1]
            self._z = value[2]
            self._w = value[3]
        elif isinstance(value, float):
            self._x = value
            self._y = value
            self._z = value
            self._w = value
        else:
            msg = f'The type "{type(value)}" is unsupported'
            raise UnsupportedArgumentTypeError(msg)

    def tuple(self) -> tuple[float, float, float, float]:
        """Представление вектора в виде кортежа.

        Returns:
            tuple[float, float, float, float]: кортеж компонентов вектора

        """
        return self._x, self._y, self._z, self._w


class Position(Vector3):
    pass


class Direction(Vector3):
    """Класс направления, наследуемый от Vector3."""

    @property
    def yaw(self) -> float:
        """Угол рыскания (поворот вокруг вертикальной оси)."""
        return self.z

    @property
    def pitch(self) -> float:
        """Угол тангажа (наклон вверх/вниз)."""
        return self.y

    @property
    def roll(self) -> float:
        """Угол крена (наклон влево/вправо)."""
        return self.x
