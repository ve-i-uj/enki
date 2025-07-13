"""Сообщения компонента Supervisor."""

from enki.kbetype.decoders.custom_decoders import (
    COMPONENT_ID,
)
from enki.msg.msg_descr import FIXED, MsgDescr

onStopComponent = MsgDescr(  # noqa: N816
    id=21001,
    lenght=10,
    name="Supervisor::onStopComponent",
    args_type=FIXED,
    args=(COMPONENT_ID,),  # этого скорей всего полностью достаточно
    desc="Уведомление, что компонент начал останавливаться",
)

SPEC_BY_ID = {
    onStopComponent.id: onStopComponent,
}

__all__ = [
    "SPEC_BY_ID",
    "onStopComponent",
]
