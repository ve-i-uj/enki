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

onAppActiveTick = MsgDescr(
    id=55103,
    lenght=12,
    name='BaseappMgr::onAppActiveTick',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
        kbetype.COMPONENT_TYPE,  # componentType
        kbetype.COMPONENT_ID,  # componentID
    ]),
    desc='Компонент сообщает, что он живой'
)

onRegisterNewApp = MsgDescr(
    id=8,
    lenght=-1,
    name='BaseappMgr::onRegisterNewApp',
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

updateBaseapp = MsgDescr(
    id=21,
    lenght=24,
    name='BaseappMgr::updateBaseapp',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
        kbetype.COMPONENT_ID,  # componentID
        kbetype.ENTITY_ID,  # numBases
        kbetype.ENTITY_ID,  # numProxices
        kbetype.FLOAT,  # load
        kbetype.UINT32,  # flags
    ]),
    desc='Update baseapp information'
)

onBaseappInitProgress = MsgDescr(
    id=22,
    lenght=12,
    name='BaseappMgr::onBaseappInitProgress',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
        kbetype.COMPONENT_ID,  # cid
        kbetype.FLOAT,  # progress
    ]),
    desc='baseapp synchronizes its own initialization information'
)

reqCreateEntityAnywhere = MsgDescr(
    id=11,
    lenght=-1,
    name='Baseappmgr::reqCreateEntityAnywhere',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=tuple([
        kbetype.UINT8_ARRAY  # см. обработчик
    ]),
    desc='Запрос на создание сущность на наименее загруженном Baseapp'
)

SPEC_BY_ID = {
    lookApp.id: lookApp,
    onAppActiveTick.id: onAppActiveTick,
    onRegisterNewApp.id: onRegisterNewApp,
    updateBaseapp.id: updateBaseapp,
    onBaseappInitProgress.id: onBaseappInitProgress,
    reqCreateEntityAnywhere.id: reqCreateEntityAnywhere,
}
