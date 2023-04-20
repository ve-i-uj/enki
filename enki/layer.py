"""Класс для коммуникации между разными игровыми слоями.

Инкапсулирует межтредовое взаимодействие.
"""

from __future__ import annotations

import abc
import enum
import logging
from typing import Any

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


class _ILayer(abc.ABC):
    """Инкапсулирует передачу вызовов между разными слоями приложения.

    Методы этого интерфейса можно вызывать из соседнего слоя,
    который может находиться в соседнем трэде или процессе.

    В данном игровом плагине код чётко разделяется на 1) сетевой функционал сетевого
    взаимодействия (сереиализация, адреса и порты, подключения) и 2) функицонал
    игровой логики (игровые сущности, реднер, UI). Каждый из этих компонентов
    игрового плагина - это слой: сетевой и игровой. Интерфейс взаимодействия
    между слоями определён в этом модуле.

    Взаимодействие между слоями (т.е. все методы обоих слоёв) полностью на
    типах Python.

    Слоёв в запущенной игре всего 2: сетевой и игровой - они сиглтоны.

    Принцип следующий: в своём слое берётся ссылка на другой слой. У другого
    слоя вызывается метод не начинающийся на "on_". Метод с тем же названием,
    но с приставкой "on_" вызывается в другом слое. Другой слой может
    находиться в другом потоке, процессе или компьютере - это уже вопрос реализации.
    """
    pass


class IGameLayer(_ILayer):
    """Игровой слой.

    Это взаимодействие из сетевого слоя в игровой.
    """

    @property
    @abc.abstractmethod
    def net(self) -> INetLayer:
        """Ссылка на сетевой слой."""
        pass

    # *** Обновить свойства сущности ***

    @abc.abstractmethod
    def update_entity_properties(self, entity_id: int, properties: dict[str, Any]):
        pass

    @abc.abstractmethod
    def on_update_entity_properties(self, entity_id: int, properties: dict[str, Any]):
        pass

    # *** Обновить свойства компонента-атрибута сущности ***

    @abc.abstractmethod
    def update_component_properties(self, entity_id: int, component_name: str,
                                    properties: dict[str, Any]):
        pass

    @abc.abstractmethod
    def on_update_component_properties(self, entity_id: int, component_name: str,
                                       properties: dict[str, Any]):
        pass

    # *** Вызов метода сущности ***

    @abc.abstractmethod
    def call_entity_method(self, entity_id: int, method_name: str, *args: list):
        pass

    @abc.abstractmethod
    def on_call_entity_method(self, entity_id: int, method_name: str, *args: list):
        pass

    # *** Вызов метода компонента-атрибута сущности ***

    @abc.abstractmethod
    def call_component_method(self, entity_id: int, component_name: str,
                              method_name: str, *args: list):
        pass

    @abc.abstractmethod
    def on_call_component_method(self, entity_id: int, component_name: str,
                                 method_name: str, *args: list):
        pass

    # *** Сущность уничтожена ***

    @abc.abstractmethod
    def call_entity_destroyed(self, entity_id: int):
        pass

    @abc.abstractmethod
    def on_call_entity_destroyed(self, entity_id: int):
        pass

    # *** Сущность создана ***

    @abc.abstractmethod
    def call_entity_created(self, entity_id: int, entity_cls_name: str, is_player: bool):
        pass

    @abc.abstractmethod
    def on_call_entity_created(self, entity_id: int, entity_cls_name: str, is_player: bool):
        pass

    # *** Сообщает, что компонент привязался к сущности ***

    @abc.abstractmethod
    def call_component_onAttached(self, entity_id: int, component_name: str):
        pass

    @abc.abstractmethod
    def on_call_component_onAttached(self, entity_id: int, component_name: str):
        pass

    """ Выставить Space Data значение """

    @abc.abstractmethod
    def call_set_space_data(self, space_id: int, key: str, value: str):
        pass

    @abc.abstractmethod
    def on_call_set_space_data(self, space_id: int, key: str, value: str):
        pass

    """ Удалить Space Data значение """

    @abc.abstractmethod
    def call_delete_space_data(self, space_id: int, key: str):
        pass

    @abc.abstractmethod
    def on_call_delete_space_data(self, space_id: int, key: str):
        pass

    """Ответы на игровый действия."""

    @abc.abstractmethod
    def on_login(self, account_name: str, password: str, success: bool, reason: str):
        """Ответ на попытку подключения."""
        pass

    @abc.abstractmethod
    def on_create_account(self, success: bool, reason: str):
        """Ответ на создание аккаунта."""
        pass

    @abc.abstractmethod
    def on_reset_password(self, success: bool, reason: str):
        """Ответ на сброс пароля."""
        pass

    @abc.abstractmethod
    def on_bind_account_email(self, success: bool, reason: str):
        """Ответ на привязку email к аккаунту."""
        pass

    @abc.abstractmethod
    def on_set_new_password(self, success: bool, reason: str):
        """Ответ на выставление нового пароля."""
        pass

    """ **** """

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'

class INetLayer(_ILayer):
    """Интерфейс сетевого слоя."""

    """Вызвать сетевой удалённый метод у сущности."""

    @abc.abstractmethod
    def call_entity_remote_method(self, entity_cls_name: str, entity_id: int,
                                  kbe_component: KBEComponentEnum,
                                  method_name: str, args: tuple):
        pass

    @abc.abstractmethod
    def on_call_entity_remote_method(self, entity_cls_name: str, entity_id: int,
                                     kbe_component: KBEComponentEnum,
                                     method_name: str, args: tuple):
        pass

    """Вызвать сетевой удалённый метод у компонента сущности."""

    @abc.abstractmethod
    def call_component_remote_method(self, entity_cls_name: str, entity_id: int,
                                     kbe_component: KBEComponentEnum,
                                     owner_attr_name: str, method_name: str, args: tuple):
        pass

    @abc.abstractmethod
    def on_call_component_remote_method(self, entity_cls_name: str, entity_id: int,
                                        kbe_component: KBEComponentEnum,
                                        owner_attr_name: str, method_name: str, args: tuple):
        pass

    """Залогиниться на игровом сервере."""

    @abc.abstractmethod
    def call_login(self, username: str, password: str):
        pass

    @abc.abstractmethod
    def on_call_login(self, username: str, password: str):
        pass

    """Создать аккаунт."""

    @abc.abstractmethod
    def call_create_account(self, username: str, password: str):
        pass

    @abc.abstractmethod
    def on_call_create_account(self, username: str, password: str):
        pass

    """Скинуть пароль."""

    @abc.abstractmethod
    def call_reset_password(self, username: str):
        pass

    @abc.abstractmethod
    def on_call_reset_password(self, username: str):
        pass

    """Привязать попробовать email к аккаунту."""

    @abc.abstractmethod
    def call_bind_account_email(self, entity_id: int, password: str, email: str):
        pass

    @abc.abstractmethod
    def on_call_bind_account_email(self, entity_id: int, account_name: str, email: str):
        pass

    """Задать новый пароль."""

    @abc.abstractmethod
    def call_set_new_password(self, entity_id: int, oldpassword: str, newpassword: str):
        pass

    @abc.abstractmethod
    def on_call_set_new_password(self, entity_id: int, oldpassword: str, newpassword: str):
        pass

    """ **** """

    @property
    @abc.abstractmethod
    def game(self) -> IGameLayer:
        """Ссылка на игровой слой."""
        pass

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'


# _net_layer: INetLayer
# _game_layer: IGameLayer

def init(net_layer: INetLayer, game_layer: IGameLayer):
    """Соединить два слоя (означает, что игра готова к приёму сообщений).

    Нужно до запуска приложения запустить этот метод, т.к. слои нужны только
    в рантайме, иначе в связьях объектов будут циклы.
    """
    global _net_layer, _game_layer
    _net_layer = net_layer
    _game_layer = game_layer


def get_net_layer() -> INetLayer:
    return _net_layer


def get_game_layer() -> IGameLayer:
    return _game_layer
