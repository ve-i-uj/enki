"""Типы данных, полученные из бинарного представления."""

from __future__ import annotations

from dataclasses import dataclass
import dataclasses
from typing import Any, Generic, Self, TypeVar

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
