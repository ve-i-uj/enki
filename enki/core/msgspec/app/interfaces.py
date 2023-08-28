"""The Interfaces component мessages (not generated)."""

from enki.core import kbeenum
from enki.core import kbetype
from enki.core.message import MsgDescr


lookApp = MsgDescr(
    id=12,
    lenght=-1,
    name='Interfaces::lookApp',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
    ]),
    desc='Check the component is alive'
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

    onRegisterNewApp.id: onRegisterNewApp,
    reqCloseServer.id: reqCloseServer,

    onAppActiveTick.id: onAppActiveTick,
    # KBEngine одно и тоже сообщение гоняет, не меняя отправителя (скорей всего баг)
    55105: onAppActiveTick
}

__all__ = [
    'SPEC_BY_ID',
    'lookApp',
    'onRegisterNewApp',
    'reqCloseServer',
    'onAppActiveTick',
]