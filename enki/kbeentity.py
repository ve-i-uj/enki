"""The entity parent class."""

from __future__ import annotations
import abc
import io
import logging
from typing import ClassVar

from enki import kbeclient
from enki.misc import devonly

logger = logging.getLogger(__name__)

# TODO: [16.07.2021 burov_alexey@mail.ru]:
# Их нужно в какое-то отдельное место (возможно в settings лучше убрать)
NO_ENTITY_CLS_ID = 0
NO_ENTITY_ID = 0


class EntityMgrError(Exception):
    pass


class IEntityMgr(abc.ABC):
    """Entity manager interface."""

    @abc.abstractmethod
    def get_entity(self, entity_id: int) -> Entity:
        """Get entity by id."""
        pass

    @abc.abstractmethod
    def remote_call(self, msg: kbeclient.Message) -> None:
        """Send remote call message."""
        pass


class _EntityRemoteCall:
    """Entity method remote call."""

    def __init__(self, entity: Entity):
        self._entity = entity


class CellEntityRemoteCall(_EntityRemoteCall):
    """Remote calls to the entity cell component."""
    pass


class BaseEntityRemoteCall(_EntityRemoteCall):
    """Remote calls to the entity base component."""
    pass


class Entity:
    """Base class for all entities."""
    CLS_ID: ClassVar = NO_ENTITY_CLS_ID  # The unique id of the entity class

    def __init__(self, entity_id: int, entity_mgr: IEntityMgr):
        self._id = entity_id
        self._entity_mgr = entity_mgr

        self._cell = CellEntityRemoteCall(entity=self)
        self._base = BaseEntityRemoteCall(entity=self)

    @property
    def id(self) -> int:
        return self._id

    @property
    def cell(self) -> CellEntityRemoteCall:
        return self._cell

    @property
    def base(self) -> BaseEntityRemoteCall:
        return self._base

    def __update_properties__(self, properties: dict):
        for name, value in properties.items():
            name = f'_{self.__class__.__name__}__{name}'
            setattr(self, name, value)

    def __remote_call__(self, msg: kbeclient.Message):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._entity_mgr.remote_call(msg)

    def __on_remote_call__(self, method_name: str, arguments: list) -> None:
        """The callback fires when method has been called on the server."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        method = getattr(self, method_name)
        method(*arguments)

    def __str__(self):
        return f'{self.__class__.__name__}(id={self._id})'

