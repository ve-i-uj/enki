"""The entity parent class.

Base entity --> bentity .
"""

from __future__ import annotations

from typing import ClassVar

__all__ = ['Entity']

# TODO: [16.07.2021 burov_alexey@mail.ru]:
# Их нужно в какое-то отдельное место (возможно в settings лучше убрать)
NO_ENTITY_CLS_ID = 0
NO_ENTITY_ID = 0


class _CellEntity:
    """Cell component methods of the entity."""
    pass


class _BaseEntity:
    """Base component methods of the entity."""
    pass


class Entity:
    """Base class for all entities."""
    CLS_ID: ClassVar = NO_ENTITY_CLS_ID  # The unique id of the entity class

    def __init__(self, entity_id: int):
        self._id = entity_id

        self._cell = _CellEntity()
        self._base = _BaseEntity()

    @property
    def cell(self) -> _CellEntity:
        return self._cell

    @property
    def base(self) -> _BaseEntity:
        return self._base

    def __update_properties__(self, properties: dict):
        for name, value in properties.items():
            name = f'_{self.__class__.__name__}__{name}'
            setattr(self, name, value)

    def __str__(self):
        return f'{self.__class__.__name__}(id={self._id})'
