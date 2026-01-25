"""The DBMgr component мessages (not generated)."""

from enki.kbeenum import ComponentType
from enki.kbetype import INT32, STRING, UINT16, UINT32
from enki.kbetype.decoders.basic_data_type_decoders import (
    BLOB,
    BOOL,
    INT8,
    UINT8_ARRAY,
    UINT64,
)
from enki.kbetype.decoders.custom_decoders import (
    CALLBACK_ID,
    COMPONENT_ID,
    COMPONENT_ORDER,
    COMPONENT_TYPE,
    DBID,
    ENTITY_ID,
    ENTITY_SCRIPT_UID,
    SERVER_ERROR_CODE,
)
from enki.msg.msg_descr import FIXED, VARIABLE, MsgDescr

from . import custom

lookApp = MsgDescr(  # noqa: N816
    id=9,
    lenght=-1,
    name="DBMgr::lookApp",
    args_type=FIXED,
    args=(),
    desc="Check the component is alive",
)

onRegisterNewApp = MsgDescr(  # noqa: N816
    id=8,
    lenght=-1,
    name="DBMgr::onRegisterNewApp",
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
    desc="Зарегистрировать новый компонент",
)

onAppActiveTick = MsgDescr(  # noqa: N816
    id=55105,
    lenght=12,
    name="DBMgr::onAppActiveTick",
    args_type=FIXED,
    args=(
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
    ),
    desc="Компонент сообщает, что он живой",
)

onBroadcastGlobalDataChanged = MsgDescr(  # noqa: N816
    id=12,
    lenght=-1,
    name="DBMgr::onBroadcastGlobalDataChanged",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Изменение глобальных данных",
)

syncEntityStreamTemplate = MsgDescr(  # noqa: N816
    id=29,
    lenght=-1,
    name="DBMgr::syncEntityStreamTemplate",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

entityAutoLoad = MsgDescr(  # noqa: N816
    id=28,
    lenght=-1,
    name="DBMgr::entityAutoLoad",
    args_type=VARIABLE,
    args=(
        UINT16,  # dbInterfaceIndex
        COMPONENT_ID,  # componentID
        UINT16,  # entityType
        ENTITY_ID,  # start
        ENTITY_ID,  # end
    ),
    desc="",
)

reqCloseServer = MsgDescr(  # noqa: N816
    id=26,
    lenght=-1,
    name="DBMgr::reqCloseServer",
    args_type=VARIABLE,
    args=(),
    desc="Отправить сигнал компоненту, что ему нужно остановиться",
)

onAccountLogin = MsgDescr(  # noqa: N816
    id=15,
    lenght=-1,
    name="DBMgr::onAccountLogin",
    args_type=VARIABLE,
    args=(
        STRING,  # login
        STRING,  # password
        BLOB,  # data
    ),
    desc="Проброс вызова из Loginapp на DBMgr",
)

onLoginAccountCBBFromInterfaces = MsgDescr(  # noqa: N816
    id=16,
    lenght=-1,
    name="DBMgr::onLoginAccountCBBFromInterfaces",
    args_type=VARIABLE,
    args=(
        UINT64,  # component_id
        STRING,  # login
        STRING,  # account_name
        STRING,  # password
        SERVER_ERROR_CODE,  # ret_code
        BLOB,  # postdatas
        BLOB,  # getdatas
    ),
    desc="Ответ от Interfaces на DBMgr",
)

queryLoad = MsgDescr(  # noqa: N816
    id=10,
    lenght=-1,
    name="DBMgr::queryLoad",
    args_type=FIXED,
    args=(),
    desc="Запрос нагрузки компонента",
)

onReqAllocEntityID = MsgDescr(  # noqa: N816
    id=11,
    lenght=-1,
    name="DBMgr::onReqAllocEntityID",
    args_type=FIXED,
    args=(
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
    ),
    desc="Запрос на выделение ID сущностей",
)

reqCreateAccount = MsgDescr(  # noqa: N816
    id=13,
    lenght=-1,
    name="DBMgr::reqCreateAccount",
    args_type=VARIABLE,
    args=(
        STRING,  # accountName
        STRING,  # password
        BLOB,  # datas
    ),
    desc="Запрос на создание аккаунта",
)

onCreateAccountCBFromInterfaces = MsgDescr(  # noqa: N816
    id=14,
    lenght=-1,
    name="DBMgr::onCreateAccountCBFromInterfaces",
    args_type=VARIABLE,
    args=(
        UINT64,  # component_id
        STRING,  # accountName
        STRING,  # password
        UINT16,  # retcode
        BLOB,  # datas
    ),
    desc="Ответ от Interfaces на запрос создания аккаунта",
)

queryAccount = MsgDescr(  # noqa: N816
    id=17,
    lenght=-1,
    name="DBMgr::queryAccount",
    args_type=VARIABLE,
    args=(
        STRING,  # accountName
        STRING,  # password
        BOOL,  # needCheckPassword
        COMPONENT_ID,  # componentID
        ENTITY_ID,  # entityID
        DBID,  # entityDBID
        UINT32,  # ip
        UINT16,  # port
    ),
    desc="Запрос информации аккаунта",
)

onAccountOnline = MsgDescr(  # noqa: N816
    id=18,
    lenght=-1,
    name="DBMgr::onAccountOnline",
    args_type=VARIABLE,
    args=(
        STRING,  # account_name
        COMPONENT_ID,  # component_id
        ENTITY_ID,  # entity_id
    ),
    desc="Уведомление, что аккаунт в сети",
)

onEntityOffline = MsgDescr(  # noqa: N816
    id=19,
    lenght=12,
    name="DBMgr::onEntityOffline",
    args_type=FIXED,
    args=(
        DBID,  # dbid
        UINT16,  # sid
        UINT16,  # dbInterfaceIndex
    ),
    desc="Уведомление, что сущность offline",
)

eraseClientReq = MsgDescr(  # noqa: N816
    id=20,
    lenght=-1,
    name="DBMgr::eraseClientReq",
    args_type=VARIABLE,
    args=(STRING,),  # logkey
    desc="Request to erase client request task",
)

executeRawDatabaseCommand = MsgDescr(  # noqa: N816
    id=21,
    lenght=-1,
    name="DBMgr::executeRawDatabaseCommand",
    args_type=VARIABLE,
    args=(
        ENTITY_ID,  # entity_id
        UINT16,  # dbInterfaceIndex
        COMPONENT_ID,  # component_id
        COMPONENT_TYPE,  # componentType
        CALLBACK_ID,  # callback_id
        BLOB,  # row_sql
    ),
    desc="Выполнение сырой команды базы данных",
)

# [2026-01-25 11:35 burov_alexey@mail.ru]:
# Сообщение уточнять, когда научусь парсить данные сущностей

writeEntity = MsgDescr(  # noqa: N816
    id=22,
    lenght=-1,
    name="DBMgr::writeEntity",
    args_type=VARIABLE,
    args=(
        COMPONENT_ID,  # componentID
        ENTITY_ID,  # entity_id
        DBID,  # entity_db_id
        UINT16,  # dbInterfaceIndex
        ENTITY_SCRIPT_UID,  # sid
        CALLBACK_ID,  # callback_id
        BOOL,  # shouldAutoLoad
        UINT32,  # ip
        UINT16,  # port
        UINT8_ARRAY,  # данные сущности
    ),
    desc="Запись сущности в базу данных",
)

removeEntity = MsgDescr(  # noqa: N816
    id=23,
    lenght=-1,
    name="DBMgr::removeEntity",
    args_type=VARIABLE,
    args=(
        UINT16,  # dbInterfaceIndex
        COMPONENT_ID,  # componentID
        ENTITY_ID,  # entity_id
        DBID,  # entity_db_id
        ENTITY_SCRIPT_UID,  # sid
        UINT8_ARRAY,  # data (даныне в зависимости от условий)
    ),
    desc="Удаление сущности из базы данных",
)

deleteEntityByDBID = MsgDescr(  # noqa: N816
    id=24,
    lenght=-1,
    name="DBMgr::deleteEntityByDBID",
    args_type=VARIABLE,
    args=(
        UINT16,  # dbInterfaceIndex
        COMPONENT_ID,  # componentID
        DBID,  # entity_db_id
        CALLBACK_ID,  # callback_id
        ENTITY_SCRIPT_UID,  # sid
    ),
    desc="Удаление сущности по DBID",
)

lookUpEntityByDBID = MsgDescr(  # noqa: N816
    id=25,
    lenght=-1,
    name="DBMgr::lookUpEntityByDBID",
    args_type=VARIABLE,
    args=(
        UINT16,  # dbInterfaceIndex
        COMPONENT_ID,  # componentID
        DBID,  # entity_db_id
        CALLBACK_ID,  # callback_id
        ENTITY_SCRIPT_UID,  # sid
    ),
    desc="Поиск сущности по DBID",
)

queryEntity = MsgDescr(  # noqa: N816
    id=27,
    lenght=-1,
    name="DBMgr::queryEntity",
    args_type=VARIABLE,
    args=(
        UINT16,  # dbInterfaceIndex
        COMPONENT_ID,  # componentID
        INT8,  # queryMode
        DBID,  # entity_db_id
        STRING,  # entityType
        CALLBACK_ID,  # callback_id
        ENTITY_ID,  # entity_id
    ),
    desc="Запрос информации сущности",
)

charge = MsgDescr(
    id=30,
    lenght=-1,
    name="DBMgr::charge",
    args_type=VARIABLE,
    args=(
        STRING,  # chargeID
        DBID,  # dbid
        BLOB,  # data
        CALLBACK_ID,  # callback_id
    ),
    desc="Пополнение счета аккаунта",
)

onChargeCB = MsgDescr(  # noqa: N816
    id=31,
    lenght=-1,
    name="DBMgr::onChargeCB",
    args_type=VARIABLE,
    args=(
        COMPONENT_ID,  # baseappID
        STRING,  # order_id
        DBID,  # dbid
        BLOB,  # extraDatas
        CALLBACK_ID,  # cbid
        SERVER_ERROR_CODE,  # errorCodecbid
    ),
    desc="Ответ на пополнение счета",
)

accountActivate = MsgDescr(  # noqa: N816
    id=32,
    lenght=-1,
    name="DBMgr::accountActivate",
    args_type=VARIABLE,
    args=(STRING,),  # scode
    desc="Активация аккаунта",
)

accountReqResetPassword = MsgDescr(  # noqa: N816
    id=33,
    lenght=-1,
    name="DBMgr::accountReqResetPassword",
    args_type=VARIABLE,
    args=(STRING,),  # accountName
    desc="Запрос на сброс пароля",
)

accountResetPassword = MsgDescr(  # noqa: N816
    id=34,
    lenght=-1,
    name="DBMgr::accountResetPassword",
    args_type=VARIABLE,
    args=(
        STRING,  # accountName
        STRING,  # newpassword
        STRING,  # code
    ),
    desc="Сброс пароля аккаунта",
)

accountReqBindMail = MsgDescr(  # noqa: N816
    id=35,
    lenght=-1,
    name="DBMgr::accountReqBindMail",
    args_type=VARIABLE,
    args=(
        ENTITY_ID,  # entityID
        STRING,  # accountName
        STRING,  # password
        STRING,  # email
    ),
    desc="Запрос на привязку email",
)

accountBindMail = MsgDescr(  # noqa: N816
    id=36,
    lenght=-1,
    name="DBMgr::accountBindMail",
    args_type=VARIABLE,
    args=(
        STRING,  # accountName
        STRING,  # code
    ),
    desc="Привязка email к аккаунту",
)

accountNewPassword = MsgDescr(  # noqa: N816
    id=37,
    lenght=-1,
    name="DBMgr::accountNewPassword",
    args_type=VARIABLE,
    args=(
        ENTITY_ID,  # entity_id
        STRING,  # accountName
        STRING,  # password
        STRING,  # newPassword
    ),
    desc="Изменение пароля аккаунта",
)

startProfile = MsgDescr(  # noqa: N816
    id=38,
    lenght=-1,
    name="DBMgr::startProfile",
    args_type=VARIABLE,
    args=(
        STRING,  # profileName
        INT8,  # profileType
        UINT32,  # timelen
    ),
    desc="Запуск профилирования",
)

reqKillServer = MsgDescr(  # noqa: N816
    id=39,
    lenght=-1,
    name="DBMgr::reqKillServer",
    args_type=VARIABLE,
    args=(
        COMPONENT_ID,  # component_id
        COMPONENT_TYPE,  # componentType
        STRING,  # username
        INT32,  # uid
        STRING,  # reason
    ),
    desc="Запрос на принудительную остановку сервера",
)

queryWatcher = MsgDescr(  # noqa: N816
    id=41006,
    lenght=-1,
    name="DBMgr::queryWatcher",
    args_type=VARIABLE,
    args=(STRING,),  # path
    desc="Запрос информации watcher'ов",
)


onLookApp = custom.change_component_owner(  # noqa: N816
    custom.onLookApp, ComponentType.DBMGR
)
onReqCloseServer = custom.change_component_owner(  # noqa: N816
    custom.onReqCloseServer, ComponentType.DBMGR
)

SPEC_BY_ID = {
    lookApp.id: lookApp,
    onLookApp.id: onLookApp,
    onRegisterNewApp.id: onRegisterNewApp,
    onAppActiveTick.id: onAppActiveTick,
    onBroadcastGlobalDataChanged.id: onBroadcastGlobalDataChanged,
    syncEntityStreamTemplate.id: syncEntityStreamTemplate,
    entityAutoLoad.id: entityAutoLoad,
    reqCloseServer.id: reqCloseServer,
    onReqCloseServer.id: onReqCloseServer,
    onAccountLogin.id: onAccountLogin,
    onLoginAccountCBBFromInterfaces.id: onLoginAccountCBBFromInterfaces,
    queryLoad.id: queryLoad,
    onReqAllocEntityID.id: onReqAllocEntityID,
    reqCreateAccount.id: reqCreateAccount,
    onCreateAccountCBFromInterfaces.id: onCreateAccountCBFromInterfaces,
    queryAccount.id: queryAccount,
    onAccountOnline.id: onAccountOnline,
    onEntityOffline.id: onEntityOffline,
    eraseClientReq.id: eraseClientReq,
    executeRawDatabaseCommand.id: executeRawDatabaseCommand,
    writeEntity.id: writeEntity,
    removeEntity.id: removeEntity,
    deleteEntityByDBID.id: deleteEntityByDBID,
    lookUpEntityByDBID.id: lookUpEntityByDBID,
    queryEntity.id: queryEntity,
    charge.id: charge,
    onChargeCB.id: onChargeCB,
    accountActivate.id: accountActivate,
    accountReqResetPassword.id: accountReqResetPassword,
    accountResetPassword.id: accountResetPassword,
    accountReqBindMail.id: accountReqBindMail,
    accountBindMail.id: accountBindMail,
    accountNewPassword.id: accountNewPassword,
    startProfile.id: startProfile,
    reqKillServer.id: reqKillServer,
    queryWatcher.id: queryWatcher,
}

__all__ = [
    "SPEC_BY_ID",
    "accountActivate",
    "accountBindMail",
    "accountNewPassword",
    "accountReqBindMail",
    "accountReqResetPassword",
    "accountResetPassword",
    "charge",
    "deleteEntityByDBID",
    "entityAutoLoad",
    "eraseClientReq",
    "executeRawDatabaseCommand",
    "lookApp",
    "lookUpEntityByDBID",
    "onAccountLogin",
    "onAccountOnline",
    "onAppActiveTick",
    "onBroadcastGlobalDataChanged",
    "onChargeCB",
    "onCreateAccountCBFromInterfaces",
    "onEntityOffline",
    "onLoginAccountCBBFromInterfaces",
    "onLookApp",
    "onRegisterNewApp",
    "onReqAllocEntityID",
    "onReqCloseServer",
    "queryAccount",
    "queryEntity",
    "queryLoad",
    "queryWatcher",
    "removeEntity",
    "reqCloseServer",
    "reqCreateAccount",
    "reqKillServer",
    "startProfile",
    "syncEntityStreamTemplate",
    "writeEntity",
]
