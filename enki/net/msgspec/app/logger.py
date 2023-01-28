"""The Logger component мessages (not generated)."""

from enki import kbeenum
from enki.net.kbeclient.message import MsgDescr


queryLoad = MsgDescr(
    id=705,
    lenght=0,
    name='Logger::queryLoad',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc='(?) Check the component is alive'
)


SPEC_BY_ID = {
    queryLoad.id: queryLoad,
}
