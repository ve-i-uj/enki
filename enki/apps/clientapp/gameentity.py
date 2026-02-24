"""Классы игровой сущности, используемой в игоровом слое."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Generic, TypeVar

from enki.misc import devonly
from enki.novalue import NoValue
from enki.vectors import Direction, Position

from .kbeapi import IKBEClientEntity, IKBEClientEntityComponent

if TYPE_CHECKING:
    from .layer.ilayer import INetLayer, KBEComponentEnum

logger = logging.getLogger(__name__)


class IUpdatableEntity(ABC):
    """Интерфейс для обновляемой сущности.

    Обновляемой как с сервера на клиенте, так и в обратную сторону.
    """

    @property
    @abstractmethod
    def id(self) -> int:
        """Id сущности."""

    @abstractmethod
    def __on_update_properties__(self, properties: dict[str, Any]) -> None:
        """Update property of the entity."""

    @abstractmethod
    def __on_update_component_properties__(
        self, component_name: str, properties: dict[str, Any]
    ) -> None:
        """Update property of the entity component."""

    @abstractmethod
    def __on_remote_call__(self, method_name: str, args: tuple) -> None:
        """Fire when the method has been called on the server."""

    @abstractmethod
    def __on_component_remote_call__(
        self, component_name: str, method_name: str, args: tuple
    ) -> None:
        """Fire when the component method has been called on the server."""

    @abstractmethod
    def __call_remote_method__(
        self, kbe_component: KBEComponentEnum, method_name: str, args: tuple
    ) -> None:
        """Call the server remote method of the entity."""

    @abstractmethod
    def __call_component_remote_method__(
        self,
        kbe_component: KBEComponentEnum,
        owner_attr_id: int,
        method_name: str,
        args: tuple,
    ) -> None:
        """Call the server remote component method of the entity."""


class _EntityRemoteCall:
    """Удалённый вызов метода сущности."""

    def __init__(self, entity: ClientGameEntity) -> None:
        self._entity = entity

    def call_remote_method(
        self, kbe_component: KBEComponentEnum, method_name: str, args: tuple
    ) -> None:
        self._entity.__call_remote_method__(kbe_component, method_name, args)


class _ClientEntityComponentRemoteCall:
    """Удалённый вызов компоенента метода сущности."""

    def __init__(self, e_component: ClientGameEntityComponent) -> None:
        self._e_component = e_component

    def call_remote_method(
        self, kbe_component: KBEComponentEnum, method_name: str, args: tuple
    ) -> None:
        self._e_component.owner.__call_component_remote_method__(
            kbe_component, self._e_component.owner_attr_id, method_name, args
        )


class ClientEntityBaseRemoteCall(_EntityRemoteCall):
    """Удалённый вызов на Base компонент сущности."""


class ClientEntityCellRemoteCall(_EntityRemoteCall):
    """Удалённый вызов на Cell компонент сущности."""


class ClientEntityComponentBaseRemoteCall(_ClientEntityComponentRemoteCall):
    """Удалённый вызов компоенента метода сущности, расположенной на серверном
    компоненте 'Base'.
    """


class ClientEntityComponentCellRemoteCall(_ClientEntityComponentRemoteCall):
    """Удалённый вызов компоенента метода сущности, расположенной на серверном
    компоненте 'Cell'.
    """


_C_CO = TypeVar("_C_CO", bound=ClientEntityComponentCellRemoteCall)
_B_CO = TypeVar("_B_CO", bound=ClientEntityComponentBaseRemoteCall)


class _IKBEClientEntityComponent(
    IKBEClientEntityComponent, Generic[_C_CO, _B_CO]
):

    @property
    @abstractmethod
    def cell(self) -> _C_CO:
        pass

    @property
    @abstractmethod
    def base(self) -> _B_CO:
        pass


class ClientGameEntityComponent(
    _IKBEClientEntityComponent[
        ClientEntityComponentCellRemoteCall, ClientEntityComponentBaseRemoteCall
    ]
):
    """Компонент игровой сущности (т.е. сущность в свойстве).

    Родительский класс для всех сгенерированных компонентов игровых сущностей.
    """

    CLS_ID: ClassVar[int] = NoValue.NO_ENTITY_CLS_ID

    def __init__(self, entity: ClientGameEntity, owner_attr_id: int) -> None:
        # TODO: [2022-08-22 13:37 burov_alexey@mail.ru]:
        # Use weakref
        # self._entity_ref: ProxyType[IEntity] = weakref.proxy(entity)
        self._entity = entity
        self._owner_attr_id: int = owner_attr_id

        # self._cell = ClientEntityComponentCellRemoteCall(self)
        # self._base = ClientEntityComponentBaseRemoteCall(self)

    @property
    def owner_attr_id(self) -> int:
        return self._owner_attr_id

    @property
    def cell(self) -> ClientEntityComponentCellRemoteCall:
        raise NotImplementedError

    @property
    def base(self) -> ClientEntityComponentBaseRemoteCall:
        raise NotImplementedError

    @property
    def ownerID(self) -> int:
        return self._entity.id

    @property
    def owner(self) -> ClientGameEntity:
        return self._entity

    @property
    def name(self) -> str:
        return NoValue.NO_COMPONENT_NAME

    @property
    def className(self) -> str:
        return self.__class__.__name__

    @property
    def isDestroyed(self) -> bool:
        return self._entity.isDestroyed

    def onAttached(self, owner: ClientGameEntity) -> None:
        logger.info("[%s] %s", self, devonly.func_args_values())

    def onDetached(self, owner: ClientGameEntity) -> None:
        logger.info("[%s] %s", self, devonly.func_args_values())

    def onEnterWorld(self) -> None:
        logger.info("[%s] %s", self, devonly.func_args_values())

    def onLeaveWorld(self) -> None:
        logger.info("[%s] %s", self, devonly.func_args_values())

    def onEnterSpace(self) -> None:
        logger.info("[%s] %s", self, devonly.func_args_values())

    def onLeaveSpace(self) -> None:
        logger.info("[%s] %s", self, devonly.func_args_values())

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(owner={self._entity})"


_C = TypeVar("_C", bound=ClientEntityCellRemoteCall)
_B = TypeVar("_B", bound=ClientEntityBaseRemoteCall)
_CO = TypeVar("_CO", bound=IKBEClientEntityComponent)


class IClientGameEntity(
    IKBEClientEntity, IUpdatableEntity, Generic[_CO, _C, _B]
):

    @property
    @abstractmethod
    def cell(self) -> _C:
        pass

    @property
    @abstractmethod
    def base(self) -> _B:
        pass


class ClientGameEntity(
    IClientGameEntity[
        ClientGameEntityComponent,
        ClientEntityCellRemoteCall,
        ClientEntityBaseRemoteCall,
    ]
):
    """Родительский класс для всех игровых сущностей в игровом слое."""

    def __init__(self, entity_id, is_player: bool, layer: INetLayer) -> None:
        self._id = entity_id
        self._layer = layer

        # self._cell = ClientEntityCellRemoteCall(entity=self)
        # self._base = ClientEntityBaseRemoteCall(entity=self)

        self._components: dict[str, ClientGameEntityComponent] = {}
        self._component_by_owner_attr_id = {
            comp.owner_attr_id: comp for comp in self._components.values()
        }

        self._isDestroyed: bool = False
        self._onGround: bool = False

        self._position = Position()
        self._direction = Direction()
        self._spaceID = NoValue.NO_ID

        self._inWorld = False
        self._isPlayer = is_player

    @property
    def id(self) -> int:
        return self._id

    @property
    def cell(self) -> ClientEntityCellRemoteCall:
        raise NotImplementedError

    @property
    def base(self) -> ClientEntityBaseRemoteCall:
        raise NotImplementedError

    def get_component_by_owner_attr_id(
        self, owner_attr_id: int
    ) -> ClientGameEntityComponent:
        return self._component_by_owner_attr_id[owner_attr_id]

    def __on_update_properties__(self, properties: dict):
        logger.debug("[%s] %s", self, devonly.func_args_values())
        if self._isDestroyed:
            logger.warning(
                f"[{self}] The entity properties cannot be updated "
                f"because the entity has been destroyed "
                f"(properties={properties})"
            )
            return

        for name, value in properties.items():
            if name in self._components:
                continue

            # [2026-02-24 10:45 burov_alexey@mail.ru]:
            # Нужно разобратсья с этим merge
            if name == "position":
                value: Position  # type: ignore
                value = value.merge(self.position)  # type: ignore
            elif name == "direction":
                value: Direction
                value = value.merge(self.direction)

            old_value = getattr(self, f"_{name}")
            setattr(self, f"_{name}", value)

            set_method = getattr(self, f"set_{name}", None)
            if set_method is not None:
                set_method(old_value)

    def __on_update_component_properties__(
        self, component_name: str, properties: dict[str, Any]
    ):
        logger.debug("[%s] %s", self, devonly.func_args_values())
        if self._isDestroyed:
            logger.warning(
                f"[{self}] The entity properties cannot be updated "
                f"because the entity has been destroyed "
                f"(properties={properties})"
            )
            return

        comp: ClientGameEntityComponent = getattr(self, component_name)
        for name, value in properties.items():
            old_value = getattr(comp, f"_{name}")
            setattr(comp, f"_{name}", value)

            set_method = getattr(self, f"set_{name}", None)
            if set_method is not None:
                set_method(old_value)

    def __on_remote_call__(self, method_name: str, args: tuple) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        if self._isDestroyed:
            logger.warning(
                f"[{self}] The entity cannot handle the remote "
                f"call because the entity has been destroyed"
            )
            return
        method = getattr(self, method_name)
        method(*args)

    def __on_component_remote_call__(
        self, component_name: str, method_name: str, args: tuple
    ) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        if self._isDestroyed:
            logger.warning(
                f"[{self}] The entity cannot handle the remote "
                f"call because the entity has been destroyed"
            )
            return
        comp: ClientGameEntityComponent = getattr(self, component_name)
        method = getattr(comp, method_name)
        method(*args)

    def __call_remote_method__(
        self, kbe_component: KBEComponentEnum, method_name: str, args: tuple
    ):
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._layer.call_entity_remote_method(
            self.className, self._id, kbe_component, method_name, args
        )

    def __call_component_remote_method__(
        self,
        kbe_component: KBEComponentEnum,
        owner_attr_id: int,
        method_name: str,
        args: tuple,
    ):
        logger.debug("[%s] %s", self, devonly.func_args_values())
        comp = self._component_by_owner_attr_id[owner_attr_id]
        self._layer.call_component_remote_method(
            self.className,
            self._id,
            kbe_component,
            comp.name,
            method_name,
            args,
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id})"

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
        return self._onGround

    @property
    def inWorld(self) -> bool:
        return self._inWorld

    def baseCall(self, methodName: str, methodArgs: list[Any]) -> None:
        method: Callable | None = getattr(self._base, methodName, None)
        if method is None:
            logger.warning(
                f'[{self}] The "base" attribute has no method "{methodName}"'
            )
            return

        method(*methodArgs)

    def cellCall(self, methodName: str, methodArgs: list[Any]) -> None:
        method: Callable | None = getattr(self._cell, methodName, None)
        if method is None:
            logger.warning(
                f'[{self}] The "cell" attribute has no method "{methodName}"'
            )
            return

        method(*methodArgs)

    def isPlayer(self) -> bool:
        return self._isPlayer

    def getComponent(
        self, componentName: str, all: bool
    ) -> list[ClientGameEntityComponent]:
        if all:
            return list(self._components.values())
        comp = self._components.get(componentName)
        if comp is None:
            logger.warning(
                "[%s] %s", self, f'There is no component "{componentName}"'
            )
            return []

        return [comp]

    def fireEvent(self, eventName: str, *args) -> None:
        logger.warning(
            "[%s] %s", self, 'The "fireEvent" method is not implemented'
        )

    def registerEvent(self, eventName: str, callback: Callable) -> None:
        logger.warning(
            "[%s] %s", self, 'The "registerEvent" method is not implemented'
        )

    def deregisterEvent(self, eventName: str, callback: Callable) -> None:
        logger.warning(
            "[%s] %s", self, 'The "deregisterEvent" method is not implemented'
        )

    def onDestroy(self) -> None:
        logger.info("[%s] %s", self, devonly.func_args_values())
        self._isDestroyed = True

    def onEnterWorld(self) -> None:
        logger.info("[%s] %s", self, devonly.func_args_values())
        self._inWorld = True

    def onLeaveWorld(self) -> None:
        logger.info("[%s] %s", self, devonly.func_args_values())
        self._inWorld = False

    def onEnterSpace(self) -> None:
        logger.info("[%s] %s", self, devonly.func_args_values())

    def onLeaveSpace(self) -> None:
        logger.info("[%s] %s", self, devonly.func_args_values())
