"""Типы коллекции, которые KBEngine добавляет в скрипты."""


from collections import OrderedDict
import collections.abc
import copy
from typing import Any, Iterable, Optional, Type


class Array(collections.abc.MutableSequence):
    """Plugin Array."""

    def __init__(self, of: Type, type_name: str,
                 initial_data: Optional[list] = None):
        self._of: Type = of
        self._type_name = type_name
        initial_data = initial_data or []
        if any(not isinstance(i, of) for i in initial_data):  # type: ignore
            raise TypeError(f'The initial data has the item with invalid type '
                            f'(initial_data = {initial_data}, should be '
                            f'the list of "{self._of.__name__}" items)')
        self._data: list = initial_data[:]

    def __cast(self, other):
        return other._data if isinstance(other, self.__class__) else other

    def __check_item(self, item: Any) -> bool:
        if not isinstance(item, self._of):  # type: ignore
            return False
        return True

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
            raise TypeError(f'The item "{item}" has invalid type (should '
                            f'be "{self._of.__name__}")')
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
        inst.__dict__['_data'] = self.__dict__['_data'].copy()
        return inst

    def __iter__(self) -> Iterable:
        return iter(self._data)

    def append(self, item):
        if not self.__check_item(item):
            raise TypeError(f'The item "{item}" has invalid type (should '
                            f'be "{self._of.__name__}")')
        self._data.append(item)

    def insert(self, i, item):
        if not self.__check_item(item):
            raise TypeError(f'The item "{item}" has invalid type (should '
                            f'be "{self._of.__name__}")')
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
                raise TypeError(f'Different types of items ("{self}" and {other}')
            self._data.extend(other._data)
            return

        if isinstance(other, list):
            for item in other:
                if not self.__check_item(item):
                    raise TypeError(
                        f'The item "{item}" has invalid type (should '
                        f'be "{self._of.__name__}")')
            self._data.extend(other)
            return
        raise TypeError(f'Use list or "{self.__class__.__name__}"')

    def __str__(self):
        return f"kbetype.Array(of={self._of.__name__}, " \
               f"type_name='{self._type_name}', initial_data={self._data})"

    def __repr__(self):
        return self._data.__repr__()


class FixedDict(collections.abc.MutableMapping):
    """Plugin FixedDict."""

    def __init__(self, type_name: str, initial_data: OrderedDict):
        if not isinstance(initial_data, OrderedDict):
            raise TypeError(f'The argument "{initial_data}" is not an instance '
                            f'of "OrderedDict"')
        # the attribute contains all possible keys
        self._data = OrderedDict()
        self._type_name = type_name

        self._data = copy.deepcopy(initial_data)

    def __check_value(self, key: str, value: Any):
        if key not in self._data:
            raise KeyError(f'The FixedDict instance does NOT contain the key "{key}"')
        should_be_type = type(self._data[key])
        if not isinstance(value, should_be_type):
            raise KeyError(f'The value "{value}" of the key "{key}" has invalid type (should '
                           f'be "{should_be_type.__name__}")')

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
        raise TypeError('You cannot delete a key from the FixedDict type')

    def __iter__(self) -> Iterable:
        return iter(self._data)

    def __contains__(self, key) -> bool:
        return key in self._data

    def __copy__(self):
        inst = self.__class__.__new__(self.__class__)
        inst.__dict__.update(self.__dict__)
        # Create a copy and avoid triggering descriptors
        inst.__dict__['_data'] = self.__dict__['_data'].copy()
        return inst

    def copy(self):
        return self.__copy__()

    @classmethod
    def fromkeys(cls, iterable, value=None):
        raise TypeError('You cannot use "fromkeys" of the PluginFixedDict type. '
                        'This makes no sense.')

    # Методы для доступа к атрибутам

    # def __getattr__(self, name: str) -> Any:
    #     if name in self._data:
    #         return self._data[name]
    #     raise AttributeError(f"type object '{self.__class__.__name__}' has "
    #                          f"no attribute '{name}'")

    # def __setattr__(self, name: str, value: Any) -> None:
    #     if '_initialized' in self.__dict__ and self._initialized:
    #         raise AttributeError(f'The attribute "{name}" cannot be added after initialization')
    #     return object.__setattr__(self, name, value)

    def __str__(self):
        return self._data.__str__()

    def __repr__(self):
        return f"{self.__class__.__name__}(type_name='{self._type_name}', " \
               f"initial_data={self._data})"
