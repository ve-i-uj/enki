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

onRegisterNewApp = MsgDescr(
    id=8,
    lenght=-1,
    name='Interfaces::onRegisterNewApp',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
        kbetype.INT32,  # uid
        kbetype.STRING,  # username
        kbetype.COMPONENT_TYPE,  # componentType
        kbetype.COMPONENT_ID,  # componentID
        kbetype.COMPONENT_ORDER,  # globalorderID
        kbetype.COMPONENT_ORDER,  # grouporderID
        kbetype.UINT32,  # intaddr
        kbetype.UINT16,  # intport
        kbetype.UINT32,  # extaddr
        kbetype.UINT16,  # extport
        kbetype.STRING,  # extaddrEx
    ]),
    desc='???'
)

onAppActiveTick = MsgDescr(
    id=55104,
    lenght=12,
    name='Interfaces::onAppActiveTick',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
        kbetype.COMPONENT_TYPE,  # componentType
        kbetype.COMPONENT_ID,  # componentID
    ]),
    desc='Компонент сообщает, что он живой'
)

reqCloseServer = MsgDescr(
    id=13,
    lenght=-1,
    name='Interfaces::reqCloseServer',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc='???'
)

SPEC_BY_ID = {
    lookApp.id: lookApp,
    fakeRespLookApp.id: fakeRespLookApp,

    onRegisterNewApp.id: onRegisterNewApp,
    reqCloseServer.id: reqCloseServer,

    onAppActiveTick.id: onAppActiveTick,
    # KBEngine одно и тоже сообщение гоняет, не меняя отправителя (скорей всего баг)
    55105: onAppActiveTick
}
