"""Класс для коммуникации между разными игровыми слоями.

Инкапсулирует межтредовое взаимодействие.
"""

from __future__ import annotations

import abc
import enum
import logging
from typing import *

from enki import devonly

logger = logging.getLogger(__name__)


class KBEComponentEnum(enum.Enum):
    CELL = enum.auto()
    BASE = enum.auto()


class TargetEnum(enum.Enum):
    ENTITY = enum.auto()
    COMPONENT = enum.auto()


class ActionEnum(enum.Enum):
    UPDATE = enum.auto()
    REMOTE_CALL = enum.auto()


class _ILayer:
    """Инкапсулирует передачу вызовов между разными слоями приложения.

    Методы этого интерфейса можно вызывать из соседнего игрового слоя,
    который может находиться в соседнем трэде или процессе.
    """
    pass


class IThreadSafeAction(abc.ABC):
    """Действия, у которых обычный метод вызывается в одном треде, колбэк в другом."""


class GLUpdateEntityAction(IThreadSafeAction):

    def update_entity_properties(self, entity_id: int, properties: dict[str, Any]):
        logger.debug('[%s] %s', self, devonly.func_args_values())

    def on_update_entity_properties(self, entity_id: int, properties: dict[str, Any]):
        logger.debug('[%s] %s', self, devonly.func_args_values())


# TODO: [2022-11-08 16:36 burov_alexey@mail.ru]:
# Возможно, обновлять отдельно свойства компонентов не нужно. Компоненты уже
# обновятся в игровом слое.
class GLUpdateComponentAction(IThreadSafeAction):

    def update_component_properties(self, entity_id: int, component_name: str,
                                    properties: dict[str, Any]):
        logger.debug('[%s] %s', self, devonly.func_args_values())

    def on_update_component_properties(self, entity_id: int, component_name: str,
                                       properties: dict[str, Any]):
        logger.debug('[%s] %s', self, devonly.func_args_values())


class GLCallEntityMethodAction(IThreadSafeAction):

    def call_entity_method(self, entity_id: int, method_name: str, *args: list):
        logger.debug('[%s] %s', self, devonly.func_args_values())

    def on_call_entity_method(self, entity_id: int, method_name: str, *args: list):
        logger.debug('[%s] %s', self, devonly.func_args_values())


class GLCallComponentMethodAction(IThreadSafeAction):

    def call_component_method(self, enity_id: int, component_name: str, method_name: str,
                              *args: list):

        logger.debug('[%s] %s', self, devonly.func_args_values())

    def on_call_component_method(self, enity_id: int, component_name: str,
                                 method_name: str, *args: list):
        logger.debug('[%s] %s', self, devonly.func_args_values())


class GLOnEntityDestroyedAction(IThreadSafeAction):

    def call_entity_destroyed(self, entity_id: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())

    def on_call_entity_destroyed(self, entity_id: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())


class GLOnEntityCreatedAction(IThreadSafeAction):

    def call_entity_created(self, entity_id: int, entity_cls_name: str):
        logger.debug('[%s] %s', self, devonly.func_args_values())

    def on_call_entity_created(self, entity_id: int, entity_cls_name: str):
        logger.debug('[%s] %s', self, devonly.func_args_values())


class GameLayer(_ILayer, GLCallComponentMethodAction, GLCallEntityMethodAction,
                GLOnEntityCreatedAction, GLOnEntityDestroyedAction,
                GLUpdateComponentAction, GLUpdateEntityAction):
    """Игровой слой.

    Это взаимодействие из сетевого слоя в игровой.
    """


class IPluginLayer(_ILayer):

    @abc.abstractmethod
    def call_entity_remote_method(self, entity_cls_name: str, entity_id: int,
                                  kbe_component: KBEComponentEnum,
                                  method_name: str, args: tuple):
        """Вызвать сетевой удалённый метод у сущности.
        """
        logger.debug('[%s] %s', self, devonly.func_args_values())

    @abc.abstractmethod
    def call_component_remote_method(self, entity_cls_name: str, entity_id: int,
                                     kbe_component: KBEComponentEnum,
                                     owner_attr_id: int, method_name: str, args: tuple):
        """Вызвать сетевой удалённый метод у компонента сущности."""
        logger.debug('[%s] %s', self, devonly.func_args_values())

    @abc.abstractmethod
    def on_call_entity_remote_method(self, entity_cls_name: str, entity_id: int,
                                     kbe_component: KBEComponentEnum,
                                     method_name: str, args: tuple):
        logger.debug('[%s] %s', self, devonly.func_args_values())

    @abc.abstractmethod
    def on_call_component_remote_method(self, entity_cls_name: str, entity_id: int,
                                        kbe_component: KBEComponentEnum,
                                        owner_attr_id: int, method_name: str, args: tuple):
        logger.debug('[%s] %s', self, devonly.func_args_values())


class IUpdatableEntity(abc.ABC):
    """Интерфейс для обновляемой сущности.

    Обновляемой как с сервера на клиенте, так и в обратную сторону.
    """

    @property
    @abc.abstractmethod
    def id(self) -> int:
        logger.debug('[%s] %s', self, devonly.func_args_values())

    @abc.abstractmethod
    def __update_properties__(self, properties: dict[str, Any]):
        """Update property of the entity."""
        logger.debug('[%s] %s', self, devonly.func_args_values())

    @abc.abstractmethod
    def __update_component_properties__(self, component_name: str,
                                        properties: dict[str, Any]):
        """Update property of the entity."""
        logger.debug('[%s] %s', self, devonly.func_args_values())

    @abc.abstractmethod
    def __on_remote_call__(self, method_name: str, arguments: list) -> None:
        """The callback fires when the method has been called on the server."""
        logger.debug('[%s] %s', self, devonly.func_args_values())

    @abc.abstractmethod
    def __on_component_remote_call__(self, component_name: str, method_name: str,
                                     args: tuple) -> None:
        """The callback fires when the component method has been called on the server."""
        logger.debug('[%s] %s', self, devonly.func_args_values())

    @abc.abstractmethod
    def __call_remote_method__(self, kbe_component: KBEComponentEnum,
                               method_name: str, args: tuple):
        """Call the server remote method of the entity."""
        logger.debug('[%s] %s', self, devonly.func_args_values())

    @abc.abstractmethod
    def __call_component_remote_method__(self, kbe_component: KBEComponentEnum,
                                         owner_attr_id: int, method_name: str,
                                         args: tuple):
        """Call the server remote component method of the entity."""
        logger.debug('[%s] %s', self, devonly.func_args_values())


# class UpdatableEntity(IUpdatableEntity):

#     @property
#     @abc.abstractmethod
#     def id(self) -> int:
#         logger.debug('[%s] %s', self, devonly.func_args_values())

#     def __update_properties__(self, properties: dict[str, Any]):
#         """Update property of the entity."""
#         logger.debug('[%s] %s', self, devonly.func_args_values())

#     def __update_component_properties__(self, component_name: str,
#                                         properties: dict[str, Any]):
#         """Update property of the entity."""
#         logger.debug('[%s] %s', self, devonly.func_args_values())

#     def __on_remote_call__(self, method_name: str, arguments: list) -> None:
#         """The callback fires when the method has been called on the server."""
#         logger.debug('[%s] %s', self, devonly.func_args_values())

#     def __on_component_remote_call__(self, component_name: str, method_name: str,
#                                      args: tuple) -> None:
#         """The callback fires when the component method has been called on the server."""
#         logger.debug('[%s] %s', self, devonly.func_args_values())

#     def __call_remote_method__(self, kbe_component: KBEComponentEnum,
#                                method_name: str, args: tuple):
#         """Call the server remote method of the entity."""
#         logger.debug('[%s] %s', self, devonly.func_args_values())

#     def __call_component_remote_method__(self, kbe_component: KBEComponentEnum,
#                                          owner_attr_id: int, method_name: str,
#                                          args: tuple):
#         """Call the server remote component method of the entity."""
#         logger.debug('[%s] %s', self, devonly.func_args_values())
