"""Messages of the CellApp component.

These messages are predefined by the plugin (not generated).
"""

from enki.kbeenum import ComponentType
from enki.kbetype import FLOAT, INT32, STRING, UINT16, UINT32
from enki.kbetype.decoders.basic_data_type_decoders import UINT8_ARRAY
from enki.kbetype.decoders.custom_decoders import (
    COMPONENT_ID,
    COMPONENT_ORDER,
    COMPONENT_TYPE,
    ENTITY_ID,
    GAME_TIME,
)
from enki.msg.msg_descr import FIXED, VARIABLE, MsgDescr

from . import custom

# Cellapp messages sorted by ID
onRegisterNewApp = MsgDescr(
    id=8,
    lenght=-1,
    name="Cellapp::onRegisterNewApp",
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
    desc="Register new application component",
)

lookApp = MsgDescr(
    id=9,
    lenght=-1,
    name="Cellapp::lookApp",
    args_type=FIXED,
    args=(),
    desc="Check if the component is alive",
)

queryLoad = MsgDescr(
    id=10,
    lenght=-1,
    name="Cellapp::queryLoad",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Query current load status",
)

onGetEntityAppFromDbmgr = MsgDescr(
    id=11,
    lenght=-1,
    name="Cellapp::onGetEntityAppFromDbmgr",
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
    desc="Get entity application information from database manager",
)

onReqAllocEntityID = MsgDescr(
    id=12,
    lenght=-1,
    name="Cellapp::onReqAllocEntityID",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Request allocation of entity ID",
)

onDbmgrInitCompleted = MsgDescr(
    id=13,
    lenght=-1,
    name="Cellapp::onDbmgrInitCompleted",
    args_type=VARIABLE,
    args=(
        GAME_TIME,  # gametime
        ENTITY_ID,  # startID
        ENTITY_ID,  # endID
        COMPONENT_ORDER,  # startGlobalOrder
        COMPONENT_ORDER,  # startGroupOrder
        STRING,  # digest
    ),
    desc="Database manager initialization completed",
)

onBroadcastGlobalDataChanged = MsgDescr(
    id=14,
    lenght=-1,
    name="Cellapp::onBroadcastGlobalDataChanged",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Broadcast global data change notification",
)

onBroadcastCellAppDataChanged = MsgDescr(
    id=15,
    lenght=12,
    name="Cellapp::onBroadcastCellAppDataChanged",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Broadcast CellApp data change notification",
)

onCreateCellEntityInNewSpaceFromBaseapp = MsgDescr(
    id=16,
    lenght=-1,
    name="Cellapp::onCreateCellEntityInNewSpaceFromBaseapp",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Create cell entity in new space from BaseApp",
)

onRestoreSpaceInCellFromBaseapp = MsgDescr(
    id=17,
    lenght=-1,
    name="Cellapp::onRestoreSpaceInCellFromBaseapp",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Restore space in cell from BaseApp",
)

requestRestore = MsgDescr(
    id=18,
    lenght=-1,
    name="Cellapp::requestRestore",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Request restoration of cell data",
)

onCreateCellEntityFromBaseapp = MsgDescr(
    id=19,
    lenght=-1,
    name="Cellapp::onCreateCellEntityFromBaseapp",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Create cell entity from BaseApp",
)

onDestroyCellEntityFromBaseapp = MsgDescr(
    id=20,
    lenght=-1,
    name="Cellapp::onDestroyCellEntityFromBaseapp",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Destroy cell entity from BaseApp",
)

onEntityCall = MsgDescr(
    id=21,
    lenght=-1,
    name="Cellapp::onEntityCall",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Entity method call",
)

onRemoteCallMethodFromClient = MsgDescr(
    id=22,
    lenght=-1,
    name="Cellapp::onRemoteCallMethodFromClient",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Remote method call from client",
)

onUpdateDataFromClient = MsgDescr(
    id=23,
    lenght=-1,
    name="Cellapp::onUpdateDataFromClient",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Update entity data from client",
)

onUpdateDataFromClientForControlledEntity = MsgDescr(
    id=24,
    lenght=-1,
    name="Cellapp::onUpdateDataFromClientForControlledEntity",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Update data from client for controlled entity",
)

onExecuteRawDatabaseCommandCB = MsgDescr(
    id=25,
    lenght=-1,
    name="Cellapp::onExecuteRawDatabaseCommandCB",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Callback for raw database command execution",
)

reqBackupEntityCellData = MsgDescr(
    id=26,
    lenght=-1,
    name="Cellapp::reqBackupEntityCellData",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Request backup of entity cell data",
)

reqWriteToDBFromBaseapp = MsgDescr(
    id=27,
    lenght=-1,
    name="Cellapp::reqWriteToDBFromBaseapp",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Request write to database from BaseApp",
)

forwardEntityMessageToCellappFromClient = MsgDescr(
    id=28,
    lenght=-1,
    name="Cellapp::forwardEntityMessageToCellappFromClient",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Forward entity message from client to CellApp",
)

reqCloseServer = MsgDescr(
    id=29,
    lenght=-1,
    name="Cellapp::reqCloseServer",
    args_type=VARIABLE,
    args=(),
    desc="Request server shutdown",
)

startProfile = MsgDescr(
    id=30,
    lenght=-1,
    name="Cellapp::startProfile",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Start profiling",
)

reqTeleportToCellApp = MsgDescr(
    id=31,
    lenght=-1,
    name="Cellapp::reqTeleportToCellApp",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Request teleport to another CellApp",
)

reqTeleportToCellAppCB = MsgDescr(
    id=32,
    lenght=-1,
    name="Cellapp::reqTeleportToCellAppCB",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Callback for teleport request to CellApp",
)

reqTeleportToCellAppOver = MsgDescr(
    id=33,
    lenght=-1,
    name="Cellapp::reqTeleportToCellAppOver",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Teleport to CellApp completed",
)

onUpdateGhostPropertys = MsgDescr(
    id=34,
    lenght=-1,
    name="Cellapp::onUpdateGhostPropertys",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Update ghost properties",
)

onRemoteRealMethodCall = MsgDescr(
    id=35,
    lenght=-1,
    name="Cellapp::onRemoteRealMethodCall",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Remote real method call",
)

onUpdateGhostVolatileData = MsgDescr(
    id=36,
    lenght=-1,
    name="Cellapp::onUpdateGhostVolatileData",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Update ghost volatile data",
)

reqKillServer = MsgDescr(
    id=37,
    lenght=-1,
    name="Cellapp::reqKillServer",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Request to kill server",
)

reqSetFlags = MsgDescr(
    id=38,
    lenght=-1,
    name="Cellapp::reqSetFlags",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Request to set flags",
)

setPosition_XZ_int = MsgDescr(
    id=39,
    lenght=-1,
    name="Entity::setPosition_XZ_int",
    args_type=FIXED,
    args=(
        ENTITY_ID,
        INT32,
        INT32,
    ),
    desc="Set entity position with XZ integer coordinates",
)


setPosition_XYZ_int = MsgDescr(
    id=40,
    lenght=-1,
    name="Entity::setPosition_XYZ_int",
    args_type=FIXED,
    args=(
        ENTITY_ID,
        INT32,
        INT32,
        INT32,
    ),
    desc="Set entity position with XYZ integer coordinates",
)


setPosition_XZ_float = MsgDescr(
    id=41,
    lenght=12,
    name="Entity::setPosition_XZ_float",
    args_type=FIXED,
    args=(
        ENTITY_ID,
        FLOAT,
        FLOAT,
    ),
    desc="Set entity position with XZ float coordinates",
)


setPosition_XYZ_float = MsgDescr(
    id=42,
    lenght=14,
    name="Entity::setPosition_XYZ_float",
    args_type=FIXED,
    args=(
        ENTITY_ID,
        FLOAT,
        FLOAT,
        FLOAT,
    ),
    desc="Set entity position with XYZ float coordinates",
)

onGetWitnessFromBase = MsgDescr(
    id=43,
    lenght=-1,
    name="Entity::onGetWitnessFromBase",
    args_type=FIXED,
    args=(ENTITY_ID,),
    desc="Entity gets witness from base",
)

onLoseWitness = MsgDescr(
    id=44,
    lenght=-1,
    name="Entity::onLoseWitness",
    args_type=FIXED,
    args=(ENTITY_ID,),
    desc="Entity loses witness",
)


onRemoteMethodCall = MsgDescr(
    id=302,
    lenght=-1,
    name="Entity::onRemoteMethodCall",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Remote method call to entity",
)

queryWatcher = MsgDescr(
    id=41002,
    lenght=-1,
    name="Cellapp::queryWatcher",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Query watcher information",
)

setSpaceViewer = MsgDescr(
    id=50005,
    lenght=-1,
    name="Cellapp::setSpaceViewer",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Set space viewer",
)

onExecScriptCommand = MsgDescr(
    id=55002,
    lenght=-1,
    name="Cellapp::onExecScriptCommand",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Execute script command",
)

onAppActiveTick = MsgDescr(
    id=55101,
    lenght=12,
    name="Cellapp::onAppActiveTick",
    args_type=FIXED,
    args=(
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
    ),
    desc="Component active tick notification",
)

# Custom messages with changed component owner
onLookApp = custom.change_component_owner(
    custom.onLookApp, ComponentType.CELLAPP
)
onReqCloseServer = custom.change_component_owner(
    custom.onReqCloseServer, ComponentType.CELLAPP
)

# Dictionary sorted alphabetically by message name
SPEC_BY_ID = {
    forwardEntityMessageToCellappFromClient.id: forwardEntityMessageToCellappFromClient,
    lookApp.id: lookApp,
    onAppActiveTick.id: onAppActiveTick,
    onBroadcastCellAppDataChanged.id: onBroadcastCellAppDataChanged,
    onBroadcastGlobalDataChanged.id: onBroadcastGlobalDataChanged,
    onCreateCellEntityFromBaseapp.id: onCreateCellEntityFromBaseapp,
    onCreateCellEntityInNewSpaceFromBaseapp.id: onCreateCellEntityInNewSpaceFromBaseapp,
    onDbmgrInitCompleted.id: onDbmgrInitCompleted,
    onDestroyCellEntityFromBaseapp.id: onDestroyCellEntityFromBaseapp,
    onEntityCall.id: onEntityCall,
    onExecuteRawDatabaseCommandCB.id: onExecuteRawDatabaseCommandCB,
    onExecScriptCommand.id: onExecScriptCommand,
    onGetEntityAppFromDbmgr.id: onGetEntityAppFromDbmgr,
    onGetWitnessFromBase.id: onGetWitnessFromBase,
    onLookApp.id: onLookApp,
    onLoseWitness.id: onLoseWitness,
    onRegisterNewApp.id: onRegisterNewApp,
    onRemoteCallMethodFromClient.id: onRemoteCallMethodFromClient,
    onRemoteMethodCall.id: onRemoteMethodCall,
    onRemoteRealMethodCall.id: onRemoteRealMethodCall,
    onReqAllocEntityID.id: onReqAllocEntityID,
    onReqCloseServer.id: onReqCloseServer,
    onRestoreSpaceInCellFromBaseapp.id: onRestoreSpaceInCellFromBaseapp,
    onUpdateDataFromClient.id: onUpdateDataFromClient,
    onUpdateDataFromClientForControlledEntity.id: onUpdateDataFromClientForControlledEntity,
    onUpdateGhostPropertys.id: onUpdateGhostPropertys,
    onUpdateGhostVolatileData.id: onUpdateGhostVolatileData,
    queryLoad.id: queryLoad,
    queryWatcher.id: queryWatcher,
    reqBackupEntityCellData.id: reqBackupEntityCellData,
    reqCloseServer.id: reqCloseServer,
    reqKillServer.id: reqKillServer,
    reqSetFlags.id: reqSetFlags,
    reqTeleportToCellApp.id: reqTeleportToCellApp,
    reqTeleportToCellAppCB.id: reqTeleportToCellAppCB,
    reqTeleportToCellAppOver.id: reqTeleportToCellAppOver,
    reqWriteToDBFromBaseapp.id: reqWriteToDBFromBaseapp,
    requestRestore.id: requestRestore,
    setPosition_XZ_float.id: setPosition_XZ_float,
    setPosition_XZ_int.id: setPosition_XZ_int,
    setPosition_XYZ_float.id: setPosition_XYZ_float,
    setPosition_XYZ_int.id: setPosition_XYZ_int,
    setSpaceViewer.id: setSpaceViewer,
    startProfile.id: startProfile,
}

# All exports sorted alphabetically
__all__ = [
    "SPEC_BY_ID",
    "forwardEntityMessageToCellappFromClient",
    "lookApp",
    "onAppActiveTick",
    "onBroadcastCellAppDataChanged",
    "onBroadcastGlobalDataChanged",
    "onCreateCellEntityFromBaseapp",
    "onCreateCellEntityInNewSpaceFromBaseapp",
    "onDbmgrInitCompleted",
    "onDestroyCellEntityFromBaseapp",
    "onEntityCall",
    "onExecScriptCommand",
    "onExecuteRawDatabaseCommandCB",
    "onGetEntityAppFromDbmgr",
    "onGetWitnessFromBase",
    "onLookApp",
    "onLoseWitness",
    "onRegisterNewApp",
    "onRemoteCallMethodFromClient",
    "onRemoteMethodCall",
    "onRemoteRealMethodCall",
    "onReqAllocEntityID",
    "onReqCloseServer",
    "onRestoreSpaceInCellFromBaseapp",
    "onUpdateDataFromClient",
    "onUpdateDataFromClientForControlledEntity",
    "onUpdateGhostPropertys",
    "onUpdateGhostVolatileData",
    "queryLoad",
    "queryWatcher",
    "reqBackupEntityCellData",
    "reqCloseServer",
    "reqKillServer",
    "reqSetFlags",
    "reqTeleportToCellApp",
    "reqTeleportToCellAppCB",
    "reqTeleportToCellAppOver",
    "reqWriteToDBFromBaseapp",
    "requestRestore",
    "setPosition_XYZ_float",
    "setPosition_XYZ_int",
    "setPosition_XZ_float",
    "setPosition_XZ_int",
    "setSpaceViewer",
    "startProfile",
]
