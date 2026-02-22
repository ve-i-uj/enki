"""Родительские классы для сериализаторов сущностей."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar, TypeAlias

from enki.novalue import NoValue

if TYPE_CHECKING:
    from enki.kbetype import KBEUInt16

logger = logging.getLogger(__name__)

# Этот id задаётся по порядковому номеру entities.xml
EntityTypeId: TypeAlias = int
EntityComponentName: TypeAlias = str


class IRPCSerializer(ABC):  # noqa: B024
    """Сериализатор для вызова удалённых методов сущности."""


class _EntityCellBaseRPCSerializer(IRPCSerializer):
    """Базовый класс для сериализаторов вызовов на cell и base."""


class EntityBaseRPCSerializer(_EntityCellBaseRPCSerializer):
    """Сериализатор RPC к base-состовляющей сущности."""


class EntityCellRPCSerializer(_EntityCellBaseRPCSerializer):
    """Сериализатор RPC к cell-состовляющей сущности."""


class IEntityRPCSerializer(IRPCSerializer):
    """Интерфейс для сериалзитора RPC-сущности.

    Её [сгененированные по entity_defs] потомки будут иметь методы для
    сериализации удалённого вызова.
    """

    ENTITY_CLS_ID: ClassVar[EntityTypeId] = NoValue.NO_ENTITY_CLS_ID

    @property
    @abstractmethod
    def cell(self) -> EntityCellRPCSerializer:
        """Возвращает сериализатор для RPC к cell-сущности."""

    @property
    @abstractmethod
    def base(self) -> EntityBaseRPCSerializer:
        """Возвращает сериализатор для RPC к base-сущности."""

    @abstractmethod
    def get_component_by_name(
        self, name: EntityComponentName
    ) -> IEntityComponentRPCSerializer:
        """Возвращает сериализатор компонента сущности по имени."""


class _EntityComponentBaseCellRPCSerializer(IRPCSerializer):
    """Базовый класс для сериализаторов компонента сущности (base и cell)."""

    def __init__(self, ec_serializer: IEntityComponentRPCSerializer) -> None:
        """Инициализирует сериализатор компонента сущности.

        Args:
            ec_serializer: сериализатор связанного компонента сущности

        """
        self._ec_serializer = ec_serializer


class EntityComponentCellRPCSerializer(_EntityComponentBaseCellRPCSerializer):
    """Сериализатор для cell части компонента сущности."""


class EntityComponentBaseRPCSerializer(_EntityComponentBaseCellRPCSerializer):
    """Сериализатор для base части компонента сущности."""


class IEntityComponentRPCSerializer(IRPCSerializer):
    """Родительский класс для сериализаторов RPC компонента-сущности."""

    def __init__(self, owner_attr_id: KBEUInt16) -> None:
        """Инициализирует сериализатор компонента сущности.

        Args:
            owner_attr_id: ID свойства сущности, которому принадлежит компонент

        """
        self._owner_attr_id = owner_attr_id

        # Пример:
        # self._cell = EntityComponentCellRPCSerializer(self)
        # self._base = EntityComponentBaseRPCSerializer(self)

    @property
    def owner_attr_id(self) -> KBEUInt16:
        """Возвращает id свойсва сущности (из сгенерированного описания).

        "owner_attr_id" динамически задаётся на сервере
        в зависимости от места расположения свойства в enities_def.
        """
        return self._owner_attr_id

    @property
    @abstractmethod
    def cell(self) -> EntityComponentCellRPCSerializer:
        """Возвращает сериализатор для cell части компонента сущности."""

    @property
    @abstractmethod
    def base(self) -> EntityComponentBaseRPCSerializer:
        """Возвращает сериализатор для base части компонента сущности."""
