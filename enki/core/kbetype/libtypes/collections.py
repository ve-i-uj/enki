"""Реализация типов коллекций, используемых в игровой логике KBEngine."""

from __future__ import annotations

import copy
from collections import OrderedDict
from collections.abc import Iterator, MutableMapping, MutableSequence
from typing import Any, Generic, TypeVar

T_ArrayElement = TypeVar("T_ArrayElement")  # pylint: disable=invalid-name


class Array(MutableSequence, Generic[T_ArrayElement]):  # noqa: PLR0904
    """Тип массива данных."""

    def __init__(
        self,
        of: type[T_ArrayElement],
        type_name: str,
        initial_data: list[T_ArrayElement] | None = None,
    ) -> None:
        """Тип данных 'массив'.

        Args:
            of (type): простой не составной python-тип элементов массива
            type_name (str): имя типа
            initial_data (list | None, optional): значения при инициализации.
                Defaults to None.

        Raises:
            TypeError: если значение при инициализации имеет неподходящий тип
                данных.

        """
        self._of = of
        self._type_name = type_name

        initial_data = initial_data or []
        if any(not isinstance(i, of) for i in initial_data):
            msg = (
                f"The initial data has the item with invalid type "
                f"(initial_data = {initial_data}, should be "
                f"the list of '{self._of.__name__}' items)"
            )
            raise TypeError(msg)
        self._data: list[T_ArrayElement] = initial_data[:]

    def __cast(self, other):
        return other._data if isinstance(other, self.__class__) else other

    def __check_item(self, item: T_ArrayElement) -> bool:
        return isinstance(item, self._of)

    def __lt__(self, other):
        return self._data < self.__cast(other)

    def __le__(self, other):
        return self._data <= self.__cast(other)

    def __eq__(self, other):
        return self._data == self.__cast(other)

    def __gt__(self, other):
        return self._data > self.__cast(other)

    def __ge__(self, other):
        return self._data >= self.__cast(other)

    def __contains__(self, item):
        return item in self._data

    def __len__(self):
        return len(self._data)

    def __getitem__(self, i):
        if isinstance(i, slice):
            return self.__class__(self._of, self._type_name, self._data[i])
        return self._data[i]

    def __setitem__(self, i, item):
        if not self.__check_item(item):
            msg = (
                f"The item '{item}' has invalid type (should "
                f"be '{self._of.__name__}')"
            )
            raise TypeError(msg)
        self._data[i] = item

    def __delitem__(self, i):
        del self._data[i]

    def __add__(self, other):
        raise NotImplementedError

    def __radd__(self, other):
        raise NotImplementedError

    def __iadd__(self, other):
        raise NotImplementedError

    def __mul__(self, n):
        return self.__class__(self._of, self._type_name, self._data * n)

    __rmul__ = __mul__

    def __imul__(self, n):
        self._data *= n
        return self

    def __copy__(self):
        inst = self.__class__.__new__(self.__class__)
        inst.__dict__.update(self.__dict__)
        # Create a copy and avoid triggering descriptors
        inst.__dict__["_data"] = self.__dict__["_data"].copy()
        return inst

    def __iter__(self) -> Iterator:
        return iter(self._data)

    def append(self, item):
        if not self.__check_item(item):
            raise TypeError(
                f"The item '{item}' has invalid type (should "
                f"be '{self._of.__name__}')"
            )
        self._data.append(item)

    def insert(self, i, item):
        if not self.__check_item(item):
            raise TypeError(
                f"The item '{item}' has invalid type (should "
                f"be '{self._of.__name__}')"
            )
        self._data.insert(i, item)

    def pop(self, i=-1):
        return self._data.pop(i)

    def remove(self, item):
        self._data.remove(item)

    def clear(self):
        self._data.clear()

    def copy(self):
        return self.__class__(self._of, self._type_name, self._data)

    def count(self, item):
        return self._data.count(item)

    def index(self, item, *args):
        return self._data.index(item, *args)

    def reverse(self):
        self._data.reverse()

    def sort(self, *args, **kwds):
        self._data.sort(*args, **kwds)

    def extend(self, other):
        if isinstance(other, self.__class__):
            if other._of != self._of:
                msg = f"Different types of items ('{self}' and {other}"
                raise TypeError(msg)
            self._data.extend(other._data)
            return

        if isinstance(other, list):
            for item in other:
                if not self.__check_item(item):
                    msg = (
                        f"The item '{item}' has invalid type (should "
                        f"be '{self._of.__name__}')"
                    )
                    raise TypeError(msg)
            self._data.extend(other)
            return

        msg = f"Use list or '{self.__class__.__name__}'"
        raise TypeError(msg)

    def __str__(self) -> str:
        return (
            f"kbetype.Array(of={self._of.__name__}, "
            f"type_name='{self._type_name}', initial_data={self._data})"
        )

    def __repr__(self) -> str:
        return self._data.__repr__()

    def __hash__(self) -> int:
        return hash(str(self))


class FixedDict(MutableMapping):
    """Plugin FixedDict."""

    def __init__(self, type_name: str, initial_data: OrderedDict):
        if not isinstance(initial_data, OrderedDict):
            msg = (
                f"The argument '{initial_data}' is not an instance of 'OrderedDict'"
            )
            raise TypeError(msg)
        # the attribute contains all possible keys
        self._data = OrderedDict()
        self._type_name = type_name

        self._data = copy.deepcopy(initial_data)

    def __check_value(self, key: str, value: Any) -> None:
        if key not in self._data:
            msg = f"The FixedDict instance does NOT contain the key '{key}'"
            raise KeyError(msg)

        should_be_type = type(self._data[key])
        if not isinstance(value, should_be_type):
            msg = (
                f"The value '{value}' of the key '{key}' has invalid type (should "
                f"be '{should_be_type.__name__}')"
            )
            raise KeyError(msg)

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, key: str) -> Any:
        if key not in self._data:
            raise KeyError(key)
        return self._data[key]

    def __setitem__(self, key: str, item: Any) -> None:
        self.__check_value(key, item)
        self._data[key] = item

    def __delitem__(self, key) -> None:
        msg = "You cannot delete a key from the FixedDict type"
        raise TypeError(msg)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._data)

    def __contains__(self, key) -> bool:
        return key in self._data

    def __copy__(self):
        inst = self.__class__.__new__(self.__class__)
        inst.__dict__.update(self.__dict__)
        # Create a copy and avoid triggering descriptors
        inst.__dict__["_data"] = self.__dict__["_data"].copy()
        return inst

    def copy(self):
        return self.__copy__()

    @classmethod
    def fromkeys(cls, iterable, value=None):
        msg = (
            'You cannot use "fromkeys" of the PluginFixedDict type. '
            "This makes no sense."
        )
        raise TypeError(msg)

    # Методы для доступа к атрибутам

    # def __getattr__(self, name: str) -> Any:
    #     if name in self._data:
    #         return self._data[name]
    #     raise AttributeError(f"type object '{self.__class__.__name__}' has "
    #                          f"no attribute '{name}'")

    # def __setattr__(self, name: str, value: Any) -> None:
    #     if '_initialized' in self.__dict__ and self._initialized:
    #         raise AttributeError(f"The attribute '{name}' cannot be added after initialization")
    #     return object.__setattr__(self, name, value)

    def __str__(self) -> str:
        return self._data.__str__()

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(type_name='{self._type_name}', "
            f"initial_data={self._data})"
        )
