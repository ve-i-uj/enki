"""The Machine component мessages (not generated)."""

from enki.core import kbeenum
from enki.core import kbetype
from enki.core.message import MsgDescr


onStopComponent = MsgDescr(
    id=21001,
    lenght=10,
    name='Supervisor::onStopComponent',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
        kbetype.COMPONENT_ID  # этого скорей всего полностью достаточно
    ]),
    desc='Уведомление, что компонент начал останавливаться'
)

SPEC_BY_ID = {
    onStopComponent.id: onStopComponent,
}

__all__ = [
    'SPEC_BY_ID',

    'onStopComponent',
]
