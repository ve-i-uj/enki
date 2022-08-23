"""The entity parent class."""

from __future__ import annotations

import logging
import weakref
from typing import Callable, ClassVar, Optional, Type, Any
from weakref import ProxyType

from enki import descr, settings, kbetype
from enki.interface import IEntity, IEntityMgr, IEntityRemoteCall, IMessage, \
    IKBEClientEntity, IKBEClientEntityComponent
from enki.misc import devonly

logger = logging.getLogger(__name__)


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


class EntityComponentRemoteCall(_EntityRemoteCall):
    """Remote calls to the server entity component."""


class Entity(IEntity):
    """Base class for all entities."""
    CLS_ID: ClassVar = settings.NO_ENTITY_CLS_ID  # The unique id of the entity class
    _cls_by_id: dict[int, Entity] = {}
    _implementation_cls = None

    def __init__(self, entity_id: int, entity_mgr: IEntityMgr):
        self._id = entity_id
        self._entity_mgr = entity_mgr

        self._cell = CellEntityRemoteCall(entity=self)
        self._base = BaseEntityRemoteCall(entity=self)

        self._pending_msgs: list[IMessage] = []

        self._isOnGround: bool = False

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
            old_value = getattr(self, f'_{name}')
            if isinstance(old_value, EntityComponent):
                value: kbetype.EntityComponentData
                old_value.__update_properties__(value.properties)
                return

            setattr(self, f'_{name}', value)

            set_method = getattr(self, f'set_{name}', None)
            if set_method is not None:
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

    @property
    def direction(self) -> kbetype.Vector3Data:
        raise NotImplementedError

    @property
    def position(self) -> kbetype.Vector3Data:
        raise NotImplementedError

    @property
    def spaceID(self) -> int:
        raise NotImplementedError

    @property
    def isDestroyed(self) -> bool:
        raise NotImplementedError

    @property
    def isOnGround(self) -> bool:
        return self._isOnGround

    @property
    def inWorld(self) -> bool:
        raise NotImplementedError

    def className(self) -> str:
        return self.__class__.__name__

    def baseCall(self, methodName: str, methodArgs: list[Any]) -> None:
        method: Optional[Callable] = getattr(self._base, methodName, None)
        if method is None:
            logger.warning(f'There is no method "{methodName}"')
            return

        method(*methodArgs)

    def cellCall(self, methodName: str, methodArgs: list[Any]) -> None:
        method: Optional[Callable] = getattr(self._cell, methodName, None)
        if method is None:
            logger.warning(f'There is no method "{methodName}"')
            return

        method(*methodArgs)

    def isPlayer(self) -> bool:
        raise NotImplementedError

    def getComponent(self, componentName: str, all: bool):
        raise NotImplementedError

    def fireEvent(self, eventName: str, *args):
        raise NotImplementedError

    def registerEvent(self, eventName: str, callback: Callable):
        raise NotImplementedError

    def deregisterEvent(self, eventName: str, callback: Callable):
        raise NotImplementedError

    def onDestroy(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())

    def onEnterWorld(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())

    def onLeaveWorld(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())

    def onEnterSpace(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())

    def onLeaveSpace(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())


class EntityComponent(_EntityRemoteCall, IKBEClientEntityComponent):

    def __init__(self, entity: IEntity, own_attr_id: int):
        # TODO: [2022-08-22 13:37 burov_alexey@mail.ru]:
        # Use weakref
        # self._entity_ref: ProxyType[IEntity] = weakref.proxy(entity)
        self._entity: IEntity = entity
        self._owner_attr_id: str = own_attr_id

    @property
    def ownerID(self) -> int:
        return self._entity.id

    @property
    def owner(self) -> IEntity:
        return self._entity

    @property
    def name(self) -> str:
        return descr.entity.DESC_BY_NAME[self._entity.className()] \
            .property_desc_by_id[10].name

    def className(self) -> str:
        return self.__class__.__name__

    @property
    def isDestroyed(self) -> bool:
        return self._entity.isDestroyed

    def onAttached(self, owner: IKBEClientEntity):
        logger.debug('[%s] %s', self, devonly.func_args_values())

    def onDetached(self, owner: IKBEClientEntity):
        logger.debug('[%s] %s', self, devonly.func_args_values())

    def onEnterworld(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())

    def onLeaveworld(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())

    def onGetBase(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())

    def onGetCell(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())

    def onLoseCell(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())

    def __update_properties__(self, properties: dict):
        for name, value in properties.items():
            old_value = getattr(self, f'_{name}')
            setattr(self, f'_{name}', value)

            set_method = getattr(self, f'set_{name}', None)
            if set_method is not None:
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
        return f'{self.__class__.__name__}(owner={self._entity})'
