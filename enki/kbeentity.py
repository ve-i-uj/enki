"""The entity parent class."""

from __future__ import annotations

import logging
import sys
from typing import Callable, ClassVar, Optional, Type, Any

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

    _implementation_cls = None

    def __init__(self, entity_id: int, entity_mgr: IEntityMgr):
        self._id = entity_id
        self._entity_mgr = entity_mgr

        self._cell = CellEntityRemoteCall(entity=self)
        self._base = BaseEntityRemoteCall(entity=self)
        self._components: dict[str, IKBEClientEntityComponent] = {}

        self._pending_msgs: list[IMessage] = []

        self._is_destroyed: bool = False
        self._isDestroyed: bool = False

        self._is_on_ground: bool = False

    @property
    def is_on_ground(self) -> bool:
        return self._is_on_ground

    def set_on_ground(self, value: bool):
        self._is_on_ground = value

    @classmethod
    def get_implementation(cls) -> Optional[Type[IEntity]]:
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
    def is_initialized(self) -> bool:
        if self.CLS_ID == settings.NO_ENTITY_CLS_ID:
            return False
        return True

    @property
    def is_destroyed(self) -> bool:
        return self._is_destroyed

    def on_initialized(self):
        assert self.is_initialized
        for comp in self._components.values():
            comp.onAttached(self)

    def on_destroyed(self):
        assert self.is_initialized
        self._is_destroyed = True
        for comp in self._components.values():
            comp.onDetached(self)

    def on_enter_world(self):
        assert self.is_initialized
        for comp in self._components.values():
            comp.onEnterWorld()

    def on_leave_world(self):
        assert self.is_initialized
        for comp in self._components.values():
            comp.onLeaveWorld()

    def on_enter_space(self):
        assert self.is_initialized
        for comp in self._components.values():
            comp.onEnterSpace()

    def on_leave_space(self):
        assert self.is_initialized
        for comp in self._components.values():
            comp.onLeaveSpace()

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
            if name in self._components:
                value: kbetype.EntityComponentData
                old_value.__update_properties__(value.properties)
                return

            setattr(self, f'_{name}', value)

            set_method = getattr(self, f'set_{name}', None)
            if set_method is not None:
                set_method(old_value)

    def __remote_call__(self, msg: IMessage):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        if self._is_destroyed:
            logger.warning(f'[{self}] The entity cannot send the message {msg.id} '
                           f'because the entity has been destroyed')
            return
        self._entity_mgr.remote_call(msg)

    def __on_remote_call__(self, method_name: str, arguments: list) -> None:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        if self._is_destroyed:
            logger.warning(f'[{self}] The entity cannot handle the remote '
                           f'call because the entity has been destroyed')
            return
        method = getattr(self, method_name)
        method(*arguments)

    def __str__(self):
        return f'{self.__class__.__name__}(id={self._id})'

    @property
    def direction(self) -> kbetype.Direction:
        raise NotImplementedError

    @property
    def position(self) -> kbetype.Position:
        raise NotImplementedError

    @property
    def spaceID(self) -> int:
        raise NotImplementedError

    @property
    def isDestroyed(self) -> bool:
        return self.is_destroyed

    @property
    def isOnGround(self) -> bool:
        return self._is_on_ground

    @property
    def inWorld(self) -> bool:
        raise NotImplementedError

    def className(self) -> str:
        return self.__class__.__name__

    def baseCall(self, methodName: str, methodArgs: list[Any]) -> None:
        method: Optional[Callable] = getattr(self._base, methodName, None)
        if method is None:
            logger.warning(f'[{self}] The "base" attribute has no method "{methodName}"')
            return

        method(*methodArgs)

    def cellCall(self, methodName: str, methodArgs: list[Any]) -> None:
        method: Optional[Callable] = getattr(self._cell, methodName, None)
        if method is None:
            logger.warning(f'[{self}] The "cell" attribute has no method "{methodName}"')
            return

        method(*methodArgs)

    def isPlayer(self) -> bool:
        return self._entity_mgr.is_player(self.id)

    def getComponent(self, componentName: str, all: bool):
        raise NotImplementedError

    def fireEvent(self, eventName: str, *args):
        raise NotImplementedError

    def registerEvent(self, eventName: str, callback: Callable):
        raise NotImplementedError

    def deregisterEvent(self, eventName: str, callback: Callable):
        raise NotImplementedError

    def onDestroy(self):
        logger.info('[%s] %s', self, devonly.func_args_values())

    def onEnterWorld(self):
        logger.info('[%s] %s', self, devonly.func_args_values())

    def onLeaveWorld(self):
        logger.info('[%s] %s', self, devonly.func_args_values())

    def onEnterSpace(self):
        logger.info('[%s] %s', self, devonly.func_args_values())

    def onLeaveSpace(self):
        logger.info('[%s] %s', self, devonly.func_args_values())


class EntityComponent(_EntityRemoteCall, IKBEClientEntityComponent):

    def __init__(self, entity: IEntity, own_attr_id: int):
        # TODO: [2022-08-22 13:37 burov_alexey@mail.ru]:
        # Use weakref
        # self._entity_ref: ProxyType[IEntity] = weakref.proxy(entity)
        self._entity: IEntity = entity
        self._owner_attr_id: int = own_attr_id

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
        logger.info('[%s] %s', self, devonly.func_args_values())

    def onDetached(self, owner: IKBEClientEntity):
        logger.info('[%s] %s', self, devonly.func_args_values())

    def onEnterWorld(self):
        logger.info('[%s] %s', self, devonly.func_args_values())

    def onLeaveWorld(self):
        logger.info('[%s] %s', self, devonly.func_args_values())

    def onEnterSpace(self):
        logger.info('[%s] %s', self, devonly.func_args_values())

    def onLeaveSpace(self):
        logger.info('[%s] %s', self, devonly.func_args_values())

    def __update_properties__(self, properties: dict):
        for name, value in properties.items():
            old_value = getattr(self, f'_{name}')
            setattr(self, f'_{name}', value)

            set_method = getattr(self, f'set_{name}', None)
            if set_method is not None:
                set_method(old_value)

    def __on_remote_call__(self, method_name: str, arguments: list) -> None:
        """The callback fires when method has been called on the server."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        method = getattr(self, method_name)
        method(*arguments)

    def __str__(self):
        return f'{self.__class__.__name__}(owner={self._entity})'
