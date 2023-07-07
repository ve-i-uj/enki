from typing import Type

from enki.core import msgspec

from ..base import Handler, HandlerResult
from . import machinehandler, interfaceshandler, dbmgrhandler, loggerhandler, \
    cellappmgrhandler, baseappmgrhandler, cellapphandler, baseapphandler

# Handlers by the server component name
SERVER_HANDLERS: dict[str, dict[int, Type[Handler]]] = {
    'machine': {
        msgspec.app.machine.onBroadcastInterface.id: machinehandler.OnBroadcastInterfaceHandler,
        msgspec.app.machine.onFindInterfaceAddr.id: machinehandler.OnFindInterfaceAddrHandler,
        msgspec.app.machine.queryComponentID.id: machinehandler.QueryComponentIDHandler,
    },
    'interfaces': {
        msgspec.app.interfaces.onRegisterNewApp.id: interfaceshandler.OnRegisterNewAppHandler,
        msgspec.app.interfaces.onAppActiveTick.id: interfaceshandler.OnAppActiveTickHandler,
    },
    'dbmgr': {
        msgspec.app.dbmgr.onRegisterNewApp.id: dbmgrhandler.OnRegisterNewAppHandler,
        msgspec.app.dbmgr.onAppActiveTick.id: dbmgrhandler.OnAppActiveTickHandler,
        msgspec.app.dbmgr.onBroadcastGlobalDataChanged.id: dbmgrhandler.OnBroadcastGlobalDataChangedHandler,
        msgspec.app.dbmgr.syncEntityStreamTemplate.id: dbmgrhandler.SyncEntityStreamTemplateHandler,
        msgspec.app.dbmgr.entityAutoLoad.id: dbmgrhandler.EntityAutoLoadHandler,
    },
    'cellappmgr': {
        msgspec.app.cellappmgr.onAppActiveTick.id: cellappmgrhandler.OnAppActiveTickHandler,
        msgspec.app.cellappmgr.onRegisterNewApp.id: cellappmgrhandler.OnRegisterNewAppHandler,
        msgspec.app.cellappmgr.lookApp.id: cellappmgrhandler.LookAppHandler,
        msgspec.app.cellappmgr.updateCellapp.id: cellappmgrhandler.UpdateCellappHandler,
        msgspec.app.cellappmgr.reqCreateCellEntityInNewSpace.id: cellappmgrhandler.ReqCreateCellEntityInNewSpaceHandler,
        msgspec.app.cellappmgr.updateSpaceData.id: cellappmgrhandler.UpdateSpaceDataHandler,
    },
    'baseappmgr': {
        msgspec.app.baseappmgr.onAppActiveTick.id: baseappmgrhandler.OnAppActiveTickHandler,
        msgspec.app.baseappmgr.onRegisterNewApp.id: baseappmgrhandler.OnRegisterNewAppHandler,
        msgspec.app.baseappmgr.updateBaseapp.id: baseappmgrhandler.UpdateBaseappHandler,
        msgspec.app.baseappmgr.onBaseappInitProgress.id: baseappmgrhandler.OnBaseappInitProgressHandler,
        msgspec.app.baseappmgr.reqCreateEntityAnywhere.id: baseappmgrhandler.ReqCreateEntityAnywhereHandler,
    },
    'logger': {
        msgspec.app.logger.writeLog.id: loggerhandler.WriteLogHandler,
        msgspec.app.logger.onRegisterNewApp.id: loggerhandler.OnRegisterNewAppHandler,
        msgspec.app.logger.onAppActiveTick.id: loggerhandler.OnAppActiveTickHandler,
    },
    'cellapp': {
        msgspec.app.cellapp.onDbmgrInitCompleted.id: cellapphandler.OnDbmgrInitCompletedHandler,
        msgspec.app.cellapp.onAppActiveTick.id: cellapphandler.OnAppActiveTickHandler,
        msgspec.app.cellapp.onBroadcastCellAppDataChanged.id: cellapphandler.OnBroadcastCellAppDataChangedHandler,
        msgspec.app.cellapp.onCreateCellEntityInNewSpaceFromBaseapp.id: cellapphandler.OnCreateCellEntityInNewSpaceFromBaseappHandler,
        msgspec.app.cellapp.onGetEntityAppFromDbmgr.id: cellapphandler.OnGetEntityAppFromDbmgrHandler,
        msgspec.app.cellapp.onBroadcastGlobalDataChanged.id: cellapphandler.OnBroadcastGlobalDataChangedHandler,
        msgspec.app.cellapp.onCreateCellEntityFromBaseapp.id: cellapphandler.OnCreateCellEntityFromBaseappHandler,
    },
    'baseapp': {
        msgspec.app.baseapp.onCreateEntityAnywhere.id: baseapphandler.OnCreateEntityAnywhereHandler,
        msgspec.app.baseapp.onDbmgrInitCompleted.id: baseapphandler.OnDbmgrInitCompletedHandler,
        msgspec.app.baseapp.onEntityAutoLoadCBFromDBMgr.id: baseapphandler.OnEntityAutoLoadCBFromDBMgrHandler,
        msgspec.app.baseapp.onBroadcastGlobalDataChanged.id: baseapphandler.OnBroadcastGlobalDataChangedHandler,
        msgspec.app.baseapp.onAppActiveTick.id: baseapphandler.OnAppActiveTickHandler,
        msgspec.app.baseapp.onRegisterNewApp.id: baseapphandler.OnRegisterNewAppHandler,
        msgspec.app.baseapp.onEntityGetCell.id: baseapphandler.OnEntityGetCellHandler,
    },
}
