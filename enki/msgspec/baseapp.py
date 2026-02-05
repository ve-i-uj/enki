"""Messages of BaseApp."""

from enki.kbeenum import ComponentType
from enki.kbetype.decoders.basic_data_type_decoders import (
    BLOB,
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
    CALLBACK_ID,
    COMPONENT_ID,
    COMPONENT_ORDER,
    COMPONENT_TYPE,
    DBID,
    ENTITY_ID,
    GAME_TIME,
    SHUTDOWN_STATE,
    SPACE_ID,
)
from enki.msg.msg_descr import FIXED, VARIABLE, MsgDescr, MsgSpecById

from . import custom

hello = MsgDescr(
    id=200,
    lenght=-1,
    name="Baseapp::hello",
    args_type=VARIABLE,
    args=(
        STRING,  # server version
        STRING,  # assets version
        BLOB,  # encrypted key
    ),
    desc="hello",
)

importClientMessages = MsgDescr(  # noqa: N816
    id=207,
    lenght=0,
    name="Baseapp::importClientMessages",
    args_type=FIXED,
    args=(),
    desc="The client requests to import the message protocol.",
)

importClientEntityDef = MsgDescr(  # noqa: N816
    id=208,
    lenght=0,
    name="Baseapp::importClientEntityDef",
    args_type=FIXED,
    args=(),
    desc="Client entitydef export.",
)

onUpdateDataFromClient = MsgDescr(  # noqa: N816
    id=27,
    lenght=-1,
    name="Baseapp::onUpdateDataFromClient",
    args_type=VARIABLE,
    args=(
        FLOAT,  # x
        FLOAT,  # y
        FLOAT,  # z
        FLOAT,  # roll
        FLOAT,  # pitch
        FLOAT,  # yaw
        BOOL,  # isOnGround
        SPACE_ID,  # spaceID
    ),
    desc="",
)

onUpdateDataFromClientForControlledEntity = MsgDescr(  # noqa: N816
    id=28,
    lenght=-1,
    name="Baseapp::onUpdateDataFromClientForControlledEntity",
    args_type=VARIABLE,
    args=(
        ENTITY_ID,  # entity_id
        FLOAT,  # x
        FLOAT,  # y
        FLOAT,  # z
        FLOAT,  # roll
        FLOAT,  # pitch
        FLOAT,  # yaw
        BOOL,  # isOnGround
        SPACE_ID,  # spaceID
    ),
    desc="",
)

lookApp = MsgDescr(  # noqa: N816
    id=8,
    lenght=-1,
    name="Baseapp::lookApp",
    args_type=FIXED,
    args=(),
    desc="Check the component is alive",
)

onCreateEntityAnywhere = MsgDescr(  # noqa: N816
    id=16,
    lenght=-1,
    name="Baseapp::onCreateEntityAnywhere",
    args_type=FIXED,
    args=(UINT8_ARRAY,),  # см. обработчик
    desc="Создать сущность на наименее этом Baseapp",
)

onGetEntityAppFromDbmgr = MsgDescr(  # noqa: N816
    id=11,
    lenght=-1,
    name="Baseapp::onGetEntityAppFromDbmgr",
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
    desc="",
)

onDbmgrInitCompleted = MsgDescr(  # noqa: N816
    id=13,
    lenght=-1,
    name="Baseapp::onDbmgrInitCompleted",
    args_type=VARIABLE,
    args=(
        GAME_TIME,  # gametime
        ENTITY_ID,  # startID
        ENTITY_ID,  # endID
        COMPONENT_ORDER,  # startGlobalOrder
        COMPONENT_ORDER,  # startGroupOrder
        STRING,  # digest
    ),
    desc="",
)

onEntityAutoLoadCBFromDBMgr = MsgDescr(  # noqa: N816
    id=23,
    lenght=-1,
    name="Baseapp::onEntityAutoLoadCBFromDBMgr",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc=(
        "Информация автоматической загрузке сущности, возвращаемая "
        "запросом из базы данных"
    ),
)

onBroadcastGlobalDataChanged = MsgDescr(  # noqa: N816
    id=14,
    lenght=-1,
    name="Baseapp::onBroadcastGlobalDataChanged",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onAppActiveTick = MsgDescr(  # noqa: N816
    id=55100,
    lenght=12,
    name="Baseapp::onAppActiveTick",
    args_type=FIXED,
    args=(
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
    ),
    desc="Компонент сообщает, что он живой",
)

onRegisterNewApp = MsgDescr(  # noqa: N816
    id=10,
    lenght=-1,
    name="Baseapp::onRegisterNewApp",
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

onEntityGetCell = MsgDescr(  # noqa: N816
    id=20,
    lenght=4 + 8 + 4,
    name="Baseapp::onEntityGetCell",
    args_type=FIXED,
    args=(
        ENTITY_ID,  # entity_id
        COMPONENT_ID,  # componentID
        SPACE_ID,  # spaceID
    ),
    desc="???",
)

reqCloseServer = MsgDescr(  # noqa: N816
    id=34,
    lenght=-1,
    name="Baseapp::reqCloseServer",
    args_type=VARIABLE,
    args=(),
    desc="Отправить сигнал компоненту, что ему нужно остановиться",
)


logoutBaseapp = MsgDescr(  # noqa: N816
    id=24,
    lenght=12,
    name="Baseapp::logoutBaseapp",
    args_type=FIXED,
    args=(
        UINT64,  # key
        INT32,  # entityID
    ),
    desc="",
)

reqAccountBindEmail = MsgDescr(  # noqa: N816
    id=51,
    lenght=-1,
    name="Baseapp::reqAccountBindEmail",
    args_type=FIXED,
    args=(
        ENTITY_ID,  # entityID
        STRING,  # password
        STRING,  # email
    ),
    desc="",
)

reqAccountNewPassword = MsgDescr(  # noqa: N816
    id=54,
    lenght=-1,
    name="Baseapp::reqAccountNewPassword",
    args_type=FIXED,
    args=(
        ENTITY_ID,  # entityID
        STRING,  # oldpassword
        STRING,  # newpassword
    ),
    desc="",
)

forwardEntityMessageToCellappFromClient = MsgDescr(  # noqa: N816
    id=58,
    lenght=-1,
    name="Entity::forwardEntityMessageToCellappFromClient",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)


loginBaseapp = MsgDescr(  # noqa: N816
    id=202,
    lenght=-1,
    name="Baseapp::loginBaseapp",
    args_type=FIXED,
    args=(
        STRING,  # accountName
        STRING,  # password
    ),
    desc="",
)

reloginBaseapp = MsgDescr(  # noqa: N816
    id=204,
    lenght=-1,
    name="Baseapp::reloginBaseapp",
    args_type=FIXED,
    args=(
        STRING,  # accountName
        STRING,  # password
        UINT64,  # key
        ENTITY_ID,  # enitity_id
    ),
    desc="",
)

onRemoteCallCellMethodFromClient = MsgDescr(  # noqa: N816
    id=205,
    lenght=-1,
    name="Baseapp::onRemoteCallCellMethodFromClient",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onClientActiveTick = MsgDescr(  # noqa: N816
    id=206,
    lenght=0,
    name="Baseapp::onClientActiveTick",
    args_type=FIXED,
    args=(),
    desc="",
)

onRemoteMethodCall = MsgDescr(  # noqa: N816
    id=302,
    lenght=-1,
    name="Entity::onRemoteMethodCall",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)


registerPendingLogin = MsgDescr(  # noqa: N816
    id=22,
    lenght=-1,
    name="Baseapp::registerPendingLogin",
    args_type=VARIABLE,
    args=(
        STRING,  # login
        STRING,  # account_name
        STRING,  # password
        BOOL,  # needCheckPassword
        ENTITY_ID,  # eid
        DBID,  # entityDBID
        UINT32,  # flags
        UINT64,  # deadline
        INT32,  # clientType
        BOOL,  # forceInternalLogin
        STRING,  # datas
    ),
    desc="",
)


reqClose = MsgDescr(  # noqa: N816
    id=201,
    lenght=0,
    name="Baseapp::reqClose",
    args_type=FIXED,
    args=(),
    desc="",
)

queryLoad = MsgDescr(  # noqa: N816
    id=9,
    lenght=0,
    name="Baseapp::queryLoad",
    args_type=FIXED,
    args=(),
    desc="",
)

onExecScriptCommand = MsgDescr(  # noqa: N816
    id=55001,
    lenght=-1,
    name="Baseapp::onExecScriptCommand",
    args_type=VARIABLE,
    args=(STRING,),  # command
    desc="",
)

onReqAllocEntityID = MsgDescr(  # noqa: N816
    id=12,
    lenght=-1,
    name="Baseapp::onReqAllocEntityID",
    args_type=VARIABLE,
    args=(UINT32,),  # count
    desc="",
)

onBroadcastBaseAppDataChanged = MsgDescr(  # noqa: N816
    id=15,
    lenght=-1,
    name="Baseapp::onBroadcastBaseAppDataChanged",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onCreateEntityAnywhereCallback = MsgDescr(  # noqa: N816
    id=17,
    lenght=-1,
    name="Baseapp::onCreateEntityAnywhereCallback",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onCreateEntityRemotely = MsgDescr(  # noqa: N816
    id=18,
    lenght=-1,
    name="Baseapp::onCreateEntityRemotely",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onCreateEntityRemotelyCallback = MsgDescr(  # noqa: N816
    id=19,
    lenght=-1,
    name="Baseapp::onCreateEntityRemotelyCallback",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onCreateCellFailure = MsgDescr(  # noqa: N816
    id=21,
    lenght=-1,
    name="Baseapp::onCreateCellFailure",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onQueryAccountCBFromDbmgr = MsgDescr(  # noqa: N816
    id=25,
    lenght=-1,
    name="Baseapp::onQueryAccountCBFromDbmgr",
    args_type=VARIABLE,
    args=(
        UINT16,  # dbInterfaceIndex
        STRING,  # accountName
        STRING,  # password
        DBID,  # dbid
        BOOL,  # success
        ENTITY_ID,  # entityID
        UINT32,  # flags
        UINT64,  # deadline
        UINT8_ARRAY,  # data
    ),
    desc="",
)

onEntityCall = MsgDescr(  # noqa: N816
    id=26,
    lenght=-1,
    name="Baseapp::onEntityCall",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onExecuteRawDatabaseCommandCB = MsgDescr(  # noqa: N816
    id=29,
    lenght=-1,
    name="Baseapp::onExecuteRawDatabaseCommandCB",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onBackupEntityCellData = MsgDescr(  # noqa: N816
    id=30,
    lenght=-1,
    name="Baseapp::onBackupEntityCellData",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onCellWriteToDBCompleted = MsgDescr(  # noqa: N816
    id=31,
    lenght=-1,
    name="Baseapp::onCellWriteToDBCompleted",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

forwardMessageToClientFromCellapp = MsgDescr(  # noqa: N816
    id=32,
    lenght=-1,
    name="Baseapp::forwardMessageToClientFromCellapp",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

forwardMessageToCellappFromCellapp = MsgDescr(  # noqa: N816
    id=33,
    lenght=-1,
    name="Baseapp::forwardMessageToCellappFromCellapp",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

reqSetFlags = MsgDescr(  # noqa: N816
    id=35,
    lenght=-1,
    name="Baseapp::reqSetFlags",
    args_type=VARIABLE,
    args=(UINT32,),  # flags
    desc="",
)

onWriteToDBCallback = MsgDescr(  # noqa: N816
    id=36,
    lenght=19,
    name="Baseapp::onWriteToDBCallback",
    args_type=FIXED,
    args=(
        ENTITY_ID,  # eid
        DBID,  # entityDBID
        UINT16,  # dbInterfaceIndex
        CALLBACK_ID,  # callbackID
        BOOL,  # success
    ),
    desc="",
)


onCreateEntityFromDBIDCallback = MsgDescr(  # noqa: N816
    id=37,
    lenght=-1,
    name="Baseapp::onCreateEntityFromDBIDCallback",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onGetCreateEntityAnywhereFromDBIDBestBaseappID = MsgDescr(  # noqa: N816
    id=38,
    lenght=-1,
    name="Baseapp::onGetCreateEntityAnywhereFromDBIDBestBaseappID",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onCreateEntityAnywhereFromDBIDCallback = MsgDescr(  # noqa: N816
    id=39,
    lenght=-1,
    name="Baseapp::onCreateEntityAnywhereFromDBIDCallback",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

createEntityAnywhereFromDBIDOtherBaseapp = MsgDescr(  # noqa: N816
    id=40,
    lenght=-1,
    name="Baseapp::createEntityAnywhereFromDBIDOtherBaseapp",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onCreateEntityAnywhereFromDBIDOtherBaseappCallback = MsgDescr(  # noqa: N816
    id=41,
    lenght=-1,
    name="Baseapp::onCreateEntityAnywhereFromDBIDOtherBaseappCallback",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onCreateEntityRemotelyFromDBIDCallback = MsgDescr(  # noqa: N816
    id=42,
    lenght=-1,
    name="Baseapp::onCreateEntityRemotelyFromDBIDCallback",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

createEntityRemotelyFromDBIDOtherBaseapp = MsgDescr(  # noqa: N816
    id=43,
    lenght=-1,
    name="Baseapp::createEntityRemotelyFromDBIDOtherBaseapp",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onCreateEntityRemotelyFromDBIDOtherBaseappCallback = MsgDescr(  # noqa: N816
    id=44,
    lenght=-1,
    name="Baseapp::onCreateEntityRemotelyFromDBIDOtherBaseappCallback",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

queryWatcher = MsgDescr(  # noqa: N816
    id=41001,
    lenght=-1,
    name="Baseapp::queryWatcher",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onChargeCB = MsgDescr(  # noqa: N816
    id=45,
    lenght=-1,
    name="Baseapp::onChargeCB",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

startProfile = MsgDescr(  # noqa: N816
    id=46,
    lenght=-1,
    name="Baseapp::startProfile",
    args_type=VARIABLE,
    args=(
        STRING,  # profileName
        INT8,  # profileType
        UINT32,  # timelen
    ),
    desc="",
)

deleteEntityByDBIDCB = MsgDescr(  # noqa: N816
    id=47,
    lenght=-1,
    name="Baseapp::deleteEntityByDBIDCB",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

lookUpEntityByDBIDCB = MsgDescr(  # noqa: N816
    id=48,
    lenght=-1,
    name="Baseapp::lookUpEntityByDBIDCB",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onRestoreSpaceCellFromOtherBaseapp = MsgDescr(  # noqa: N816
    id=49,
    lenght=-1,
    name="Baseapp::onRestoreSpaceCellFromOtherBaseapp",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onRequestRestoreCB = MsgDescr(  # noqa: N816
    id=50,
    lenght=-1,
    name="Baseapp::onRequestRestoreCB",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onReqAccountBindEmailCBFromDBMgr = MsgDescr(  # noqa: N816
    id=52,
    lenght=-1,
    name="Baseapp::onReqAccountBindEmailCBFromDBMgr",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onReqAccountBindEmailCBFromBaseappmgr = MsgDescr(  # noqa: N816
    id=53,
    lenght=-1,
    name="Baseapp::onReqAccountBindEmailCBFromBaseappmgr",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onReqAccountNewPasswordCB = MsgDescr(  # noqa: N816
    id=55,
    lenght=-1,
    name="Baseapp::onReqAccountNewPasswordCB",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

reqKillServer = MsgDescr(  # noqa: N816
    id=56,
    lenght=-1,
    name="Baseapp::reqKillServer",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onLookApp = MsgDescr(  # noqa: N816
    id=custom.get_fake_msg_id(),
    lenght=29,
    name="Baseapp::onLookApp",
    args_type=FIXED,
    args=(
        COMPONENT_TYPE,
        COMPONENT_ID,
        SHUTDOWN_STATE,
        UINT32,  # entitiesSize
        INT32,  # numClients
        INT32,  # numProxices
        UINT32,  # port
    ),
    desc="Пользовательское сообщение фиксирующее ответ на ::lookApp",
)

onReqCloseServer = custom.change_component_owner(  # noqa: N816
    custom.onReqCloseServer, ComponentType.BASEAPP
)

SPEC_BY_ID: MsgSpecById = {
    onLookApp.id: onLookApp,
    onReqCloseServer.id: onReqCloseServer,
    forwardEntityMessageToCellappFromClient.id: forwardEntityMessageToCellappFromClient,  # noqa: E501
    hello.id: hello,
    importClientEntityDef.id: importClientEntityDef,
    importClientMessages.id: importClientMessages,
    loginBaseapp.id: loginBaseapp,
    logoutBaseapp.id: logoutBaseapp,
    lookApp.id: lookApp,
    onAppActiveTick.id: onAppActiveTick,
    onBroadcastGlobalDataChanged.id: onBroadcastGlobalDataChanged,
    onClientActiveTick.id: onClientActiveTick,
    onCreateEntityAnywhere.id: onCreateEntityAnywhere,
    onDbmgrInitCompleted.id: onDbmgrInitCompleted,
    onEntityAutoLoadCBFromDBMgr.id: onEntityAutoLoadCBFromDBMgr,
    onEntityGetCell.id: onEntityGetCell,
    onGetEntityAppFromDbmgr.id: onGetEntityAppFromDbmgr,
    onRegisterNewApp.id: onRegisterNewApp,
    onRemoteCallCellMethodFromClient.id: onRemoteCallCellMethodFromClient,
    onRemoteMethodCall.id: onRemoteMethodCall,
    onUpdateDataFromClient.id: onUpdateDataFromClient,
    onUpdateDataFromClientForControlledEntity.id: onUpdateDataFromClientForControlledEntity,  # noqa: E501
    reloginBaseapp.id: reloginBaseapp,
    reqAccountBindEmail.id: reqAccountBindEmail,
    reqAccountNewPassword.id: reqAccountNewPassword,
    reqCloseServer.id: reqCloseServer,
    registerPendingLogin.id: registerPendingLogin,
    reqClose.id: reqClose,
    queryLoad.id: queryLoad,
    onExecScriptCommand.id: onExecScriptCommand,
    onReqAllocEntityID.id: onReqAllocEntityID,
    onBroadcastBaseAppDataChanged.id: onBroadcastBaseAppDataChanged,
    onCreateEntityAnywhereCallback.id: onCreateEntityAnywhereCallback,
    onCreateEntityRemotely.id: onCreateEntityRemotely,
    onCreateEntityRemotelyCallback.id: onCreateEntityRemotelyCallback,
    onCreateCellFailure.id: onCreateCellFailure,
    onQueryAccountCBFromDbmgr.id: onQueryAccountCBFromDbmgr,
    onEntityCall.id: onEntityCall,
    onExecuteRawDatabaseCommandCB.id: onExecuteRawDatabaseCommandCB,
    onBackupEntityCellData.id: onBackupEntityCellData,
    onCellWriteToDBCompleted.id: onCellWriteToDBCompleted,
    forwardMessageToClientFromCellapp.id: forwardMessageToClientFromCellapp,
    forwardMessageToCellappFromCellapp.id: forwardMessageToCellappFromCellapp,
    reqSetFlags.id: reqSetFlags,
    onWriteToDBCallback.id: onWriteToDBCallback,
    onCreateEntityFromDBIDCallback.id: onCreateEntityFromDBIDCallback,
    onGetCreateEntityAnywhereFromDBIDBestBaseappID.id: onGetCreateEntityAnywhereFromDBIDBestBaseappID,
    onCreateEntityAnywhereFromDBIDCallback.id: onCreateEntityAnywhereFromDBIDCallback,
    createEntityAnywhereFromDBIDOtherBaseapp.id: createEntityAnywhereFromDBIDOtherBaseapp,
    onCreateEntityAnywhereFromDBIDOtherBaseappCallback.id: onCreateEntityAnywhereFromDBIDOtherBaseappCallback,
    onCreateEntityRemotelyFromDBIDCallback.id: onCreateEntityRemotelyFromDBIDCallback,
    createEntityRemotelyFromDBIDOtherBaseapp.id: createEntityRemotelyFromDBIDOtherBaseapp,
    onCreateEntityRemotelyFromDBIDOtherBaseappCallback.id: onCreateEntityRemotelyFromDBIDOtherBaseappCallback,
    queryWatcher.id: queryWatcher,
    onChargeCB.id: onChargeCB,
    startProfile.id: startProfile,
    deleteEntityByDBIDCB.id: deleteEntityByDBIDCB,
    lookUpEntityByDBIDCB.id: lookUpEntityByDBIDCB,
    onRestoreSpaceCellFromOtherBaseapp.id: onRestoreSpaceCellFromOtherBaseapp,
    onRequestRestoreCB.id: onRequestRestoreCB,
    onReqAccountBindEmailCBFromDBMgr.id: onReqAccountBindEmailCBFromDBMgr,
    onReqAccountBindEmailCBFromBaseappmgr.id: onReqAccountBindEmailCBFromBaseappmgr,
    onReqAccountNewPasswordCB.id: onReqAccountNewPasswordCB,
    reqKillServer.id: reqKillServer,
}


__all__ = [
    "SPEC_BY_ID",
    "createEntityAnywhereFromDBIDOtherBaseapp",
    "createEntityRemotelyFromDBIDOtherBaseapp",
    "deleteEntityByDBIDCB",
    "forwardEntityMessageToCellappFromClient",
    "forwardMessageToCellappFromCellapp",
    "forwardMessageToClientFromCellapp",
    "hello",
    "importClientEntityDef",
    "importClientMessages",
    "loginBaseapp",
    "logoutBaseapp",
    "lookApp",
    "lookUpEntityByDBIDCB",
    "onAppActiveTick",
    "onBackupEntityCellData",
    "onBroadcastBaseAppDataChanged",
    "onBroadcastGlobalDataChanged",
    "onCellWriteToDBCompleted",
    "onChargeCB",
    "onClientActiveTick",
    "onCreateCellFailure",
    "onCreateEntityAnywhere",
    "onCreateEntityAnywhereCallback",
    "onCreateEntityAnywhereFromDBIDCallback",
    "onCreateEntityAnywhereFromDBIDOtherBaseappCallback",
    "onCreateEntityFromDBIDCallback",
    "onCreateEntityRemotely",
    "onCreateEntityRemotelyCallback",
    "onCreateEntityRemotelyFromDBIDCallback",
    "onCreateEntityRemotelyFromDBIDOtherBaseappCallback",
    "onDbmgrInitCompleted",
    "onEntityAutoLoadCBFromDBMgr",
    "onEntityCall",
    "onEntityGetCell",
    "onExecScriptCommand",
    "onExecuteRawDatabaseCommandCB",
    "onGetCreateEntityAnywhereFromDBIDBestBaseappID",
    "onGetEntityAppFromDbmgr",
    "onLookApp",
    "onQueryAccountCBFromDbmgr",
    "onRegisterNewApp",
    "onRemoteCallCellMethodFromClient",
    "onRemoteMethodCall",
    "onReqAccountBindEmailCBFromBaseappmgr",
    "onReqAccountBindEmailCBFromDBMgr",
    "onReqAccountNewPasswordCB",
    "onReqAllocEntityID",
    "onRequestRestoreCB",
    "onRestoreSpaceCellFromOtherBaseapp",
    "onUpdateDataFromClient",
    "onUpdateDataFromClientForControlledEntity",
    "onWriteToDBCallback",
    "queryLoad",
    "queryWatcher",
    "registerPendingLogin",
    "reloginBaseapp",
    "reqAccountBindEmail",
    "reqAccountNewPassword",
    "reqClose",
    "reqCloseServer",
    "reqKillServer",
    "reqSetFlags",
    "startProfile",
]
