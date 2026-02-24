"""Threaded layers."""

from __future__ import annotations

import asyncio
import collections
import logging
import queue
import time
from asyncio import AbstractEventLoop
from dataclasses import dataclass
from functools import cached_property
from queue import Empty, Queue
from typing import TYPE_CHECKING, Any, Callable

from enki import settings
from enki.apps.clientapp.app import (
    BaseappConnectionError,
    LoginappConnectionError,
)
from enki.apps.clientapp.layer import ilayer
from enki.kbeenum import ClientType, ServerError
from enki.misc import devonly
from enki.novalue import NoValue

from . import ilayer
from .ilayer import IGameLayer, INetLayer, KBEComponentEnum

if TYPE_CHECKING:
    from enki.apps.clientapp.app import ClientApp
    from enki.apps.clientapp.entity_sub_system.ientity_serializer import (
        IEntityRPCSerializer,
    )
    from enki.apps.clientapp.gameentity import ClientGameEntity
    from enki.msg.message import Message

logger = logging.getLogger(__name__)


@dataclass
class QueueCallbackItem:
    callback: Callable
    args: tuple[Any, ...]


class GameState:
    def __init__(self) -> None:
        self._entities: dict[int, ClientGameEntity] = {}
        self._player_id = NoValue.NO_ENTITY_ID
        self._account_name = ""
        self._password = ""

        self.space_data: dict[int, dict[str, str]] = collections.defaultdict(
            dict
        )

    def get_account_name(self) -> str:
        return self._account_name

    def get_password(self) -> str:
        return self._password

    def set_account_name(self, name: str, password: str) -> None:
        self._account_name = name
        self._password = password

    def get_entities(self) -> dict[int, ClientGameEntity]:
        return dict(self._entities)

    def get_entity(self, entity_id: int) -> ClientGameEntity:
        return self._entities[entity_id]

    def get_player(self) -> ClientGameEntity:
        return self.get_entity(self._player_id)

    def add_entity(self, entity: ClientGameEntity) -> None:
        self._entities[entity.id] = entity
        if entity.isPlayer():
            self._player_id = entity.id

    def delete_entity(self, entity_id: int) -> None:
        entity = self._entities[entity_id]
        del self._entities[entity_id]
        if entity.isPlayer():
            self._player_id = NoValue.NO_ENTITY_ID

    def get_player_id(self) -> int:
        return self._player_id


# TODO: [2022-11-21 15:40 burov_alexey@mail.ru]:
# Здесь сразу сделана и игровая реализация и будет и трэды. Я бы ботву
# с тредами здесь остваил, а игру реализоваывал бы уже в отельном модуле.
# Трэдовая реализация, а рядом абстрактные методы для реализации.


class ThreadedGameLayer(IGameLayer):
    """Игровой слой в отдельном трэде."""

    def __init__(
        self,
        entity_cls_by_name: dict[str, type[ClientGameEntity]],
        game_queue: Queue[QueueCallbackItem],
    ) -> None:
        self._entity_cls_by_name = entity_cls_by_name
        self._game_state = GameState()
        self._queue = game_queue

    # TODO: [2023-01-18 10:24 burov_alexey@mail.ru]:
    # Этот метод в каждом слое есть. Нужно разобраться и оставить только в одном.
    def call_in_game_thread(self, callback, args) -> None:
        item = QueueCallbackItem(callback, args)
        try:
            self._queue.put_nowait(item)
        except queue.Full as err:
            logger.error(
                "[%s] %s", self, devonly.func_args_values(), exc_info=True
            )
            # TODO: [2022-11-22 11:24 burov_alexey@mail.ru]:
            # Пока заваливать приложение, чтобы на отладке поймать подобную проблему
            raise SystemExit(err)

    def get_game_state(self) -> GameState:
        return self._game_state

    @cached_property
    def net(self) -> ThreadedNetLayer:
        return ilayer.get_net_layer()  # type: ignore

    def sync_layers(self, time_frame: float = settings.GAME_TICK) -> int:
        """Reads messages from the queue for the specified number of seconds.

        Returns the number of messages read.
        """
        net_frame = time_frame / 3
        consume_frame = time_frame / 3

        cntr = 0
        stop_sync_time = time.time() + time_frame
        while time.time() < stop_sync_time:
            # Из-за GIL нужно часть времени отдавать сетевому трэду, чтобы
            # он создал события, а затем уже потребить эти события.
            stop_consume_time = time.time() + consume_frame
            while time.time() < stop_consume_time:
                # Обязательно нужна блокировка, иначе на соседний трэд в обще
                # не переключится, если очередь пустая. Таймаут тоже нужен
                # обязательно, т.к. можно в тестах выхватить дэдлок (попасть
                # на пустою очередь от сервера, сервер ждёт от клиента
                # сообщение, а клиент может зависнуть в этой точке, ожидая
                # сообщения от сервера).
                try:
                    item = self._queue.get(block=True, timeout=net_frame)
                except Empty:
                    continue
                item.callback(*item.args)
                cntr += 1
            time.sleep(net_frame)

        return cntr

    # *** Сущность создана ***

    def call_entity_created(
        self, entity_id: int, entity_cls_name: str, is_player: bool
    ) -> None:
        """Сообщить, что сущность создана (вызов из сетевого трэда)."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self.call_in_game_thread(
            self._on_call_entity_created,
            (entity_id, entity_cls_name, is_player),
        )

    def _on_call_entity_created(
        self, entity_id: int, entity_cls_name: str, is_player: bool
    ) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        # TODO: [2026-02-10 20:02 burov_alexey@mail.ru]:
        # Это должна быть отдельна сущность EntityManager
        e_cls = self._entity_cls_by_name[entity_cls_name]
        entity = e_cls(entity_id, is_player, self.net)
        self._game_state.add_entity(entity)

    # *** Сущность уничтожена ***

    def call_entity_destroyed(self, entity_id: int) -> None:
        """Сущность уничтожена (вызов в сетевом трэде)."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self.call_in_game_thread(self._on_call_entity_destroyed, (entity_id,))

    def _on_call_entity_destroyed(self, entity_id: int) -> None:
        """Сущность уничтожена (вызов в игровом трэде)."""
        # TODO: [2022-11-18 12:57 burov_alexey@mail.ru]:
        # На начальных итерациях хватит и такого
        self._game_state.delete_entity(entity_id)

    # *** Вызов метода сущности ***

    def call_entity_method(
        self, entity_id: int, method_name: str, *args: list
    ) -> None:
        """Получен вызов удалённого метода (вызов в сетевом трэде)."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self.call_in_game_thread(
            self._on_call_entity_method, (entity_id, method_name, args)
        )

    def _on_call_entity_method(
        self, entity_id: int, method_name: str, *args: list
    ) -> None:
        """Получен вызов удалённого метода (вызов в игровом трэде)."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        entity = self._game_state.get_entity(entity_id)
        entity.__on_remote_call__(method_name, args)

    # *** Обновить свойства сущности ***

    def update_entity_properties(
        self, entity_id: int, properties: dict[str, Any]
    ) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self.call_in_game_thread(
            self._on_update_entity_properties, (entity_id, properties)
        )

    def _on_update_entity_properties(
        self, entity_id: int, properties: dict[str, Any]
    ) -> None:
        entity = self._game_state.get_entity(entity_id)
        entity.__on_update_properties__(properties)

    # *** Обновить свойства компонента-атрибута сущности ***

    def update_component_properties(
        self, entity_id: int, component_name: str, properties: dict[str, Any]
    ) -> None:
        self.call_in_game_thread(
            self._on_update_component_properties,
            (entity_id, component_name, properties),
        )

    def _on_update_component_properties(
        self, entity_id: int, component_name: str, properties: dict[str, Any]
    ) -> None:
        entity = self._game_state.get_entity(entity_id)
        entity.__on_update_component_properties__(component_name, properties)

    # *** Вызов метода компонента-атрибута сущности ***

    def call_component_method(
        self, entity_id: int, component_name: str, method_name: str, *args: list
    ) -> None:
        self.call_in_game_thread(
            self._on_call_component_method,
            (entity_id, component_name, method_name, args),
        )

    def _on_call_component_method(
        self, entity_id: int, component_name: str, method_name: str, *args: list
    ) -> None:
        entity = self._game_state.get_entity(entity_id)
        entity.__on_component_remote_call__(component_name, method_name, args)

    # *** Сообщает, что компонент привязался к сущности ***

    def call_component_onAttached(
        self, entity_id: int, component_name: str
    ) -> None:
        self.call_in_game_thread(
            self._on_call_component_onAttached, (entity_id, component_name)
        )

    def _on_call_component_onAttached(
        self, entity_id: int, component_name: str
    ) -> None:
        entity = self._game_state.get_entity(entity_id)
        entity.__on_component_remote_call__(
            component_name, "onAttached", (entity,)
        )

    """ Выставить Space Data значение """

    def call_set_space_data(self, space_id: int, key: str, value: str) -> None:
        self.call_in_game_thread(
            self._on_call_set_space_data, (space_id, key, value)
        )

    def _on_call_set_space_data(
        self, space_id: int, key: str, value: str
    ) -> None:
        self._game_state.space_data[space_id][key] = value

    """ Удалить Space Data значение """

    def call_delete_space_data(self, space_id: int, key: str) -> None:
        self.call_in_game_thread(
            self._on_call_delete_space_data, (space_id, key)
        )

    def _on_call_delete_space_data(self, space_id: int, key: str) -> None:
        # От сервера вызовы должны приходить без повреждения данных (т.е.
        # удаление не сущенствующего ключа не возможно)
        del self._game_state.space_data[space_id][key]

    """Ответы на различные действия."""

    def on_login(
        self,
        account_name: str,
        password: str,
        success: bool,
        ret_code: ServerError,
        reason: str,
    ) -> None:
        """Вызов в игровом трэде."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        if success:
            self._game_state.set_account_name(account_name, password)
            return

    def on_bind_account_email(self, success: bool, reason: str) -> None:
        """Вызов в игровом трэде."""
        logger.debug("[%s] %s", self, devonly.func_args_values())

    def on_create_account(
        self, success: bool, ret_code: ServerError, data: bytes, reason: str
    ) -> None:
        """Вызов в игровом трэде."""
        logger.debug("[%s] %s", self, devonly.func_args_values())

    def on_reset_password(self, success: bool, reason: str) -> None:
        """Вызов в игровом трэде."""
        logger.debug("[%s] %s", self, devonly.func_args_values())

    def on_set_new_password(self, success: bool, reason: str) -> None:
        """Вызов в игровом трэде."""
        logger.debug("[%s] %s", self, devonly.func_args_values())


class ThreadedNetLayer(INetLayer):
    """Сетевой слой.

    Его колбэки срабатывают в трэде с event loop.
    """

    def __init__(
        self,
        app: ClientApp,
        loop: AbstractEventLoop,
        queue: Queue[QueueCallbackItem],
    ) -> None:
        self._clientapp = app
        # Эта петля запущена в отдельном сетевом трэде. Ссылка на неё
        # используется в игровом трэде для отправки из игрового трэда
        # в сетевой вызовов.
        self._loop = loop
        # Очередь нужна для отправки вызовов из сетевого треда с loop в игровой
        # тред.
        self._queue = queue

    @cached_property
    def game(self) -> ThreadedGameLayer:
        return ilayer.get_game_layer()  # type: ignore

    def call_in_game_thread(self, callback, args) -> None:
        item = QueueCallbackItem(callback, args)
        try:
            self._queue.put_nowait(item)
        except queue.Full as err:
            logger.error("[%s] %s", self, devonly.func_args_values())
            # TODO: [2022-11-22 11:24 burov_alexey@mail.ru]:
            # Пока заваливать приложение, чтобы на отладке поймать подобную проблему
            raise SystemExit(err)

    def call_entity_remote_method(
        self,
        entity_cls_name: str,
        entity_id: int,
        kbe_component: KBEComponentEnum,
        method_name: str,
        args: tuple,
    ) -> None:
        """Вызывает на стороне игрового трэда (колбэк будет вызван в сетевом трэде)."""
        asyncio.run_coroutine_threadsafe(
            self._on_call_entity_remote_method(
                entity_cls_name, entity_id, kbe_component, method_name, args
            ),
            self._loop,
        )

    async def _on_call_entity_remote_method(
        self,
        entity_cls_name: str,
        entity_id: int,
        kbe_component: KBEComponentEnum,
        method_name: str,
        args: tuple,
    ) -> None:
        """Колбэк, вызванный в сетевом трэде."""
        entity_rpc_serializer = self._eserializer_by_name[entity_cls_name]
        method: Callable
        if kbe_component == KBEComponentEnum.BASE:
            method = getattr(entity_rpc_serializer.base, method_name)
        else:
            method = getattr(entity_rpc_serializer.cell, method_name)

        msg: Message = method(entity_id, *args)

        self._clientapp.baseapp_client.send_message(msg)

    """Сделать удалённый вызов компонентета."""

    def call_component_remote_method(
        self,
        entity_cls_name: str,
        entity_id: int,
        kbe_component: KBEComponentEnum,
        owner_attr_name: str,
        method_name: str,
        args: tuple,
    ) -> None:
        asyncio.run_coroutine_threadsafe(
            self._on_call_component_remote_method(
                entity_cls_name,
                entity_id,
                kbe_component,
                owner_attr_name,
                method_name,
                args,
            ),
            self._loop,
        )

    async def _on_call_component_remote_method(
        self,
        entity_cls_name: str,
        entity_id: int,
        kbe_component: KBEComponentEnum,
        owner_attr_name: str,
        method_name: str,
        args: tuple,
    ) -> None:
        """Вызов в сетевом трэде."""
        serializer: IEntityRPCSerializer = self._eserializer_by_name[
            entity_cls_name
        ]
        comp_serializer = serializer.get_component_by_name(owner_attr_name)
        if kbe_component == KBEComponentEnum.BASE:
            method: Callable = getattr(comp_serializer.base, method_name)
        else:
            method: Callable = getattr(comp_serializer.cell, method_name)
        msg: Message = method(entity_id, *args)
        self._clientapp.send_message(msg)

    """Залогиниться на игровом сервере."""

    def call_login(self, username: str, password: str) -> None:
        """Вызов в игровом трэде."""
        asyncio.run_coroutine_threadsafe(
            self._on_call_login(username, password), self._loop
        )

    async def _on_call_login(self, username: str, password: str) -> None:
        """Вызов в сетевом трэде."""
        try:
            res = await self._clientapp.loginapp_client.get_baseapp_address(
                client_type=ClientType.UNKNOWN,
                client_data=b"",
                account_name=username,
                password=password,
                entitydefs_hash=settings.ENTITYDEFS_HASH,
                force_login=True,
            )
        except LoginappConnectionError as err:
            self.call_in_game_thread(
                self.game.on_login,
                (username, password, False, ServerError.MAX, str(err.args)),
            )
            return

        if not res.success:
            self.call_in_game_thread(
                self.game.on_login,
                (username, password, False, res.result.ret_code, res.text),
            )
            return

        assert res.result.baseapp_tcp_addr is not None

        self._clientapp.create_baseapp_client(res.result.baseapp_tcp_addr)
        try:
            login_res = await self._clientapp.baseapp_client.login(
                username, password
            )
        except BaseappConnectionError as err:
            self.call_in_game_thread(
                self.game.on_login,
                (username, password, False, ServerError.MAX, str(err.args)),
            )
            return

        if not login_res.success:
            self.call_in_game_thread(
                self.game.on_login,
                (username, password, False, res.result.ret_code, res.text),
            )
            return

        self.call_in_game_thread(
            self.game.on_login,
            (username, password, True, res.result.ret_code, res.text),
        )

    """Создать аккаунт."""

    def call_create_account(self, username: str, password: str) -> None:
        """Вызов в игровом трэде."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        asyncio.run_coroutine_threadsafe(
            self._on_call_create_account(username, password), self._loop
        )

    async def _on_call_create_account(
        self, username: str, password: str
    ) -> None:
        """Вызов в сетевом трэде."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        assert not self._clientapp.is_started

        # Непонятно, что за данные здесь должны быть
        data = b""
        res = await self._clientapp.loginapp_client.create_account(
            username, password, data
        )

        self.call_in_game_thread(
            self.game.on_create_account,
            (res.success, res.result.ret_code, res.result.data, res.text),
        )

    """Скинуть пароль."""

    def call_reset_password(self, username: str) -> None:
        """Вызов в игровом трэде."""
        asyncio.run_coroutine_threadsafe(
            self._on_call_reset_password(username), self._loop
        )

    async def _on_call_reset_password(self, username: str) -> None:
        """Вызов в сетевом трэде."""
        res = await self._clientapp.reset_password(username)
        self.call_in_game_thread(
            self.game.on_reset_password, (res.success, res.text)
        )

    """Привязать попробовать email к аккаунту."""

    def call_bind_account_email(
        self, entity_id: int, password: str, email: str
    ) -> None:
        """Вызов в игровом трэде."""
        asyncio.run_coroutine_threadsafe(
            self._on_call_bind_account_email(entity_id, password, email),
            self._loop,
        )

    async def _on_call_bind_account_email(
        self, entity_id: int, password: str, email: str
    ) -> None:
        """Вызов в сетевом трэде."""
        res = await self._clientapp.bind_account_email(
            entity_id, password, email
        )
        self.call_in_game_thread(
            self.game.on_bind_account_email, (res.success, res.text)
        )

    """Задать новый пароль."""

    def call_set_new_password(
        self, entity_id: int, oldpassword: str, newpassword: str
    ) -> None:
        """Вызов в игровом трэде."""
        asyncio.run_coroutine_threadsafe(
            self._on_call_set_new_password(entity_id, oldpassword, newpassword),
            self._loop,
        )

    async def _on_call_set_new_password(
        self, entity_id: int, oldpassword: str, newpassword: str
    ) -> None:
        """Вызов в сетевом трэде."""
        res = await self._clientapp.set_new_password(
            entity_id, oldpassword, newpassword
        )
        self.call_in_game_thread(
            self.game.on_set_new_password, (res.success, res.text)
        )
