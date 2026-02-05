"""The BaseAppMgr component мessages (not generated)."""

from enki.kbeenum import ComponentType
from enki.kbetype.decoders.basic_data_type_decoders import (
    BOOL,
    FLOAT,
    INT8,
    INT32,
    STRING,
    UINT8_ARRAY,
    UINT16,
    UINT32,
    UINT64,
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
    name="Baseappmgr::lookApp",
    args_type=FIXED,
    args=(),
    desc="Check the component is alive",
)

onAppActiveTick = MsgDescr(  # noqa: N816
    id=55103,
    lenght=12,
    name="Baseappmgr::onAppActiveTick",
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
    name="Baseappmgr::onRegisterNewApp",
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
    desc="Сообщение от нового компонента о его регистрации в Baseappmgr",
)

updateBaseapp = MsgDescr(  # noqa: N816
    id=21,
    lenght=24,
    name="Baseappmgr::updateBaseapp",
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
    name="Baseappmgr::onBaseappInitProgress",
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
    name="Baseappmgr::reqCreateEntityAnywhere",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),  # см. обработчик
    desc="Запрос на создание сущности на наименее загруженном Baseapp",
)

reqCloseServer = MsgDescr(  # noqa: N816
    id=20,
    lenght=-1,
    name="Baseappmgr::reqCloseServer",
    args_type=VARIABLE,
    args=(),
    desc="Отправить сигнал компоненту, что ему нужно остановиться",
)

onPendingAccountGetBaseappAddr = MsgDescr(  # noqa: N816
    id=18,
    lenght=-1,
    name="Baseappmgr::onPendingAccountGetBaseappAddr",
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
    name="Baseappmgr::registerPendingAccountToBaseapp",
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
    desc="Регистрация отложенного аккаунта на Baseapp",
)

queryLoad = MsgDescr(  # noqa: N816
    id=10,
    lenght=4,
    name="Baseappmgr::queryLoad",
    args_type=FIXED,
    args=(),
    desc="Запрос загрузки указанного компонента",
)

reqCreateEntityRemotely = MsgDescr(  # noqa: N816
    id=12,
    lenght=-1,
    name="Baseappmgr::reqCreateEntityRemotely",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),  # см. обработчик
    desc="Запрос на создание сущности на удаленном Baseapp",
)

reqCreateEntityAnywhereFromDBIDQueryBestBaseappID = MsgDescr(  # noqa: N816
    id=13,
    lenght=-1,
    name="Baseappmgr::reqCreateEntityAnywhereFromDBIDQueryBestBaseappID",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),  # см. обработчик
    desc="Запрос ID наименее загруженного Baseapp для создания сущности по DBID",
)

reqCreateEntityAnywhereFromDBID = MsgDescr(  # noqa: N816
    id=14,
    lenght=-1,
    name="Baseappmgr::reqCreateEntityAnywhereFromDBID",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),  # см. обработчик
    desc="Создание сущности на наименее загруженном Baseapp по DBID",
)

reqCreateEntityRemotelyFromDBID = MsgDescr(  # noqa: N816
    id=15,
    lenght=-1,
    name="Baseappmgr::reqCreateEntityRemotelyFromDBID",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),  # см. обработчик
    desc="Создание сущности на удаленном Baseapp по DBID",
)

forwardMessage = MsgDescr(  # noqa: N816
    id=16,
    lenght=-1,
    name="Baseappmgr::forwardMessage",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),  # см. обработчик
    desc="Перенаправление сообщения между компонентами",
)

registerPendingAccountToBaseappAddr = MsgDescr(  # noqa: N816
    id=19,
    lenght=-1,
    name="Baseappmgr::registerPendingAccountToBaseappAddr",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),  # см. обработчик
    desc="Регистрация отложенного аккаунта по адресу Baseapp",
)

reqKillServer = MsgDescr(  # noqa: N816
    id=24,
    lenght=-1,
    name="Baseappmgr::reqKillServer",
    args_type=VARIABLE,
    args=(),
    desc="Запрос на принудительную остановку сервера",
)

startProfile = MsgDescr(  # noqa: N816
    id=23,
    lenght=-1,
    name="Baseappmgr::startProfile",
    args_type=VARIABLE,
    args=(
        STRING,  # profileName
        INT8,  # profileType
        UINT32,  # timelen
    ),
    desc="Запуск профилирования производительности",
)

queryWatcher = MsgDescr(  # noqa: N816
    id=41004,
    lenght=-1,
    name="Baseappmgr::queryWatcher",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),  # см. обработчик
    desc="Запрос данных мониторинга (watcher)",
)

queryAppsLoads = MsgDescr(  # noqa: N816
    id=50001,
    lenght=-1,
    name="Baseappmgr::queryAppsLoads",
    args_type=VARIABLE,
    args=(),
    desc="Запрос загрузки всех приложений",
)

reqAccountBindEmailAllocCallbackLoginapp = MsgDescr(  # noqa: N816
    id=25,
    lenght=-1,
    name="Baseappmgr::reqAccountBindEmailAllocCallbackLoginapp",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),  # см. обработчик
    desc="Запрос на привязку email к аккаунту с колбэком через Loginapp",
)

onReqAccountBindEmailCBFromLoginapp = MsgDescr(  # noqa: N816
    id=26,
    lenght=-1,
    name="Baseappmgr::onReqAccountBindEmailCBFromLoginapp",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),  # см. обработчик
    desc="Колбэк от Loginapp о результате привязки email к аккаунту",
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
    queryLoad.id: queryLoad,
    reqCreateEntityRemotely.id: reqCreateEntityRemotely,
    reqCreateEntityAnywhereFromDBIDQueryBestBaseappID.id: reqCreateEntityAnywhereFromDBIDQueryBestBaseappID,
    reqCreateEntityAnywhereFromDBID.id: reqCreateEntityAnywhereFromDBID,
    reqCreateEntityRemotelyFromDBID.id: reqCreateEntityRemotelyFromDBID,
    forwardMessage.id: forwardMessage,
    registerPendingAccountToBaseappAddr.id: registerPendingAccountToBaseappAddr,
    reqKillServer.id: reqKillServer,
    startProfile.id: startProfile,
    queryWatcher.id: queryWatcher,
    queryAppsLoads.id: queryAppsLoads,
    reqAccountBindEmailAllocCallbackLoginapp.id: reqAccountBindEmailAllocCallbackLoginapp,
    onReqAccountBindEmailCBFromLoginapp.id: onReqAccountBindEmailCBFromLoginapp,
}

__all__ = [
    "SPEC_BY_ID",
    "forwardMessage",
    "lookApp",
    "onAppActiveTick",
    "onBaseappInitProgress",
    "onLookApp",
    "onPendingAccountGetBaseappAddr",
    "onRegisterNewApp",
    "onReqAccountBindEmailCBFromLoginapp",
    "onReqCloseServer",
    "queryAppsLoads",
    "queryLoad",
    "queryWatcher",
    "registerPendingAccountToBaseapp",
    "registerPendingAccountToBaseappAddr",
    "reqAccountBindEmailAllocCallbackLoginapp",
    "reqCloseServer",
    "reqCreateEntityAnywhere",
    "reqCreateEntityAnywhereFromDBID",
    "reqCreateEntityAnywhereFromDBIDQueryBestBaseappID",
    "reqCreateEntityRemotely",
    "reqCreateEntityRemotelyFromDBID",
    "reqKillServer",
    "startProfile",
    "updateBaseapp",
]
