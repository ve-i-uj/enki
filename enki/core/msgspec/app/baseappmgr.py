"""The BaseAppMgr component мessages (not generated)."""

from enki.core import kbeenum
from enki.core import kbetype
from enki.core.message import MsgDescr


lookApp = MsgDescr(
    id=9,
    lenght=-1,
    name='BaseappMgr::lookApp',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
    ]),
    desc='Check the component is alive'
)

SPEC_BY_ID = {
    lookApp.id: lookApp
}
