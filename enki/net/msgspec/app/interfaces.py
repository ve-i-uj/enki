"""The Interfaces component мessages (not generated)."""

from enki import kbeenum
from enki.net.kbeclient import kbetype
from enki.net.kbeclient.message import MsgDescr

from .. import internal


lookApp = MsgDescr(
    id=12,
    lenght=-1,
    name='Interfaces::lookApp',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
    ]),
    desc='Check the component is alive'
)

fakeRespLookApp = MsgDescr(
    id=internal.get_fake_msg_id(),
    lenght=9,
    name='Enki::fakeRespLookApp',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.COMPONENT_TYPE,
        kbetype.COMPONENT_ID,
        kbetype.INT8
    ),
    desc='The fake message contained the serialization specification'
)

SPEC_BY_ID = {
    lookApp.id: lookApp,
    fakeRespLookApp.id: fakeRespLookApp,
}
