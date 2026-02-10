"""Типы данных, полученные из бинарного представления."""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Generic, TypeVar

from enki.kbetype.ikbetype import IKBEType

_T = TypeVar("_T", bound=IKBEType)  # Array Element Type


class KBEArray(IKBEType, list[_T], Generic[_T]):
    """KBEngine-массив из бинарного представления."""


# Наследовать вместе TypedDict и IKBEType нельзя, т.к. IKBEType не подкласс
# TypedDict. Но игнорировать это предупреждение - это самый простой способ
# описать типы ключей. Можно ещё написать свой класс словаря с типизированными
# полями - но это долго.
@dataclass
class KBEFixedDict(IKBEType):  # type: ignore
    """KBEngine FixedDict из бинарного представления."""

    def get_ordered_items(self) -> tuple[tuple[str, IKBEType], ...]:
        return tuple(
            (f.name, getattr(self, f.name)) for f in dataclasses.fields(self)
        )
