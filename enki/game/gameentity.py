"""???"""

from __future__ import annotations

import abc
import logging
from typing import Any, Optional, Callable

from enki import settings, devonly
from enki.net.kbeclient.kbetype import EntityComponentData, Position, Direction
from enki.app.appl import App
from enki.app.layer import IUpdatableEntity, KBEComponentEnum

from .kbeapi import IKBEClientKBEngineModule, IKBEClientGameEntity, IKBEClientGameEntityComponent

logger = logging.getLogger(__name__)


class _EntityRemoteCall:

    def __init__(self, entity: GameEntity) -> None:
        self._entity = entity

    def call_remote_method(self, kbe_component: KBEComponentEnum,
                           method_name: str, args: tuple):
        self._entity.__call_remote_method__(kbe_component, method_name, args)


class EntityBaseRemoteCall(_EntityRemoteCall):
    pass


class EntityCellRemoteCall(_EntityRemoteCall):
    pass


class _EntityComponentRemoteCall:

    def __init__(self, e_component: GameEntityComponent) -> None:
        self._e_component = e_component

    def call_remote_method(self, kbe_component: KBEComponentEnum,
                           method_name: str, args: tuple):
        self._e_component.owner.__call_component_remote_method__(
            kbe_component, self._e_component.owner_attr_id, method_name, args
        )


class EntityComponentBaseRemoteCall(_EntityComponentRemoteCall):
    pass


class EntityComponentCellRemoteCall(_EntityComponentRemoteCall):
    pass


class GameEntityComponent(IKBEClientGameEntityComponent):

    CLS_ID: int = settings.NO_ENTITY_CLS_ID

    def __init__(self, entity: GameEntity, owner_attr_id: int):
        # TODO: [2022-08-22 13:37 burov_alexey@mail.ru]:
        # Use weakref
        # self._entity_ref: ProxyType[IEntity] = weakref.proxy(entity)
        self._entity = entity
        self._owner_attr_id: int = owner_attr_id

        self._cell = EntityComponentCellRemoteCall(self)
        self._base = EntityComponentBaseRemoteCall(self)

    @property
    def owner_attr_id(self) -> int:
        return self._owner_attr_id

    @property
    def cell(self) -> EntityComponentCellRemoteCall:
        return self._cell

    @property
    def base(self) -> EntityComponentBaseRemoteCall:
        return self._base

    @property
    def ownerID(self) -> int:
        return self._entity.id

    @property
    def owner(self) -> GameEntity:
        return self._entity

    @property
    def name(self) -> str:
        return settings.NO_COMPONENT_NAME

    def className(self) -> str:
        return self.__class__.__name__

    @property
    def isDestroyed(self) -> bool:
        return self._entity.isDestroyed

    def onAttached(self, owner: GameEntity):
        logger.info('[%s] %s', self, devonly.func_args_values())

    def onDetached(self, owner: GameEntity):
        logger.info('[%s] %s', self, devonly.func_args_values())

    def onEnterWorld(self):
        logger.info('[%s] %s', self, devonly.func_args_values())

    def onLeaveWorld(self):
        logger.info('[%s] %s', self, devonly.func_args_values())

    def onEnterSpace(self):
        logger.info('[%s] %s', self, devonly.func_args_values())

    def onLeaveSpace(self):
        logger.info('[%s] %s', self, devonly.func_args_values())

    def __str__(self):
        return f'{self.__class__.__name__}(owner={self._entity})'


class GameEntity(IUpdatableEntity, IKBEClientGameEntity):
    """Родительский класс для всех игровых сущностей в игровом слое."""

    def __init__(self, entity_id, is_player: bool, app: App):
        self._id = entity_id
        self._app = app

        self._cell = EntityCellRemoteCall(entity=self)
        self._base = EntityBaseRemoteCall(entity=self)

        self._components: dict[str, GameEntityComponent] = {}

        self._isDestroyed: bool = False
        self._isOnGround: bool = False

        self._position = Position()
        self._direction = Direction()
        self._spaceID = settings.NO_ID

        self._inWorld = False
        self._isPlayer = is_player

    @property
    def id(self) -> int:
        return self._id

    @property
    def cell(self) -> EntityCellRemoteCall:
        return self._cell

    @property
    def base(self) -> EntityBaseRemoteCall:
        return self._base

    def __on_update_properties__(self, properties: dict):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        if self._isDestroyed:
            logger.warning(f'[{self}] The entity properties cannot be updated '
                           f'because the entity has been destroyed '
                           f'(properties={properties})')
            return

        for name, value in properties.items():
            if name in self._components:
                continue

            old_value = getattr(self, f'_{name}')
            setattr(self, f'_{name}', value)

            set_method = getattr(self, f'set_{name}', None)
            if set_method is not None:
                set_method(old_value)

    def __on_update_component_properties__(self, component_name: str,
                                           properties: dict[str, Any]):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        if self._isDestroyed:
            logger.warning(f'[{self}] The entity properties cannot be updated '
                           f'because the entity has been destroyed '
                           f'(properties={properties})')
            return

        comp: GameEntityComponent = getattr(self, component_name)
        for name, value in properties.items():
            old_value = getattr(self, f'_{name}')
            setattr(comp, f'_{name}', value)

            set_method = getattr(self, f'set_{name}', None)
            if set_method is not None:
                set_method(old_value)

    def __on_remote_call__(self, method_name: str, args: list) -> None:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        if self._isDestroyed:
            logger.warning(f'[{self}] The entity cannot handle the remote '
                           f'call because the entity has been destroyed')
            return
        method = getattr(self, method_name)
        method(*args)

    def __on_component_remote_call__(self, component_name: str, method_name: str,
                                     args: tuple) -> None:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        if self._isDestroyed:
            logger.warning(f'[{self}] The entity cannot handle the remote '
                           f'call because the entity has been destroyed')
            return
        comp: GameEntityComponent = getattr(self, component_name)
        method = getattr(comp, method_name)
        method(*args)

    def __call_remote_method__(self, kbe_component: KBEComponentEnum,
                               method_name: str, args: tuple):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._app.net.call_entity_remote_method(
            self.className, self._id, kbe_component, method_name, args
        )

    def __call_component_remote_method__(self, kbe_component: KBEComponentEnum,
                                         owner_attr_id: int, method_name: str,
                                         args: tuple):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._app.net.call_component_remote_method(
            self.className, self._id, kbe_component,
            owner_attr_id, method_name, args
        )

    def __str__(self):
        return f'{self.__class__.__name__}(id={self._id})'

    @property
    def position(self) -> Position:
        return self._position

    @property
    def direction(self) -> Direction:
        return self._direction

    @property
    def spaceID(self) -> int:
        return self._spaceID

    @property
    def isDestroyed(self) -> bool:
        return self._isDestroyed

    @property
    def isOnGround(self) -> bool:
        return self._isOnGround

    @property
    def inWorld(self) -> bool:
        return self._inWorld

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
        return self._isPlayer

    def getComponent(self, componentName: str, all: bool):
        if all:
            return list(self._components.values())
        comp = self._components.get(componentName)
        if comp is None:
            logger.warning('[%s] %s', self, f'There is no component "{componentName}"')
            return []
        return comp

    def fireEvent(self, eventName: str, *args):
        logger.warning('[%s] %s', self, f'The "fireEvent" method is not implemented')

    def registerEvent(self, eventName: str, callback: Callable):
        logger.warning('[%s] %s', self, f'The "registerEvent" method is not implemented')

    def deregisterEvent(self, eventName: str, callback: Callable):
        logger.warning('[%s] %s', self, f'The "deregisterEvent" method is not implemented')

    def onDestroy(self):
        logger.info('[%s] %s', self, devonly.func_args_values())
        self._isDestroyed = True

    def onEnterWorld(self):
        logger.info('[%s] %s', self, devonly.func_args_values())
        self._inWorld = True

    def onLeaveWorld(self):
        logger.info('[%s] %s', self, devonly.func_args_values())
        self._inWorld = False

    def onEnterSpace(self):
        logger.info('[%s] %s', self, devonly.func_args_values())

    def onLeaveSpace(self):
        logger.info('[%s] %s', self, devonly.func_args_values())


# # TODO: [2022-11-06 15:29 burov_alexey@mail.ru]:
# # Сущности не должны знать о приложении
# class PlayerMover:

#     def __init__(self, app: IApp):
#         self._app = app

#     def move(self, entity: IEntity,
#              new_position: Optional[Position] = None,
#              new_direction: Optional[Direction] = None):
#         logger.debug('[%s] %s', self, devonly.func_args_values())
#         assert entity.isPlayer(), f'The entity is not a player (entity = "{entity}")'
#         if new_position is None and new_direction is None:
#             logger.warning(f'[{self}] There is no new position nor direction')
#             return

#         if new_direction is not None:
#             raise NotImplementedError

#         position = new_position or entity.position
#         direction = new_direction or entity.direction

#         cmd = command.baseapp.OnUpdateDataFromClientForControlledEntityCommand(
#             self._app.client, entity.id, position, direction,
#             entity.is_on_ground, entity.spaceID
#         )

#         asyncio.run(self._app.send_command(cmd))
#         # TODO: [2022-09-18 09:10 burov_alexey@mail.ru]:
#         # Нужно как-то по другому придумать. Мы находимся сейчас в главном треде
#         # и пробуем обновить позицию сущности. Здесь или лок нужен или как-то
#         # по другому это делать.

#         async def _update_entity_pos_and_dir(entity: IEntity):
#             entity.__update_properties__({
#                 'position': position,
#                 'direction': direction,
#             })
#         asyncio.run(_update_entity_pos_and_dir(entity))
