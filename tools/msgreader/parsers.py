"""Парсеры сообщений по id-сообщения."""

from enki import msgspec
from enki.kbeenum import ComponentType
from enki.msg.msg_descr import MsgId
from enki.msg_parser import machine_msg_parser
from enki.msg_parser.imsg_parser import IMsgParser

MESSAGE_PARSERS_BY_COMP_TYPE: dict[
    ComponentType, dict[MsgId, type[IMsgParser]]
] = {
    ComponentType.MACHINE: {
        msgspec.machine.onBroadcastInterface.id: machine_msg_parser.OnBroadcastInterfaceMsgParser,
        msgspec.machine.onFindInterfaceAddr.id: machine_msg_parser.OnFindInterfaceAddrMsgParser,
        msgspec.machine.queryComponentID.id: machine_msg_parser.QueryComponentIDMsgParser,
        msgspec.machine.onLookApp.id: machine_msg_parser.OnLookAppMsgParser,
    },
    # "interfaces": {
    #     msgspec.interfaces.onRegisterNewApp.id: interfaceshandler.OnRegisterNewAppHandler,
    #     msgspec.interfaces.onAppActiveTick.id: interfaceshandler.OnAppActiveTickHandler,
    # },
    # "dbmgr": {
    #     msgspec.dbmgr.onRegisterNewApp.id: dbmgrhandler.OnRegisterNewAppHandler,
    #     msgspec.dbmgr.onAppActiveTick.id: dbmgrhandler.OnAppActiveTickHandler,
    #     msgspec.dbmgr.onBroadcastGlobalDataChanged.id: dbmgrhandler.OnBroadcastGlobalDataChangedHandler,
    #     msgspec.dbmgr.syncEntityStreamTemplate.id: dbmgrhandler.SyncEntityStreamTemplateHandler,
    #     msgspec.dbmgr.entityAutoLoad.id: dbmgrhandler.EntityAutoLoadHandler,
    # },
    # "cellappmgr": {
    #     msgspec.cellappmgr.onAppActiveTick.id: cellappmgrhandler.OnAppActiveTickHandler,
    #     msgspec.cellappmgr.onRegisterNewApp.id: cellappmgrhandler.OnRegisterNewAppHandler,
    #     msgspec.cellappmgr.lookApp.id: cellappmgrhandler.LookAppHandler,
    #     msgspec.cellappmgr.updateCellapp.id: cellappmgrhandler.UpdateCellappHandler,
    #     msgspec.cellappmgr.reqCreateCellEntityInNewSpace.id: cellappmgrhandler.ReqCreateCellEntityInNewSpaceHandler,
    #     msgspec.cellappmgr.updateSpaceData.id: cellappmgrhandler.UpdateSpaceDataHandler,
    # },
    # "baseappmgr": {
    #     msgspec.baseappmgr.onAppActiveTick.id: baseappmgrhandler.OnAppActiveTickHandler,
    #     msgspec.baseappmgr.onRegisterNewApp.id: baseappmgrhandler.OnRegisterNewAppHandler,
    #     msgspec.baseappmgr.updateBaseapp.id: baseappmgrhandler.UpdateBaseappHandler,
    #     msgspec.baseappmgr.onBaseappInitProgress.id: baseappmgrhandler.OnBaseappInitProgressHandler,
    #     msgspec.baseappmgr.reqCreateEntityAnywhere.id: baseappmgrhandler.ReqCreateEntityAnywhereHandler,
    # },
    # "logger": {
    #     msgspec.logger.writeLog.id: loggerhandler.WriteLogHandler,
    #     msgspec.logger.onRegisterNewApp.id: loggerhandler.OnRegisterNewAppHandler,
    #     msgspec.logger.onAppActiveTick.id: loggerhandler.OnAppActiveTickHandler,
    # },
    # "cellapp": {
    #     msgspec.cellapp.onDbmgrInitCompleted.id: cellapphandler.OnDbmgrInitCompletedHandler,
    #     msgspec.cellapp.onAppActiveTick.id: cellapphandler.OnAppActiveTickHandler,
    #     msgspec.cellapp.onBroadcastCellAppDataChanged.id: cellapphandler.OnBroadcastCellAppDataChangedHandler,
    #     msgspec.cellapp.onCreateCellEntityInNewSpaceFromBaseapp.id: cellapphandler.OnCreateCellEntityInNewSpaceFromBaseappHandler,
    #     msgspec.cellapp.onGetEntityAppFromDbmgr.id: cellapphandler.OnGetEntityAppFromDbmgrHandler,
    #     msgspec.cellapp.onBroadcastGlobalDataChanged.id: cellapphandler.OnBroadcastGlobalDataChangedHandler,
    #     msgspec.cellapp.onCreateCellEntityFromBaseapp.id: cellapphandler.OnCreateCellEntityFromBaseappHandler,
    #     msgspec.cellapp.onRegisterNewApp.id: cellapphandler.OnRegisterNewAppHandler,
    # },
    # "baseapp": {
    #     msgspec.baseapp.onCreateEntityAnywhere.id: baseapphandler.OnCreateEntityAnywhereHandler,
    #     msgspec.baseapp.onDbmgrInitCompleted.id: baseapphandler.OnDbmgrInitCompletedHandler,
    #     msgspec.baseapp.onEntityAutoLoadCBFromDBMgr.id: baseapphandler.OnEntityAutoLoadCBFromDBMgrHandler,
    #     msgspec.baseapp.onBroadcastGlobalDataChanged.id: baseapphandler.OnBroadcastGlobalDataChangedHandler,
    #     msgspec.baseapp.onAppActiveTick.id: baseapphandler.OnAppActiveTickHandler,
    #     msgspec.baseapp.onRegisterNewApp.id: baseapphandler.OnRegisterNewAppHandler,
    #     msgspec.baseapp.onEntityGetCell.id: baseapphandler.OnEntityGetCellHandler,
    #     msgspec.baseapp.onGetEntityAppFromDbmgr.id: baseapphandler.OnGetEntityAppFromDbmgrHandler,
    # },
    # "loginapp": {
    #     msgspec.loginapp.onDbmgrInitCompleted.id: loginapphandler.OnDbmgrInitCompletedHandler,
    #     msgspec.loginapp.onBaseappInitProgress.id: loginapphandler.OnBaseappInitProgressHandler,
    #     msgspec.loginapp.onAppActiveTick.id: loginapphandler.OnAppActiveTickHandler,
    # },
    # "supervisor": {
    #     msgspec.supervisor.onStopComponent.id: supervisorhandler.OnStopComponentHandler,
    # },
}
