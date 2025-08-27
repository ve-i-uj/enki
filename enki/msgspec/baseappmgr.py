"""The BaseAppMgr component мessages (not generated)."""

from enki.kbeenum import ComponentType
from enki.kbetype import FLOAT, INT32, STRING, UINT16, UINT32
from enki.kbetype.decoders.basic_data_type_decoders import (
    BOOL,
    UINT64,
    UINT8_ARRAY,
)
from enki.kbetype.decoders.custom_decoders import (
    COMPONENT_ID,
    COMPONENT_ORDER,
    COMPONENT_TYPE,
    DBID,
    ENTITY_ID,
)
from enki.msg.msg_descr import FIXED, VARIABLE, MsgDescr

from . import custom

lookApp = MsgDescr(  # noqa: N816
    id=9,
    lenght=-1,
    name="BaseappMgr::lookApp",
    args_type=FIXED,
    args=(),
    desc="Check the component is alive",
)

onAppActiveTick = MsgDescr(  # noqa: N816
    id=55103,
    lenght=12,
    name="BaseappMgr::onAppActiveTick",
    args_type=FIXED,
    args=(
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
    ),
    desc="Компонент сообщает, что он живой",
)

onRegisterNewApp = MsgDescr(  # noqa: N816
    id=8,
    lenght=-1,
    name="BaseappMgr::onRegisterNewApp",
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
    desc="???",
)

updateBaseapp = MsgDescr(  # noqa: N816
    id=21,
    lenght=24,
    name="BaseappMgr::updateBaseapp",
    args_type=FIXED,
    args=(
        COMPONENT_ID,  # componentID
        ENTITY_ID,  # numBases
        ENTITY_ID,  # numProxices
        FLOAT,  # load
        UINT32,  # flags
    ),
    desc="Update baseapp information",
)

onBaseappInitProgress = MsgDescr(  # noqa: N816
    id=22,
    lenght=12,
    name="BaseappMgr::onBaseappInitProgress",
    args_type=FIXED,
    args=(
        COMPONENT_ID,  # cid
        FLOAT,  # progress
    ),
    desc="baseapp synchronizes its own initialization information",
)

reqCreateEntityAnywhere = MsgDescr(  # noqa: N816
    id=11,
    lenght=-1,
    name="BaseappMgr::reqCreateEntityAnywhere",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),  # см. обработчик
    desc="Запрос на создание сущность на наименее загруженном Baseapp",
)

reqCloseServer = MsgDescr(  # noqa: N816
    id=20,
    lenght=-1,
    name="BaseappMgr::reqCloseServer",
    args_type=VARIABLE,
    args=(),
    desc="Отправить сигнал компоненту, что ему нужно остановиться",
)

onPendingAccountGetBaseappAddr = MsgDescr(  # noqa: N816
    id=18,
    lenght=-1,
    name="BaseappMgr::onPendingAccountGetBaseappAddr",
    args_type=VARIABLE,
    args=(
        STRING,  # loginName
        STRING,  # accountName
        STRING,  # addr
        UINT16,  # tcp_port
        UINT16,  # udp_port
    ),
    desc="Получить адрес Baseapp",
)

registerPendingAccountToBaseapp = MsgDescr(  # noqa: N816
    id=17,
    lenght=-1,
    name="BaseappMgr::registerPendingAccountToBaseapp",
    args_type=VARIABLE,
    args=(
        STRING,  # login
        STRING,  # account_name
        STRING,  # password
        BOOL,  # needCheckPassword
        DBID,  # dbid
        UINT32,  # flags
        UINT64,  # deadline
        INT32,  # clientType
        BOOL,  # forceInternalLogin
        STRING,  # datas
    ),
    desc="Получить адрес Baseapp",
)

onLookApp = custom.change_component_owner(  # noqa: N816
    custom.onLookApp, ComponentType.BASEAPPMGR
)
onReqCloseServer = custom.change_component_owner(  # noqa: N816
    custom.onReqCloseServer, ComponentType.BASEAPPMGR
)

SPEC_BY_ID = {
    onPendingAccountGetBaseappAddr.id: onPendingAccountGetBaseappAddr,
    onLookApp.id: onLookApp,
    lookApp.id: lookApp,
    onAppActiveTick.id: onAppActiveTick,
    onRegisterNewApp.id: onRegisterNewApp,
    updateBaseapp.id: updateBaseapp,
    onBaseappInitProgress.id: onBaseappInitProgress,
    reqCreateEntityAnywhere.id: reqCreateEntityAnywhere,
    reqCloseServer.id: reqCloseServer,
    onReqCloseServer.id: onReqCloseServer,
    registerPendingAccountToBaseapp.id: registerPendingAccountToBaseapp,
}

__all__ = [
    "SPEC_BY_ID",
    "lookApp",
    "onAppActiveTick",
    "onBaseappInitProgress",
    "onLookApp",
    "onPendingAccountGetBaseappAddr",
    "onRegisterNewApp",
    "onReqCloseServer",
    "registerPendingAccountToBaseapp",
    "reqCloseServer",
    "reqCreateEntityAnywhere",
    "updateBaseapp",
]
