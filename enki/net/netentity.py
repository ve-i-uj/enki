"""The entity parent class."""

from __future__ import annotations

import abc
import logging

logger = logging.getLogger(__name__)


class IRPCSerializer(abc.ABC):
    """Сериализатор для вызова удалённых методов сущности."""

    @abc.abstractmethod
    def send_remote_call_msg(self, msg):
        """Отправить сообщение вызова метода на серверном компоненте сущности."""
        pass


class IBaseERPCSerializer(IRPCSerializer):
    """Interface for the class can serialize remote calls to the base entity."""
    pass


class ICellERPCSerializer(IRPCSerializer):
    """Interface for the class can serialize remote calls to the cell entity."""
    pass


class IComponentERPCSerializer(IRPCSerializer):
    """Interface for the class can serialize remote calls to the entity component."""
    pass


# TODO: [2022-11-09 07:40 burov_alexey@mail.ru]:
# Эту штуку как-то нужно применить в сгенерированном сетевом коде (сущностей сериализаторов).
class IEntityRPCSerializer(IRPCSerializer):
    """Её [сгененированные] потомки будут иметь методы сериализация удалённого вызова."""

    @property
    @abc.abstractmethod
    def cell(self) -> ICellERPCSerializer:
        pass

    @property
    @abc.abstractmethod
    def base(self) -> IBaseERPCSerializer:
        pass
