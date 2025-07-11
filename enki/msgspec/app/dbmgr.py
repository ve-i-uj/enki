"""The DBMgr component мessages (not generated)."""

from enki import kbeenum
from enki.core import kbetype
from enki.core.message import MsgDescr


lookApp = MsgDescr(  # noqa: N816
    id=9,
    lenght=-1,
    name='DBMgr::lookApp',
    args_type=FIXED,
    args=(),
    desc='Check the component is alive'
)

onRegisterNewApp = MsgDescr(  # noqa: N816
    id=8,
    lenght=-1,
    name='DBMgr::onRegisterNewApp',
    args_type=VARIABLE,
    args=(
        INT32,  # uid
        STRING,  # username
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
        COMPONENT_ORDER,  # globalorderID
        COMPONENT_ORDER,  # grouporderID
        UINT32,  # intaddr
        UINT16,  # intport
        UINT32,  # extaddr
        UINT16,  # extport
        STRING,  # extaddrEx
    ),
    desc='???'
)

onAppActiveTick = MsgDescr(  # noqa: N816
    id=55105,
    lenght=12,
    name='DBMgr::onAppActiveTick',
    args_type=FIXED,
    args=(
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
    ),
    desc='Компонент сообщает, что он живой'
)

onBroadcastGlobalDataChanged = MsgDescr(  # noqa: N816
    id=12,
    lenght=-1,
    name='DBMgr::onBroadcastGlobalDataChanged',
    args_type=VARIABLE,
    args=(
        UINT8_ARRAY,
    ),
    desc=''
)

syncEntityStreamTemplate = MsgDescr(  # noqa: N816
    id=29,
    lenght=-1,
    name='DBMgr::syncEntityStreamTemplate',
    args_type=VARIABLE,
    args=(
        UINT8_ARRAY,
    ),
    desc=''
)

entityAutoLoad = MsgDescr(  # noqa: N816
    id=28,
    lenght=-1,
    name='DBMgr::entityAutoLoad',
    args_type=VARIABLE,
    args=(
        UINT16,  # dbInterfaceIndex
        COMPONENT_ID,  # componentID
        UINT16,  # entityType
        ENTITY_ID,  # start
        ENTITY_ID,  # end
    ),
    desc=''
)

reqCloseServer = MsgDescr(  # noqa: N816
    id=26,
    lenght=-1,
    name='DBMgr::reqCloseServer',
    args_type=VARIABLE,
    args=(),
    desc='Отправить сигнал компоненту, что ему нужно остановиться'
)

SPEC_BY_ID = {
    lookApp.id: lookApp,

    onRegisterNewApp.id: onRegisterNewApp,
    onAppActiveTick.id: onAppActiveTick,
    onBroadcastGlobalDataChanged.id: onBroadcastGlobalDataChanged,
    syncEntityStreamTemplate.id: syncEntityStreamTemplate,
    entityAutoLoad.id: entityAutoLoad,
    reqCloseServer.id: reqCloseServer,
}

__all__ = [
    'SPEC_BY_ID',
    'lookApp',

    'onRegisterNewApp',
    'onAppActiveTick',
    'onBroadcastGlobalDataChanged',
    'syncEntityStreamTemplate',
    'entityAutoLoad',
    'reqCloseServer',
]