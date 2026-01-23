"""Утилиты этого пакета."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from enki import msgspec
from enki.msg.msg_serializer import MessageSerializer

if TYPE_CHECKING:
    from enki.kbeenum import ComponentType

logger = logging.getLogger(__name__)


def get_serializer(comp_type: ComponentType) -> MessageSerializer:
    """Возвращает сериализатор сообщения в зависимовсти от типа компонента.

    Args:
        comp_type (ComponentType): тип компонента

    Returns:
        MessageSerializer: сериализатор сообщений

    """
    comp_msg_specs = msgspec.get_comp_msg_specs(comp_type)
    return MessageSerializer(comp_msg_specs)
