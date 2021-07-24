"""The entity parent class.

Base entity --> kbeentity .
"""

from __future__ import annotations
import io
from typing import ClassVar

from enki import kbeclient

# TODO: [16.07.2021 burov_alexey@mail.ru]:
# Их нужно в какое-то отдельное место (возможно в settings лучше убрать)
NO_ENTITY_CLS_ID = 0
NO_ENTITY_ID = 0


# TODO: [20.07.2021 burov_alexey@mail.ru]:
# Здесь возможно нужны интерфейсы между сущностью и удалёнными вызовами.
# Или вынести в интерфесы и сущность, и удалённые вызовы. Потому что здесь
# лишние импорты появляются.
class _EntityCall:
    
    def __init__(self, entity: Entity):
        self._entity = entity


class CellEntityCall(_EntityCall):
    """Remote calls to the entity cell component."""
    pass


class BaseEntityCall(_EntityCall):
    """Remote calls to the entity base component."""
    pass


class Entity:
    """Base class for all entities."""
    CLS_ID: ClassVar = NO_ENTITY_CLS_ID  # The unique id of the entity class

    def __init__(self, entity_id: int):
        self._id = entity_id

        self._cell = CellEntityCall(entity=self)
        self._base = BaseEntityCall(entity=self)

    @property
    def cell(self) -> CellEntityCall:
        return self._cell

    @property
    def base(self) -> BaseEntityCall:
        return self._base

    def __update_properties__(self, properties: dict):
        for name, value in properties.items():
            name = f'_{self.__class__.__name__}__{name}'
            setattr(self, name, value)

    def __cell_remote_call__(self, method_id: int, buffer: io.BytesIO):
        pass

    def __base_remote_call__(self, buffer: io.BytesIO):
        pass

    def __str__(self):
        return f'{self.__class__.__name__}(id={self._id})'


class NotInitializedEntity(Entity):

    def __init__(self, entity_id: int):
        super().__init__(entity_id)
        self._not_handled_messages: list[kbeclient.Message] = []

    def add_not_handled_message(self, msg: kbeclient.Message) -> None:
        self._not_handled_messages.append(msg)

    def get_not_handled_messages(self) -> list[kbeclient.Message]:
        return self._not_handled_messages[:]


class EntityMgrError(Exception):
    pass


class IEntityMgr:
    """Entity manager interface."""
