"""The DBMgr component мessages (not generated)."""

from enki.core import kbeenum
from enki.core import kbetype
from enki.core.message import MsgDescr


lookApp = MsgDescr(
    id=9,
    lenght=-1,
    name='DBMgr::lookApp',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
    ]),
    desc='Check the component is alive'
)

onRegisterNewApp = MsgDescr(
    id=8,
    lenght=-1,
    name='DBMgr::onRegisterNewApp',
    args_type=kbeenum.MsgArgsType.VARIABLE,
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
    id=55105,
    lenght=12,
    name='DBMgr::onAppActiveTick',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
        kbetype.COMPONENT_TYPE,  # componentType
        kbetype.COMPONENT_ID,  # componentID
    ]),
    desc='Компонент сообщает, что он живой'
)

onBroadcastGlobalDataChanged = MsgDescr(
    id=12,
    lenght=-1,
    name='DBMgr::onBroadcastGlobalDataChanged',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=tuple([
        kbetype.UINT8_ARRAY
    ]),
    desc=''
)

syncEntityStreamTemplate = MsgDescr(
    id=29,
    lenght=-1,
    name='DBMgr::syncEntityStreamTemplate',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=tuple([
        kbetype.UINT8_ARRAY
    ]),
    desc=''
)

entityAutoLoad = MsgDescr(
    id=28,
    lenght=-1,
    name='DBMgr::entityAutoLoad',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=tuple([
        kbetype.UINT16,  # dbInterfaceIndex
        kbetype.COMPONENT_ID,  # componentID
        kbetype.UINT16,  # entityType
        kbetype.ENTITY_ID,  # start
        kbetype.ENTITY_ID,  # end
    ]),
    desc=''
)

SPEC_BY_ID = {
    lookApp.id: lookApp,

    onRegisterNewApp.id: onRegisterNewApp,
    onAppActiveTick.id: onAppActiveTick,
    onBroadcastGlobalDataChanged.id: onBroadcastGlobalDataChanged,
    syncEntityStreamTemplate.id: syncEntityStreamTemplate,
    entityAutoLoad.id: entityAutoLoad,
}

__all__ = [
    'SPEC_BY_ID',
    'lookApp',

    'onRegisterNewApp',
    'onAppActiveTick',
    'onBroadcastGlobalDataChanged',
    'syncEntityStreamTemplate',
    'entityAutoLoad',
]