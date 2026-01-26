"""The module contains classes working with communication messages."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final, TypeAlias

from enki.kbeenum import ComponentType  # noqa: TC001
from enki.kbetype.ikbetype import IKBEType

from .msg_descr import MsgId

if TYPE_CHECKING:
    from .msg_descr import MsgDescr, MsgName

logger = logging.getLogger(__name__)


MsgValues: TypeAlias = tuple[IKBEType, ...]


class Message:
    """Сообщение KBEngine для общения между компонентами.

    Это id сообщения и последовательность значений.
    """

    NO_ID: Final[MsgId] = MsgId(0)

    @classmethod
    def create(cls, msg_descr: MsgDescr, values: MsgValues) -> Message:
        """Создать сообщение на основе его описания.

        Args:
            msg_descr (MsgDescr): описание сообщения

        Returns:
            Message: новый объект сообщения

        """
        assert len(msg_descr.args) == len(values), "Not enough values"
        return Message(
            msg_id=msg_descr.id,
            name=msg_descr.name,
            comp=msg_descr.component_type,
            values=values,
        )

    def __init__(
        self,
        msg_id: MsgId,
        name: MsgName,
        comp: ComponentType,
        values: MsgValues,
    ) -> None:
        """Конструктор.

        Args:
            msg_id (MsgID): id сообщения
            name (MsgName): имя сообщения
            comp (ComponentType): компонент получатель сообщения
            values (MsgValues): последовательность значений сообщения

        """
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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Message):
            return False

        return (
            self.name == other.name
            and self.id == other.id
            and self.component == other.component
        )

    def __hash__(self) -> int:
        return hash(str(self))

    def __str__(self) -> str:
        cls_name = self.__class__.__name__
        return f"{cls_name}(id={self.id}, name={self.name})"

    __repr__ = __str__
