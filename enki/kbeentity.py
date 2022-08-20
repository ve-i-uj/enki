"""The entity parent class."""

from __future__ import annotations
import abc
import collections
import io
import logging
from typing import ClassVar, Optional, Type

from enki.interface import IEntity, IEntityMgr, IEntityRemoteCall, IMessage
from enki.misc import devonly

logger = logging.getLogger(__name__)

# TODO: [16.07.2021 burov_alexey@mail.ru]:
# Их нужно в какое-то отдельное место (возможно в settings лучше убрать)
NO_ENTITY_CLS_ID = 0
NO_ENTITY_ID = 0


class EntityMgrError(Exception):
    pass


class _EntityRemoteCall(IEntityRemoteCall):

    def __init__(self, entity: IEntity):
        self._entity = entity

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'


class CellEntityRemoteCall(_EntityRemoteCall):
    """Remote calls to the entity cell component."""
    pass


class BaseEntityRemoteCall(_EntityRemoteCall):
    """Remote calls to the entity base component."""


class Entity(IEntity):
    """Base class for all entities."""
    CLS_ID: ClassVar = NO_ENTITY_CLS_ID  # The unique id of the entity class
    _cls_by_id: dict[int, Entity] = {}
    _implementation_cls = None

    def __init__(self, entity_id: int, entity_mgr: IEntityMgr):
        self._id = entity_id
        self._entity_mgr = entity_mgr

        self._cell = CellEntityRemoteCall(entity=self)
        self._base = BaseEntityRemoteCall(entity=self)

        # It need to call the "set_" callback after the property was updated.
        # The array of property names will be generated in descendants.
        # (distribution flags for "set_" methods: ALL_CLIENTS, OTHER_CLIENTS,
        # OWN_CLIENT).
        self._set_property_names = set()

        self._pending_msgs: list[IMessage] = []

    @staticmethod
    def get_implementation(cls: Entity) -> Optional[Type[Entity]]:
        # TODO: [2022-08-18 12:09 burov_alexey@mail.ru]:
        # Это можно вызывать только у родительских классов
        if cls._implementation_cls is not None:
            return cls._implementation_cls
        descendants = cls.__subclasses__()
        if not descendants:
            return None
        cls._implementation_cls = descendants[-1]
        return cls._implementation_cls

    @property
    def id(self) -> int:
        return self._id

    @property
    def cell(self) -> CellEntityRemoteCall:
        return self._cell

    @property
    def base(self) -> BaseEntityRemoteCall:
        return self._base

    def add_pending_msg(self, msg: IMessage):
        self._pending_msgs.append(msg)

    def get_pending_msgs(self) -> list[IMessage]:
        return self._pending_msgs[:]

    def clean_pending_msgs(self):
        self._pending_msgs[:] = []

    def __update_properties__(self, properties: dict):
        for name, value in properties.items():
            old_value = getattr(self, name)
            setattr(self, f'_{name}', value)

            if name in self._set_property_names:
                set_method = getattr(self, f'set_{name}')
                set_method(old_value)

    def __remote_call__(self, msg: IMessage):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._entity_mgr.remote_call(msg)

    def __on_remote_call__(self, method_name: str, arguments: list) -> None:
        """The callback fires when method has been called on the server."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        method = getattr(self, method_name)
        method(*arguments)

    def __str__(self):
        return f'{self.__class__.__name__}(id={self._id})'
