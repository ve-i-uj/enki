"""Родительские классы для сериализаторов сущностей."""

from __future__ import annotations

import abc
import logging
from typing import ClassVar, TypeAlias

from enki.novalue import NoValue

logger = logging.getLogger(__name__)

# Этот id задаётся по порядковому номеру entities.xml
EntityTypeId: TypeAlias = int
EntityComponentName: TypeAlias = str
EntityPropertyId: TypeAlias = int


class IRPCSerializer(abc.ABC):  # noqa: B024
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
    @abc.abstractmethod
    def cell(self) -> EntityCellRPCSerializer:
        """Возвращает сериализатор для RPC к cell-сущности."""

    @property
    @abc.abstractmethod
    def base(self) -> EntityBaseRPCSerializer:
        """Возвращает сериализатор для RPC к base-сущности."""

    @abc.abstractmethod
    def get_component_by_name(
        self, name: EntityComponentName
    ) -> EntityComponentRPCSerializer:
        """Возвращает сериализатор компонента сущности по имени."""


class _EntityComponentBaseCellRPCSerializer(IRPCSerializer):
    """Базовый класс для сериализаторов компонента сущности (base и cell)."""

    def __init__(self, ec_serializer: EntityComponentRPCSerializer) -> None:
        """Инициализирует сериализатор компонента сущности.

        Args:
            ec_serializer: сериализатор связанного компонента сущности

        """
        self._ec_serializer = ec_serializer


class EntityComponentCellRPCSerializer(_EntityComponentBaseCellRPCSerializer):
    """Сериализатор для cell части компонента сущности."""


class EntityComponentBaseRPCSerializer(_EntityComponentBaseCellRPCSerializer):
    """Сериализатор для baase части компонента сущности."""


class EntityComponentRPCSerializer(IRPCSerializer):
    """Родительский класс для сериализаторов RPC компонента-сущности."""

    def __init__(self, owner_attr_id: EntityPropertyId) -> None:
        """Инициализирует сериализатор компонента сущности.

        Args:
            owner_attr_id: ID свойства сущности, которому принадлежит компонент

        """
        self._owner_attr_id = owner_attr_id

        self._cell = EntityComponentCellRPCSerializer(self)
        self._base = EntityComponentBaseRPCSerializer(self)

    @property
    def owner_attr_id(self) -> EntityPropertyId:
        """Возвращает id свойсва сущности (из сгенерированного описания).

        "owner_attr_id" динамически задаётся на сервере
        в зависимости от места расположения свойства в enities_def.
        """
        return self._owner_attr_id

    @property
    def cell(self) -> EntityComponentCellRPCSerializer:
        """Возвращает сериализатор для cell части компонента сущности."""
        return self._cell

    @property
    def base(self) -> EntityComponentBaseRPCSerializer:
        """Возвращает сериализатор для base части компонента сущности."""
        return self._base
