"""The DBMgr component мessages (not generated)."""

from enki.core import kbeenum
from enki.core import kbetype
from enki.core.message import MsgDescr


onAppActiveTick = MsgDescr(
    id=55102,
    lenght=12,
    name='CellappMgr::onAppActiveTick',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
        kbetype.COMPONENT_TYPE,  # componentType
        kbetype.COMPONENT_ID,  # componentID
    ]),
    desc='Компонент сообщает, что он живой'
)

SPEC_BY_ID = {
    onAppActiveTick.id: onAppActiveTick,
}
