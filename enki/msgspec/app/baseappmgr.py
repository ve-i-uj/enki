"""The BaseAppMgr component мessages (not generated)."""

from enki import kbeenum
from enki.core import kbetype
from enki.core.message import MsgDescr


lookApp = MsgDescr(  # noqa: N816
    id=9,
    lenght=-1,
    name='BaseappMgr::lookApp',
    args_type=FIXED,
    args=(),
    desc='Check the component is alive'
)

onAppActiveTick = MsgDescr(  # noqa: N816
    id=55103,
    lenght=12,
    name='BaseappMgr::onAppActiveTick',
    args_type=FIXED,
    args=(
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
    ),
    desc='Компонент сообщает, что он живой'
)

onRegisterNewApp = MsgDescr(  # noqa: N816
    id=8,
    lenght=-1,
    name='BaseappMgr::onRegisterNewApp',
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

updateBaseapp = MsgDescr(  # noqa: N816
    id=21,
    lenght=24,
    name='BaseappMgr::updateBaseapp',
    args_type=FIXED,
    args=(
        COMPONENT_ID,  # componentID
        ENTITY_ID,  # numBases
        ENTITY_ID,  # numProxices
        FLOAT,  # load
        UINT32,  # flags
    ),
    desc='Update baseapp information'
)

onBaseappInitProgress = MsgDescr(  # noqa: N816
    id=22,
    lenght=12,
    name='BaseappMgr::onBaseappInitProgress',
    args_type=FIXED,
    args=(
        COMPONENT_ID,  # cid
        FLOAT,  # progress
    ),
    desc='baseapp synchronizes its own initialization information'
)

reqCreateEntityAnywhere = MsgDescr(  # noqa: N816
    id=11,
    lenght=-1,
    name='BaseappMgr::reqCreateEntityAnywhere',
    args_type=VARIABLE,
    args=(
        UINT8_ARRAY  # см. обработчик
    )
    desc='Запрос на создание сущность на наименее загруженном Baseapp'
)

reqCloseServer = MsgDescr(  # noqa: N816
    id=20,
    lenght=-1,
    name='BaseappMgr::reqCloseServer',
    args_type=VARIABLE,
    args=(),
    desc='Отправить сигнал компоненту, что ему нужно остановиться'
)

SPEC_BY_ID = {
    lookApp.id: lookApp,
    onAppActiveTick.id: onAppActiveTick,
    onRegisterNewApp.id: onRegisterNewApp,
    updateBaseapp.id: updateBaseapp,
    onBaseappInitProgress.id: onBaseappInitProgress,
    reqCreateEntityAnywhere.id: reqCreateEntityAnywhere,
    reqCloseServer.id: reqCloseServer,
}

__all__ = [
    'SPEC_BY_ID',
    'lookApp',
    'onAppActiveTick',
    'onRegisterNewApp',
    'updateBaseapp',
    'onBaseappInitProgress',
    'reqCreateEntityAnywhere',
    'reqCloseServer',
]