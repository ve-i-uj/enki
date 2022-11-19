"""Threaded layers."""

import logging
from functools import cached_property
from typing import *

from enki import devonly
from enki.net.kbeclient import Message
from enki.net.netentity import IEntityRPCSerializer

from enki import layer
from enki.layer import IGameLayer, INetLayer, KBEComponentEnum

from .iapp import IApp
from .gameentity import GameEntity

logger = logging.getLogger(__name__)


class ThreadedGameLayer(IGameLayer):

    def __init__(self, entity_cls_by_name: dict[str, Type[GameEntity]]) -> None:
        self._entities: dict[int, GameEntity] = {}
        self._entity_cls_by_name = entity_cls_by_name

    @cached_property
    def net(self) -> INetLayer:
        return layer.get_net_layer()

    # *** Сущность создана ***

    def call_entity_created(self, entity_id: int, entity_cls_name: str, is_player: bool):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self.on_call_entity_created(entity_id, entity_cls_name, is_player)

    def on_call_entity_created(self, entity_id: int, entity_cls_name: str, is_player: bool):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        e_cls = self._entity_cls_by_name[entity_cls_name]
        entity = e_cls(entity_id, is_player, self.net)
        self._entities[entity.id] = entity

    # *** Сущность уничтожена ***

    def call_entity_destroyed(self, entity_id: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self.on_call_entity_destroyed(entity_id)

    def on_call_entity_destroyed(self, entity_id: int):
        # TODO: [2022-11-18 12:57 burov_alexey@mail.ru]:
        # На начальных итерациях хватит и такого
        del self._entities[entity_id]

    # *** Вызов метода сущности ***

    def call_entity_method(self, entity_id: int, method_name: str, *args: list):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self.on_call_entity_method(entity_id, method_name, *args)

    def on_call_entity_method(self, entity_id: int, method_name: str, *args):
        entity = self._entities[entity_id]
        entity.__on_remote_call__(method_name, args)

    # *** Обновить свойства сущности ***

    def update_entity_properties(self, entity_id: int, properties: dict[str, Any]):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self.on_update_entity_properties(entity_id, properties)

    def on_update_entity_properties(self, entity_id: int, properties: dict[str, Any]):
        entity = self._entities[entity_id]
        entity.__on_update_properties__(properties)

    # *** Обновить свойства компонента-атрибута сущности ***

    def update_component_properties(self, entity_id: int, component_name: str,
                                    properties: dict[str, Any]):
        self.on_update_component_properties(entity_id, component_name, properties)

    def on_update_component_properties(self, entity_id: int, component_name: str,
                                       properties: dict[str, Any]):
        entity = self._entities[entity_id]
        entity.__on_update_component_properties__(component_name, properties)

    # *** Вызов метода компонента-атрибута сущности ***

    def call_component_method(self, entity_id: int, component_name: str,
                              method_name: str, *args: list):
        self.on_call_component_method(entity_id, component_name, method_name, *args)

    def on_call_component_method(self, entity_id: int, component_name: str,
                                 method_name: str, *args: list):
        entity = self._entities[entity_id]
        entity.__on_component_remote_call__(component_name, method_name, args)


    # *** Сообщает, что компонент привязался к сущности ***

    def call_component_onAttached(self, entity_id: int, component_name: str):
        self.on_call_component_onAttached(entity_id, component_name)

    def on_call_component_onAttached(self, entity_id: int, component_name: str):
        entity = self._entities[entity_id]
        entity.__on_component_remote_call__(component_name, 'onAttached', (entity, ))


class ThreadedNetLayer(INetLayer):

    def __init__(self, entity_serializer_cls_by_name: dict[str, Type[IEntityRPCSerializer]],
                 app: IApp) -> None:
        self._eserializer_by_name = {
            n: cls() for n, cls in entity_serializer_cls_by_name.items()
        }
        self._app = app

    @cached_property
    def game(self) -> IGameLayer:
        return layer.get_game_layer()

    def call_entity_remote_method(self, entity_cls_name: str, entity_id: int, kbe_component: KBEComponentEnum, method_name: str, args: tuple):
        self.on_call_entity_remote_method(entity_cls_name, entity_id, kbe_component, method_name, args)

    def on_call_entity_remote_method(self, entity_cls_name: str, entity_id: int, kbe_component: KBEComponentEnum, method_name: str, args: tuple):
        """This call is on the net side."""
        serializer = self._eserializer_by_name[entity_cls_name]
        if kbe_component == KBEComponentEnum.BASE:
            method: Callable = getattr(serializer.base, method_name)
        else:
            method: Callable = getattr(serializer.cell, method_name)
        msg: Message = method(entity_id, *args)
        self._app.send_message(msg)

    def call_component_remote_method(self, entity_cls_name: str, entity_id: int, kbe_component: KBEComponentEnum, owner_attr_id: int, method_name: str, args: tuple):
        return super().call_component_remote_method(entity_cls_name, entity_id, kbe_component, owner_attr_id, method_name, args)

    def on_call_component_remote_method(self, entity_cls_name: str, entity_id: int, kbe_component: KBEComponentEnum, owner_attr_id: int, method_name: str, args: tuple):
        return super().on_call_component_remote_method(entity_cls_name, entity_id, kbe_component, owner_attr_id, method_name, args)
