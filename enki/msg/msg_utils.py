"""Утилиты этого пакета."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from enki import msgspec
from enki.msg.msg_serializer import MessageSerializer

if TYPE_CHECKING:
    from enki.kbeenum import ComponentType

logger = logging.getLogger(__name__)


class NoSerializerForComponentError(RuntimeError):
    """Исключение в случае, если для нужного компонента нет сериализатора."""


def get_serializer(component: ComponentType) -> MessageSerializer:
    """Возвращает сериализатор сообщения в зависимовсти от типа компонента.

    Args:
        component (ComponentType): тип компонента

    Raises:
        NoSerializerForComponentError: если для нужного компонента нет
            сериализатора

    Returns:
        MessageSerializer: сериализатор сообщений

    """
    comp_msg_specs = msgspec.MSG_SPEC_BY_COMPONENT.get(component)
    if comp_msg_specs is not None:
        return MessageSerializer(comp_msg_specs)

    err_msg = f"There is no serializator for the component '{component.name}'"
    logger.error("%s (Logic error)", err_msg)
    raise NoSerializerForComponentError(err_msg)
