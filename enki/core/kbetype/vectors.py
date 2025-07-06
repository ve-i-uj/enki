"""Реализация типов векторов, используемые в игровой логике KBEngine.

Повторяет API модуля Math из KBEngine.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Iterator


class UnsupportedArgumentTypeError(Exception):
    """Операция используется неподдерживаемый тип."""


class Vector2(Iterable):  # noqa: PLR0904
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
        return (v for v in (self.x, self.y))

    def __add__(self, v: Vector2) -> Vector2:
        return Vector2(self._x + v.x, self._y + v.y)

    def __sub__(self, v: Vector2) -> Vector2:
        return Vector2(self._x - v.x, self._y - v.y)

    def __mul__(self, other: float | Vector2) -> Vector2:
        if isinstance(other, (float, int)):
            return Vector2(self._x * other, self._y * other)

        if isinstance(other, Vector2):
            return Vector2(self._x * other.x, self._y * other.y)

        raise UnsupportedArgumentTypeError

    __rmul__ = __mul__

    def __truediv__(self, value: float) -> Vector2:
        return Vector2(self._x / value, self._y / value)

    def __neg__(self) -> Vector2:
        return Vector2(self._x * -1, self._y * -1)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Vector2):
            return self._x == other.x and self._y == other.y

        raise UnsupportedArgumentTypeError

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self._x}, {self._y})"

    def __hash__(self) -> int:
        return hash(str(self))

    __repr__ = __str__

    @property
    def length(self) -> float:
        """Длина вектора."""
        return math.sqrt(self.lengthSquared)

    @property
    def lengthSquared(self) -> float:
        """Квадрат вектора."""
        return self._x * self._x + self._y * self._y

    def cross2D(self, other: Vector2) -> float:  # noqa: N802 # pylint: disable=invalid-name
        """Return the magnitude of the cross product between two vectors.

        Args:
            other (Vector2): the other vector

        Returns:
            float: the magnitude of the cross product between two vectors

        """
        return self._x * other.y - self._y * other.x

    def distSqrTo(self, other: Vector2) -> float:  # noqa: N802 # pylint: disable=invalid-name
        v = Vector2(self._x - other.x, self._y - other.y)
        return v.lengthSquared

    def distTo(self, other: Vector2) -> float:  # noqa: N802 # pylint: disable=invalid-name
        return math.sqrt(self.distSqrTo(other))

    def scale(self, scale: float):
        return Vector2(self._x * scale, self._y * scale)

    def dot(self, other: Vector2):
        return self._x * other.x + self._y * other.y

    def normalise(self) -> None:
        if self.length == 0:
            return
        length = self.length
        self._x /= length
        self._y /= length

    def list(self) -> list:
        return [self._x, self._y]

    def set(self, value: Vector2 | tuple[float, float] | float):
        if isinstance(value, Vector2):
            self._x = value.x
            self._y = value.y
        elif isinstance(value, tuple):
            assert len(value) == 2
            self._x = value[0]
            self._y = value[1]
        elif isinstance(value, float):
            self._x = value
            self._y = value
        else:
            msg = f'The type "{type(value)}" is unsupported'
            raise UnsupportedArgumentTypeError(msg)

    def tuple(self) -> tuple:
        return self._x, self._y


class Vector3(Iterable):  # noqa: PLR0904
    """Реализация трёхмерного вектора."""

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        """Двумерный вектор.

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
        return (v for v in (self.x, self.y, self.z))

    def __eq__(self, other: object) -> bool:
        if isinstance(object, Vector3):
            return self.x == other.x and self.y == other.y and self.z == other.z

        raise UnsupportedArgumentTypeError

    def __add__(self, v: Vector3) -> Vector3:
        return Vector3(self._x + v.x, self._y + v.y, self._z + v.z)

    def __sub__(self, v: Vector3) -> Vector3:
        return Vector3(self._x - v.x, self._y - v.y, self._z - v.z)

    def __mul__(self, other: float | Vector3) -> Vector3:
        if isinstance(other, (float, int)):
            return Vector3(self._x * other, self._y * other, self._z * other)

        if isinstance(other, Vector3):
            return Vector3(self._x * other.x, self._y * other.y, self._z * other.z)

        raise UnsupportedArgumentTypeError

    def __hash__(self) -> int:
        return hash(str(self))

    __rmul__ = __mul__

    def __truediv__(self, value: float) -> Vector3:
        return Vector3(self._x / value, self._y / value, self._z / value)

    def __neg__(self) -> Vector3:
        return Vector3(self._x * -1, self._y * -1, self._z * -1)

    def cross2D(self, v: Vector3) -> float:  # noqa: N802 # pylint: disable=invalid-name
        """Return the magnitude of the cross product between two Vector3.

        The formula is v1.x * v2.z - v1.z * v2.x
        Parameters: v2  The vector on the right hand side of the cross product.

        Args:
            v (Vector3): _description_

        Returns:
            float: The magnitude of the cross product

        """
        return self._x * v.z - self._z * v.x

    def distSqrTo(self, v: Vector3) -> float:  # noqa: N802 # pylint: disable=invalid-name
        """Return the square of the distance between two vectors.

        This is often used for comparisons between two distances, because
        it saves the computational expense of calculating a square root.

        Args:
            v (Vector3): the vector to calculated the distance to, from this
                vector.

        Returns:
            float: the square of the distance between the two vectors, as
                a float.

        """
        return (self - v).lengthSquared

    def distTo(self, v: Vector3) -> float:  # noqa: N802 # pylint: disable=invalid-name
        """
        This function returns the distance between two vectors.
        Parameters: v  the vector to calculated the distance to, from this vector.

        Returns: the distance between the two vectors, as a float.
        """
        return (self - v).length

    def dot(self, rhs: Vector3) -> float:
        """
        This function performs a dot product between this vector and
        the specified vector, and returns the product as a float. It doesn't
        effect this vector.

        Dot product is defined to be the sum of the products of the individual
        components, ie:

        x*x + y*y + z*z
        Parameters: rhs  The vector to dot this vector with.

        Returns: The float which is the dot product.
        """
        return float(self._x * rhs.x + self._y * rhs.y + self._z * rhs.z)

    def flatDistSqrTo(self, v: Vector3) -> float:
        """
        This function calculates the distance squared between the points in
        the XZ plane. This is often used for comparisons between two distances,
        because it saves the computational expense of calculating a square root.

        Parameters: v  the vector to calculated the distance to, from this vector.

        Returns: the distance squared between the two vectors, as a float.
        """
        x = self._x - v.x
        z = self._z - v.z
        return x * x + z * z

    def flatDistTo(self, v: Vector3) -> float:
        """
        This function calculates the distance between the points in the XZ plane.

        Parameters: v  the vector to calculated the distance to, from this vector.

        Returns: the distance between the two vectors, as a float.
        """
        x = self._x - v.x
        z = self._z - v.z
        return math.sqrt(x * x + z * z)

    def list(self):
        """
        This function returns the vector converted to a list of 3 elements.
        Returns: The list representation of the vector.
        """
        return [self._x, self._y, self._z]

    def normalise(self) -> None:
        """Normalise this vector (scales it so that its length is exactly 1)."""
        if self.length == 0:
            return
        length = self.length
        self._x /= length
        self._y /= length
        self._z /= length

    def scale(self, s: float) -> Vector3:
        """
        Returns the value of this vector, mutiplied by a scalar, leaving this
        vector unaffected.

        Parameters: s  the scalar to multiply by.

        Returns: returns the _BaseVector3 product of the scalar with the vector.
        """
        return self * s

    def set(self, value: Vector3 | tuple[float, float, float] | float):
        """Set the value of a Vector3 to the specified value.

        It can take several different styles of argument:

        - It can take a _BaseVector3, which sets this vector equal to the argument.
        - It can take a tuple, with the same size as the vector, assigning the
            first element to x, the second to y and the third to z.
        - It can take a floating point number, which will be assigned to all
            components of the vector.

        Args:
            value (Vector3 | tuple[float, float, float] | float): значение,
                которое будет у вектора

        Raises:
            UnsupportedArgumentTypeError: аргумент имеет неподдерживаемый тип

        """
        if isinstance(value, Vector3):
            self._x = value.x
            self._y = value.y
            self._z = value.z
        elif isinstance(value, tuple):
            assert len(value) == 3
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
        """Return the vector converted to a tuple of 3 elements.

        Returns:
            tuple[float, float, float]: the vector converted to a tuple of
                3 elements

        """
        return (self._x, self._y, self._z)

    @property
    def length(self) -> float:
        return float(
            math.sqrt(self._x * self._x + self._y * self._y + self._z * self._z)
        )

    @property
    def lengthSquared(self) -> float:
        return float(self._x * self._x + self._y * self._y + self._z * self._z)

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}({', '.join(str(round(v, 2)) for v in self)})"
        )

    __repr__ = __str__


class Vector4(Iterable):  # noqa: PLR0904
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
        return (v for v in (self.x, self.y, self.z, self.w))

    def __add__(self, v: Vector4) -> Vector4:
        return Vector4(self._x + v.x, self._y + v.y, self._z + v.z, self._w + v.w)

    def __sub__(self, v: Vector4) -> Vector4:
        return Vector4(self._x - v.x, self._y - v.y, self._z - v.z, self._w - v.w)

    def __mul__(self, other: float | Vector4) -> Vector4:
        if isinstance(other, (float, int)):
            return Vector4(
                self._x * other, self._y * other, self._z * other, self._w * other
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
        return hash(str(self))

    __rmul__ = __mul__

    def __truediv__(self, value: float) -> Vector4:
        return Vector4(
            self._x / value, self._y / value, self._z / value, self._w / value
        )

    def __neg__(self) -> Vector4:
        return Vector4(self._x * -1, self._y * -1, self._z * -1, self._w * -1)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Vector4):
            return (
                self._x == other.x
                and self._y == other.y
                and self._z == other.z
                and self._w == other.w
            )

        raise UnsupportedArgumentTypeError

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}({self._x}, {self._y}, {self._z}, {self._w})"
        )

    __repr__ = __str__

    @property
    def length(self) -> float:
        return math.sqrt(self.lengthSquared)

    @property
    def lengthSquared(self) -> float:
        return (
            self._x * self._x
            + self._y * self._y
            + self._z * self._z
            + self._w * self._w
        )

    def distTo(self, other: Vector4) -> float:
        return math.sqrt(self.distSqrTo(other))

    def distSqrTo(self, other: Vector4) -> float:
        v = Vector4(
            self._x - other.x,
            self._y - other.y,
            self._z - other.z,
            self._w - other.w,
        )
        return v.lengthSquared

    def scale(self, scale: float) -> Vector4:
        return self * scale

    def dot(self, other: Vector4) -> float:
        return (
            self._x * other.x
            + self._y * other.y
            + self._z * other.z
            + self._w * other.w
        )

    def normalise(self) -> None:
        if self.length == 0:
            return
        length = self.length
        self._x /= length
        self._y /= length
        self._z /= length
        self._w /= length

    def list(self) -> list:
        return [self._x, self._y, self._z, self._w]

    def set(self, value: Vector4 | tuple[float, float, float, float] | float):
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

    def tuple(self) -> tuple:
        return self._x, self._y, self._z, self._w
