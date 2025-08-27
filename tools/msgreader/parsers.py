"""Парсеры сообщений по id-сообщения."""

from enki import msgspec
from enki.kbeenum import ComponentType
from enki.msg.msg_descr import MsgId
from enki.msg_parser import (
    baseapp_msg_parser,
    baseappmgr_msg_parser,
    cellapp_msg_parser,
    cellappmgr_msg_parser,
    dbmgr_msg_parser,
    interfaces_msg_parser,
    logger_msg_parser,
    loginapp_msg_parser,
    machine_msg_parser,
    supervisor_msg_parser,
)
from enki.msg_parser.client_msg_parser import client_msg_pasrser
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
    ComponentType.INTERFACES: {
        msgspec.interfaces.onRegisterNewApp.id: interfaces_msg_parser.OnRegisterNewAppMsgParser,
        msgspec.interfaces.onAppActiveTick.id: interfaces_msg_parser.OnAppActiveTickMsgParser,
        msgspec.interfaces.onAccountLogin.id: interfaces_msg_parser.OnAccountLoginMsgParser,
    },
    ComponentType.DBMGR: {
        msgspec.dbmgr.onRegisterNewApp.id: dbmgr_msg_parser.OnRegisterNewAppMsgParser,
        msgspec.dbmgr.onAppActiveTick.id: dbmgr_msg_parser.OnAppActiveTickMsgParser,
        msgspec.dbmgr.onBroadcastGlobalDataChanged.id: dbmgr_msg_parser.OnBroadcastGlobalDataChangedMsgParser,
        msgspec.dbmgr.syncEntityStreamTemplate.id: dbmgr_msg_parser.SyncEntityStreamTemplateMsgParser,
        msgspec.dbmgr.entityAutoLoad.id: dbmgr_msg_parser.EntityAutoLoadMsgParser,
        msgspec.dbmgr.onAccountLogin.id: dbmgr_msg_parser.OnAccountLoginMsgParser,
        msgspec.dbmgr.onLoginAccountCBBFromInterfaces.id: dbmgr_msg_parser.OnLoginAccountCBBFromInterfacesMsgParser,
    },
    ComponentType.CELLAPPMGR: {
        msgspec.cellappmgr.onAppActiveTick.id: cellappmgr_msg_parser.OnAppActiveTickMsgParser,
        msgspec.cellappmgr.onRegisterNewApp.id: cellappmgr_msg_parser.OnRegisterNewAppMsgParser,
        msgspec.cellappmgr.lookApp.id: cellappmgr_msg_parser.LookAppMsgParser,
        msgspec.cellappmgr.updateCellapp.id: cellappmgr_msg_parser.UpdateCellappMsgParser,
        msgspec.cellappmgr.reqCreateCellEntityInNewSpace.id: cellappmgr_msg_parser.ReqCreateCellEntityInNewSpaceMsgParser,
        msgspec.cellappmgr.updateSpaceData.id: cellappmgr_msg_parser.UpdateSpaceDataMsgParser,
    },
    ComponentType.BASEAPPMGR: {
        msgspec.baseappmgr.onAppActiveTick.id: baseappmgr_msg_parser.OnAppActiveTickMsgParser,
        msgspec.baseappmgr.onRegisterNewApp.id: baseappmgr_msg_parser.OnRegisterNewAppMsgParser,
        msgspec.baseappmgr.updateBaseapp.id: baseappmgr_msg_parser.UpdateBaseappMsgParser,
        msgspec.baseappmgr.onBaseappInitProgress.id: baseappmgr_msg_parser.OnBaseappInitProgressMsgParser,
        msgspec.baseappmgr.reqCreateEntityAnywhere.id: baseappmgr_msg_parser.ReqCreateEntityAnywhereMsgParser,
        msgspec.baseappmgr.onPendingAccountGetBaseappAddr.id: baseappmgr_msg_parser.OnPendingAccountGetBaseappAddrMsgParser,
    },
    ComponentType.LOGGER: {
        msgspec.logger.writeLog.id: logger_msg_parser.WriteLogMsgParser,
        msgspec.logger.onRegisterNewApp.id: logger_msg_parser.OnRegisterNewAppMsgParser,
        msgspec.logger.onAppActiveTick.id: logger_msg_parser.OnAppActiveTickMsgParser,
    },
    ComponentType.CELLAPP: {
        msgspec.cellapp.onDbmgrInitCompleted.id: cellapp_msg_parser.OnDbmgrInitCompletedMsgParser,
        msgspec.cellapp.onAppActiveTick.id: cellapp_msg_parser.OnAppActiveTickMsgParser,
        msgspec.cellapp.onBroadcastCellAppDataChanged.id: cellapp_msg_parser.OnBroadcastCellAppDataChangedMsgParser,
        msgspec.cellapp.onCreateCellEntityInNewSpaceFromBaseapp.id: cellapp_msg_parser.OnCreateCellEntityInNewSpaceFromBaseappMsgParser,
        msgspec.cellapp.onGetEntityAppFromDbmgr.id: cellapp_msg_parser.OnGetEntityAppFromDbmgrMsgParser,
        msgspec.cellapp.onBroadcastGlobalDataChanged.id: cellapp_msg_parser.OnBroadcastGlobalDataChangedMsgParser,
        msgspec.cellapp.onCreateCellEntityFromBaseapp.id: cellapp_msg_parser.OnCreateCellEntityFromBaseappMsgParser,
        msgspec.cellapp.onRegisterNewApp.id: cellapp_msg_parser.OnRegisterNewAppMsgParser,
    },
    ComponentType.BASEAPP: {
        msgspec.baseapp.onCreateEntityAnywhere.id: baseapp_msg_parser.OnCreateEntityAnywhereMsgParser,
        msgspec.baseapp.onDbmgrInitCompleted.id: baseapp_msg_parser.OnDbmgrInitCompletedMsgParser,
        msgspec.baseapp.onEntityAutoLoadCBFromDBMgr.id: baseapp_msg_parser.OnEntityAutoLoadCBFromDBMgrMsgParser,
        msgspec.baseapp.onBroadcastGlobalDataChanged.id: baseapp_msg_parser.OnBroadcastGlobalDataChangedMsgParser,
        msgspec.baseapp.onAppActiveTick.id: baseapp_msg_parser.OnAppActiveTickMsgParser,
        msgspec.baseapp.onRegisterNewApp.id: baseapp_msg_parser.OnRegisterNewAppMsgParser,
        msgspec.baseapp.onEntityGetCell.id: baseapp_msg_parser.OnEntityGetCellMsgParser,
        msgspec.baseapp.onGetEntityAppFromDbmgr.id: baseapp_msg_parser.OnGetEntityAppFromDbmgrMsgParser,
        msgspec.baseapp.registerPendingLogin.id: baseapp_msg_parser.RegisterPendingLoginMsgParser,
    },
    ComponentType.LOGINAPP: {
        msgspec.loginapp.onDbmgrInitCompleted.id: loginapp_msg_parser.OnDbmgrInitCompletedMsgParser,
        msgspec.loginapp.onBaseappInitProgress.id: loginapp_msg_parser.OnBaseappInitProgressMsgParser,
        msgspec.loginapp.onAppActiveTick.id: loginapp_msg_parser.OnAppActiveTickMsgParser,
        msgspec.loginapp.login.id: loginapp_msg_parser.LoginMsgParser,
        msgspec.loginapp.onLoginAccountQueryResultFromDbmgr.id: loginapp_msg_parser.OnLoginAccountQueryResultFromDbmgrMsgParser,
        msgspec.loginapp.onLoginAccountQueryBaseappAddrFromBaseappmgr.id: loginapp_msg_parser.OnLoginAccountQueryBaseappAddrFromBaseappmgrMsgParser,
    },
    ComponentType.SUPERVISOR: {
        msgspec.supervisor.onStopComponent.id: supervisor_msg_parser.OnStopComponentMsgParser,
    },
    ComponentType.CLIENT: {
        msgspec.client.onLoginSuccessfully.id: client_msg_pasrser.OnLoginSuccessfullyMsgParser,
        msgspec.client.onLoginFailed.id: client_msg_pasrser.OnLoginFailedMsgParser,
        msgspec.client.onScriptVersionNotMatch.id: client_msg_pasrser.OnScriptVersionNotMatchMsgParser,
        msgspec.client.onVersionNotMatch.id: client_msg_pasrser.OnVersionNotMatchMsgParser,
        msgspec.client.onHelloCB.id: client_msg_pasrser.OnHelloCBMsgParser,
        msgspec.client.onKicked.id: client_msg_pasrser.OnKickedMsgParser,
    },
}
