"""The module contains classes working with communication messages."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import IntEnum
from typing import TypeAlias

from enki.kbeenum import ComponentType
from enki.kbetype.decoders.basic_data_type_decoders import *

logger = logging.getLogger(__name__)

MsgId: TypeAlias = int
MsgLenght: TypeAlias = int
MsgName: TypeAlias = str


class MsgArgsType(IntEnum):
    """Fixed or variable length of message (see MESSAGE_ARGS_TYPE)."""

    VARIABLE = -1
    FIXED = 0


VARIABLE = MsgArgsType.VARIABLE
FIXED = MsgArgsType.FIXED

MsgArgTypeDecoder: TypeAlias = (
    UINT8_ARRAY \
    | BOOL \
    | BLOB \
    | DOUBLE \
    | ENTITYCALL \
    | FLOAT \
    | INT8 \
    | INT16 \
    | INT32 \
    | INT64 \
    | KBE_DATATYPE2ID_MAX \
    | PYTHON \
    | PY_DICT \
    | PY_LIST \
    | PY_TUPLE \
    | STRING \
    | UINT8 \
    | UINT16 \
    | UINT32 \
    | UINT64 \
    | UNICODE \
    | VECTOR2 \
    | VECTOR3 \
    | VECTOR4
)

@dataclass(frozen=True)
class MsgDescr:
    """Specification of a message (see messages_fixed_defaults.xml)."""

    id: MsgId
    lenght: MsgLenght
    name: MsgName
    args_type: MsgArgsType
    # Типы закодированных данных
    # args: tuple[type[IKBETypeDecoder], ...] # pyright: ignore[reportMissingTypeArgument]
    args: tuple[type[MsgArgTypeDecoder], ...]
    desc: str

    @property
    def short_name(self) -> str:
        """Имя сообщения без имени компонента."""
        return self.name.split("::")[1]

    @property
    def component_type(self) -> ComponentType:
        """Компонент, которому пренадлежит сообщение."""
        comp_name = self.name.split("::")[0]
        return getattr(ComponentType, comp_name.upper())

    @property
    def is_length_calculation_needed(self) -> bool:
        """Нужно ли считывать длину сообщения."""
        return self.lenght == -1

    @property
    def is_a_short_message(self) -> bool:
        """It is a short message.

        Only message id, there is no payload.
        """
        return self.args_type == MsgArgsType.FIXED and not self.args


MsgSpecById: TypeAlias = dict[MsgId, MsgDescr]


@dataclass
class ComponentMsgSpecById:
    """Спецификации KBEngine-сообщений конкретного компонента."""

    component: ComponentType
    msg_spec_by_id: MsgSpecById


CompenentMsgSpecs: TypeAlias = dict[ComponentType, ComponentMsgSpecById]
