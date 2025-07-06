"""Типы данных, полученные из бинарного представления."""

from __future__ import annotations

from .ikbetype import IKBEType


class KBEArray(IKBEType, list):
    """KBEngine-массив из бинарного представления."""


class KBEFixedDict(IKBEType, dict):
    """KBEngine-dict with the fixed [non-deletable] keys."""
