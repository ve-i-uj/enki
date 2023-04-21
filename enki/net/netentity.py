"""The entity parent class."""

from __future__ import annotations

import abc
import logging
from typing import ClassVar

from enki import settings
from enki.net.kbeclient import Message, Client

logger = logging.getLogger(__name__)


class IRPCSerializer(abc.ABC):
    """Сериализатор для вызова удалённых методов сущности."""


class _EntityCellBaseRPCSerializer(IRPCSerializer):
    pass


class EntityBaseRPCSerializer(_EntityCellBaseRPCSerializer):
    """Class for the class can serialize remote calls to the base entity."""


class EntityCellRPCSerializer(_EntityCellBaseRPCSerializer):
    """Class for the class can serialize remote calls to the cell entity."""


class IEntityRPCSerializer(IRPCSerializer):
    """Её [сгененированные] потомки будут иметь методы для сериализации удалённого вызова."""

    @property
    def ENTITY_CLS_ID(self) -> ClassVar[int]:
        return None


    @property
    @abc.abstractmethod
    def cell(self) -> EntityCellRPCSerializer:
        pass

    @property
    @abc.abstractmethod
    def base(self) -> EntityBaseRPCSerializer:
        pass

    @abc.abstractmethod
    def get_component_by_name(self, name: str) -> EntityComponentRPCSerializer:
        pass


class _EntityComponentBaseCellRPCSerializer(IRPCSerializer):

    def __init__(self, ec_serializer: EntityComponentRPCSerializer) -> None:
        self._ec_serializer = ec_serializer


class EntityComponentCellRPCSerializer(_EntityComponentBaseCellRPCSerializer):
    pass


class EntityComponentBaseRPCSerializer(_EntityComponentBaseCellRPCSerializer):
    pass


class EntityComponentRPCSerializer(IRPCSerializer):
    """Interface for the class can serialize remote calls to the entity component."""

    def __init__(self, owner_attr_id: int) -> None:
        self._owner_attr_id = owner_attr_id

        self._cell = EntityComponentCellRPCSerializer(self)
        self._base = EntityComponentBaseRPCSerializer(self)

    @property
    def owner_attr_id(self) -> int:
        """Возвращает id свойсва сущности (из сгенерированного описания).

        В этом свойство сущности будет ссылать на экземпляр этого класса
        (с этим owner_attr_id). "owner_attr_id" динамически задаётся на сервере
        в зависимости от места расположения свойства в enities_def.
        """
        return self._owner_attr_id

    @property
    def cell(self) -> EntityComponentCellRPCSerializer:
        return self._cell

    @property
    def base(self) -> EntityComponentBaseRPCSerializer:
        return self._base
