"""The module contains classes working with communication messages."""

from __future__ import annotations

import logging
from typing import Final, TypeAlias

from enki.kbeenum import ComponentType  # noqa: TC001
from enki.kbetype.ikbetype import IKBEType

logger = logging.getLogger(__name__)


MsgId: TypeAlias = int
MsgName: TypeAlias = str
MsgValues: TypeAlias = tuple[IKBEType, ...]


class Message:
    """Сообщение KBEngine для общения между компонентами.

    Это id сообщения и последовательность значений. Сообщения соответствует
    протоколу, фиксированному в файле messages_fixed_defaults.xml .
    """

    NO_ID: Final[MsgId] = 0

    def __init__(
        self, msg_id: MsgId, name: MsgName, comp: ComponentType, values: MsgValues
    ) -> None:
        """Конструктор.

        Args:
            msg_id (MsgID): id сообщения
            name (MsgName): имя сообщения
            comp (ComponentType): компонент получатель сообщения
            values (MsgValues): последовательность значений сообщения

        """
        assert name.split(":")[0].capitalize() == comp.name, (
            "The message name and the component type are different"
        )

        self._msg_id = msg_id
        self._name = name
        self._comp = comp
        self._values = values

    @property
    def id(self) -> MsgId:
        """Message id (see messages_fixed_defaults.xml)."""
        return self._msg_id

    @property
    def name(self) -> MsgName:
        """Имя сообщения."""
        return self._name

    @property
    def component(self) -> ComponentType:
        """Компонент-получатель сообщения."""
        return self._comp

    def get_values(self) -> MsgValues:
        """Return values of message fields.

        Returns:
            MsgValues: значения полей сообщения

        """
        return tuple(self._values)

    def __str__(self) -> str:
        cls_name = self.__class__.__name__
        return f"{cls_name}(id={self.id}, name={self.name})"

    __repr__ = __str__


OptionalMessage: TypeAlias = Message | None
