"""Threaded layers."""

import abc
import asyncio
import logging
import queue
from dataclasses import dataclass
from functools import cached_property
import time
from typing import *

from enki import devonly, settings
from enki.net.kbeclient import Message
from enki.net.netentity import IEntityRPCSerializer

from enki import layer
from enki.layer import IGameLayer, INetLayer, KBEComponentEnum

from .iapp import IApp
from .gameentity import GameEntity

logger = logging.getLogger(__name__)


@dataclass
class QueueCallbackItem:
    callback: Callable
    args: tuple[Any, ...]


class GameState:

    def __init__(self) -> None:
        self._entities: dict[int, GameEntity] = {}
        self._player_id = settings.NO_ENTITY_ID
        self._account_name = ''
        self._password = ''

        self.space_data: dict[int, dict[str, str]] = {}

    def get_account_name(self) -> str:
        return self._account_name

    def get_password(self) -> str:
        return self._password

    def set_account_name(self, name: str, password: str):
        self._account_name = name
        self._password = password

    def get_entities(self) -> dict[int, GameEntity]:
        return dict(self._entities)

    def get_entity(self, entity_id: int) -> GameEntity:
        return self._entities[entity_id]

    def get_player(self) -> GameEntity:
        return self.get_entity(self._player_id)

    def add_entity(self, entity: GameEntity):
        self._entities[entity.id] = entity
        if entity.isPlayer():
            self._player_id = entity.id

    def delete_entity(self, entity_id: int):
        entity = self._entities[entity_id]
        del self._entities[entity_id]
        if entity.isPlayer():
            self._player_id = settings.NO_ENTITY_ID

    def get_player_id(self) -> int:
        return self._player_id

# TODO: [2022-11-21 15:40 burov_alexey@mail.ru]:
# Здесь сразу сделана и игровая реализация и будет и трэды. Я бы ботву
# с тредами здесь остваил, а игру реализоваывал бы уже в отельном модуле.
# Трэдовая реализация, а рядом абстрактные методы для реализации.


class IGameQueueHolder(abc.ABC):

    @property
    @abc.abstractmethod
    def _queue(self) -> queue.Queue:
        return


def call_in_game_thread(method: Callable):

    def wrapper(self: IGameQueueHolder, *args):
        item = QueueCallbackItem(method, args)
        try:
            self._queue.put_nowait(item)
        except queue.Full as err:
            logger.error('[%s] %s', self, devonly.func_args_values())
            # TODO: [2022-11-22 11:24 burov_alexey@mail.ru]:
            # Пока заваливать приложение, чтобы на отладке поймать подобную проблему
            raise SystemExit(err)

    return wrapper


class ThreadedGameLayer(IGameLayer):
    """Игровой слой в отдельном трэде."""

    def __init__(self, entity_cls_by_name: dict[str, Type[GameEntity]],
                 game_queue: queue.Queue[QueueCallbackItem]) -> None:
        self._entity_cls_by_name = entity_cls_by_name
        self._game_state = GameState()
        self._queue = game_queue

    def call_in_game_thread(self, callback, args):
        item = QueueCallbackItem(callback, args)
        try:
            self._queue.put_nowait(item)
        except queue.Full as err:
            logger.error('[%s] %s', self, devonly.func_args_values())
            # TODO: [2022-11-22 11:24 burov_alexey@mail.ru]:
            # Пока заваливать приложение, чтобы на отладке поймать подобную проблему
            raise SystemExit(err)

    def get_game_state(self) -> GameState:
        return self._game_state

    @cached_property
    def net(self) -> INetLayer:
        return layer.get_net_layer()

    def update_from_net(self, block=False) -> int:
        """Вычитывает одно сообщение из очереди.

        Ничего не делает, если в очереди нет сообщения. Должен вызываться
        из игрового трэда для получения обновления состояния.
        """
        try:
            # TODO: [2022-11-22 16:56 burov_alexey@mail.ru]:
            # Обязательно нужна блокировка, иначе на соседний трэд в обще не переключится.
            # Таймаут тоже нужен обязательно, т.к. можно в тестах попасть на
            # пустою очередь и зависнуть.
            item = self._queue.get(block=block, timeout=1)
        except queue.Empty:
            return 0
        # Вызов метода в другом трэде
        item.callback(*item.args)
        return 1

    # *** Сущность создана ***

    def call_entity_created(self, entity_id: int, entity_cls_name: str, is_player: bool):
        """Сообщить, что сущность создана (вызов из сетевого трэда)."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self.call_in_game_thread(
            self.on_call_entity_created,
            (entity_id, entity_cls_name, is_player)
        )

    def on_call_entity_created(self, entity_id: int, entity_cls_name: str, is_player: bool):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        e_cls = self._entity_cls_by_name[entity_cls_name]
        entity = e_cls(entity_id, is_player, self.net)
        self._game_state.add_entity(entity)

    # *** Сущность уничтожена ***

    def call_entity_destroyed(self, entity_id: int):
        """Сущность уничтожена (вызов в сетевом трэде)."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self.call_in_game_thread(
            self.on_call_entity_destroyed,
            (entity_id, )
        )

    def on_call_entity_destroyed(self, entity_id: int):
        """Сущность уничтожена (вызов в игровом трэде)."""
        # TODO: [2022-11-18 12:57 burov_alexey@mail.ru]:
        # На начальных итерациях хватит и такого
        self._game_state.delete_entity(entity_id)

    # *** Вызов метода сущности ***

    def call_entity_method(self, entity_id: int, method_name: str, *args: list):
        """Получен вызов удалённого метода (вызов в сетевом трэде)."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self.call_in_game_thread(
            self.on_call_entity_method,
            (entity_id, method_name, args)
        )

    def on_call_entity_method(self, entity_id: int, method_name: str, args: tuple):
        """Получен вызов удалённого метода (вызов в игровом трэде)."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        entity = self._game_state.get_entity(entity_id)
        entity.__on_remote_call__(method_name, args)

    # *** Обновить свойства сущности ***

    def update_entity_properties(self, entity_id: int, properties: dict[str, Any]):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self.call_in_game_thread(
            self.on_update_entity_properties,
            (entity_id, properties)
        )

    def on_update_entity_properties(self, entity_id: int, properties: dict[str, Any]):
        entity = self._game_state.get_entity(entity_id)
        entity.__on_update_properties__(properties)

    # *** Обновить свойства компонента-атрибута сущности ***

    def update_component_properties(self, entity_id: int, component_name: str,
                                    properties: dict[str, Any]):
        self.call_in_game_thread(
            self.on_update_component_properties,
            (entity_id, component_name, properties)
        )

    def on_update_component_properties(self, entity_id: int, component_name: str,
                                       properties: dict[str, Any]):
        entity = self._game_state.get_entity(entity_id)
        entity.__on_update_component_properties__(component_name, properties)

    # *** Вызов метода компонента-атрибута сущности ***

    def call_component_method(self, entity_id: int, component_name: str,
                              method_name: str, *args: list):
        self.call_in_game_thread(
            self.on_call_component_method,
            (entity_id, component_name, method_name, args)
        )

    def on_call_component_method(self, entity_id: int, component_name: str,
                                 method_name: str, args: tuple):
        entity = self._game_state.get_entity(entity_id)
        entity.__on_component_remote_call__(component_name, method_name, args)

    # *** Сообщает, что компонент привязался к сущности ***

    def call_component_onAttached(self, entity_id: int, component_name: str):
        self.call_in_game_thread(
            self.on_call_component_onAttached,
            (entity_id, component_name)
        )

    def on_call_component_onAttached(self, entity_id: int, component_name: str):
        entity = self._game_state.get_entity(entity_id)
        entity.__on_component_remote_call__(component_name, 'onAttached', (entity, ))

    """ Выставить Space Data значение """

    def call_set_space_data(self, space_id: int, key: str, value: str):
        self.call_in_game_thread(
            self.on_call_set_space_data,
            (space_id, key, value)
        )

    def on_call_set_space_data(self, space_id: int, key: str, value: str):
        self._game_state.space_data[space_id][key] = value

    """ Удалить Space Data значение """

    def call_delete_space_data(self, space_id: int, key: str):
        self.call_in_game_thread(
            self.on_call_delete_space_data,
            (space_id, key)
        )

    def on_call_delete_space_data(self, space_id: int, key: str):
        # От сервера вызовы должны приходить без повреждения данных (т.е.
        # удаление не сущенствующего ключа не возможно)
        del self._game_state.space_data[space_id][key]

    """Ответы на различные действия."""

    def on_login(self, account_name: str, password: str, success: bool, reason: str):
        """Вызов в игровом трэде."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        if success:
            self._game_state.set_account_name(account_name, password)

    def on_bind_account_email(self, success: bool, reason: str):
        """Вызов в игровом трэде."""
        logger.debug('[%s] %s', self, devonly.func_args_values())

    def on_create_account(self, success: bool, reason: str):
        """Вызов в игровом трэде."""
        logger.debug('[%s] %s', self, devonly.func_args_values())

    def on_reset_password(self, success: bool, reason: str):
        """Вызов в игровом трэде."""
        logger.debug('[%s] %s', self, devonly.func_args_values())

    def on_set_new_password(self, success: bool, reason: str):
        """Вызов в игровом трэде."""
        logger.debug('[%s] %s', self, devonly.func_args_values())


class ThreadedNetLayer(INetLayer):
    """Сетевой слой.

    Его колбэки срабатывают в трэде с event loop.
    """

    def __init__(self, entity_serializer_cls_by_name: dict[str, Type[IEntityRPCSerializer]],
                 app: IApp,
                 loop: asyncio.AbstractEventLoop,
                 queue: queue.Queue[QueueCallbackItem]):
        self._eserializer_by_name = {
            n: cls() for n, cls in entity_serializer_cls_by_name.items()
        }
        self._app = app
        # Эта петля запущена в отдельном сетевом трэде. Ссылка на неё
        # используется в игровом трэде для отправки из игрового трэда
        # в сетевой вызовов.
        self._loop = loop
        self._queue = queue

    @cached_property
    def game(self) -> IGameLayer:
        return layer.get_game_layer()

    def call_in_game_thread(self, callback, args):
        item = QueueCallbackItem(callback, args)
        try:
            self._queue.put_nowait(item)
        except queue.Full as err:
            logger.error('[%s] %s', self, devonly.func_args_values())
            # TODO: [2022-11-22 11:24 burov_alexey@mail.ru]:
            # Пока заваливать приложение, чтобы на отладке поймать подобную проблему
            raise SystemExit(err)

    def call_entity_remote_method(self, entity_cls_name: str, entity_id: int,
                                  kbe_component: KBEComponentEnum,
                                  method_name: str, args: tuple):
        """Вызывает на стороне игрового трэда (колбэк будет вызван в сетевом трэде)."""
        asyncio.run_coroutine_threadsafe(
            self.on_call_entity_remote_method(
                entity_cls_name, entity_id, kbe_component, method_name, args
            ),
            self._loop
        )

    async def on_call_entity_remote_method(self, entity_cls_name: str, entity_id: int, kbe_component: KBEComponentEnum, method_name: str, args: tuple):
        """Колбэк, вызванный в сетевом трэде."""
        serializer = self._eserializer_by_name[entity_cls_name]
        if kbe_component == KBEComponentEnum.BASE:
            method: Callable = getattr(serializer.base, method_name)
        else:
            method: Callable = getattr(serializer.cell, method_name)
        msg: Message = method(entity_id, *args)
        self._app.send_message(msg)

    """Сделать удалённый вызов компонентета."""

    def call_component_remote_method(self, entity_cls_name: str, entity_id: int,
                                     kbe_component: KBEComponentEnum,
                                     owner_attr_name: str, method_name: str,
                                     args: tuple):
        asyncio.run_coroutine_threadsafe(
            self.on_call_component_remote_method(
                entity_cls_name, entity_id, kbe_component, owner_attr_name,
                method_name, args
            ),
            self._loop
        )

    async def on_call_component_remote_method(self, entity_cls_name: str,
                                              entity_id: int,
                                              kbe_component: KBEComponentEnum,
                                              owner_attr_name: str, method_name: str,
                                              args: tuple):
        """Вызов в сетевом трэде."""
        serializer: IEntityRPCSerializer = self._eserializer_by_name[entity_cls_name]
        comp_serializer = serializer.get_component_by_name(owner_attr_name)
        if kbe_component == KBEComponentEnum.BASE:
            method: Callable = getattr(comp_serializer.base, method_name)
        else:
            method: Callable = getattr(comp_serializer.cell, method_name)
        msg: Message = method(entity_id, *args)
        self._app.send_message(msg)

    """Залогиниться на игровом сервере."""

    def call_login(self, username: str, password: str):
        """Вызов в игровом трэде."""
        asyncio.run_coroutine_threadsafe(
            self.on_call_login(username, password), self._loop
        )

    async def on_call_login(self, username: str, password: str):
        """Вызов в сетевом трэде."""
        res = await self._app.start(username, password)
        if not res.success:
            logger.error(res.text)
            await self._app.stop()

        self.call_in_game_thread(self.game.on_login,
                                 (username, password, res.success, res.text))

    """Создать аккаунт."""

    def call_create_account(self, username: str, password: str):
        """Вызов в игровом трэде."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        asyncio.run_coroutine_threadsafe(
            self.on_call_create_account(username, password),
            self._loop
        )

    async def on_call_create_account(self, username: str, password: str):
        """Вызов в сетевом трэде."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        assert not self._app.is_connected
        res = await self._app.connect_to_loginapp()
        res = await self._app.create_account(username, password)

        self.call_in_game_thread(self.game.on_create_account,
                                 (res.success, res.text))

    """Скинуть пароль."""

    def call_reset_password(self, username: str):
        """Вызов в игровом трэде."""
        asyncio.run_coroutine_threadsafe(
            self.on_call_reset_password(username),
            self._loop
        )

    async def on_call_reset_password(self, username: str):
        """Вызов в сетевом трэде."""
        res = await self._app.reset_password(username)
        self.call_in_game_thread(
            self.game.on_reset_password,
            (res.success, res.text)
        )

    """Привязать попробовать email к аккаунту."""

    def call_bind_account_email(self, entity_id: int, password: str, email: str):
        """Вызов в игровом трэде."""
        asyncio.run_coroutine_threadsafe(
            self.on_call_bind_account_email(entity_id, password, email),
            self._loop
        )

    async def on_call_bind_account_email(self, entity_id: int, password: str, email: str):
        """Вызов в сетевом трэде."""
        res = await self._app.bind_account_email(entity_id, password, email)
        self.call_in_game_thread(
            self.game.on_bind_account_email,
            (res.success, res.text)
        )

    """Задать новый пароль."""

    def call_set_new_password(self, entity_id: int, oldpassword: str, newpassword: str):
        """Вызов в игровом трэде."""
        asyncio.run_coroutine_threadsafe(
            self.on_call_set_new_password(entity_id, oldpassword, newpassword),
            self._loop
        )

    async def on_call_set_new_password(self, entity_id: int, oldpassword: str, newpassword: str):
        """Вызов в сетевом трэде."""
        res = await self._app.set_new_password(entity_id, oldpassword, newpassword)
        self.call_in_game_thread(
            self.game.on_set_new_password,
            (res.success, res.text)
        )
