"""The entity parent class."""

from __future__ import annotations

import abc
import logging

from enki import settings
from enki.net.kbeclient import Message, Client

logger = logging.getLogger(__name__)


class IRPCSerializer(abc.ABC):
    """Сериализатор для вызова удалённых методов сущности."""

    @abc.abstractmethod
    def send_remote_call_msg(self, msg: Message):
        """Отправить сообщение вызова метода на серверном компоненте сущности."""
        pass


class _EntityCellBaseRPCSerializer(IRPCSerializer):

    def __init__(self, e_serializer: IEntityRPCSerializer) -> None:
        self._e_serializer = e_serializer

    def send_remote_call_msg(self, msg: Message):
        self._e_serializer.send_remote_call_msg(msg)


class EntityBaseRPCSerializer(_EntityCellBaseRPCSerializer):
    """Class for the class can serialize remote calls to the base entity."""


class EntityCellRPCSerializer(_EntityCellBaseRPCSerializer):
    """Class for the class can serialize remote calls to the cell entity."""


class IEntityRPCSerializer(IRPCSerializer):
    """Её [сгененированные] потомки будут иметь методы сериализация удалённого вызова."""

    @property
    @abc.abstractmethod
    def ENTITY_CLS_ID(self) -> int:
        """Будет захардкожено в сгенерированном наследнике."""
        return settings.NO_ENTITY_CLS_ID

    @property
    @abc.abstractmethod
    def cell(self) -> EntityCellRPCSerializer:
        pass

    @property
    @abc.abstractmethod
    def base(self) -> EntityBaseRPCSerializer:
        pass


class _EntityComponentBaseCellRPCSerializer(IRPCSerializer):

    def __init__(self, ec_serializer: EntityComponentRPCSerializer) -> None:
        self._ec_serializer = ec_serializer

    def send_remote_call_msg(self, msg: Message):
        self._ec_serializer.send_remote_call_msg(msg)


class EntityComponentCellRPCSerializer(_EntityComponentBaseCellRPCSerializer):
    pass


class EntityComponentBaseRPCSerializer(_EntityComponentBaseCellRPCSerializer):
    pass


class EntityComponentRPCSerializer(IRPCSerializer):
    """Interface for the class can serialize remote calls to the entity component."""

    def __init__(self, e_serializer: IEntityRPCSerializer, owner_attr_id: int) -> None:
        self._e_serializer = e_serializer
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

    def send_remote_call_msg(self, msg: Message):
        self._e_serializer.send_remote_call_msg(msg)
