import logging
from typing import Type

from enki.net import msgspec

from .base import Handler, HandlerResult
from .ehandler import *
from .sdhandler import *
from .strmhandler import *
from .ghandler import *

from . import machinehandler, interfaceshandler, dbmgrhandler

logger = logging.getLogger(__name__)


E_HANDLER_CLS_BY_MSG_ID: dict[int, Type[EntityHandler]] = {
    msgspec.app.client.onUpdatePropertys.id: OnUpdatePropertysHandler,
    msgspec.app.client.onUpdatePropertysOptimized.id: OnUpdatePropertysOptimizedHandler,

    msgspec.app.client.onRemoteMethodCall.id: OnRemoteMethodCallHandler,
    msgspec.app.client.onRemoteMethodCallOptimized.id: OnRemoteMethodCallOptimizedHandler,

    msgspec.app.client.onCreatedProxies.id: OnCreatedProxiesHandler,
    msgspec.app.client.onEntityDestroyed.id: OnEntityDestroyedHandler,
    msgspec.app.client.onEntityEnterWorld.id: OnEntityEnterWorldHandler,
    msgspec.app.client.onEntityLeaveWorld.id: OnEntityLeaveWorldHandler,
    msgspec.app.client.onEntityLeaveWorldOptimized.id: OnEntityLeaveWorldOptimizedHandler,
    msgspec.app.client.onEntityEnterSpace.id: OnEntityEnterSpaceHandler,
    msgspec.app.client.onEntityLeaveSpace.id: OnEntityLeaveSpaceHandler,

    msgspec.app.client.onSetEntityPosAndDir.id: OnSetEntityPosAndDirHandler,

    msgspec.app.client.onUpdateBasePos.id: OnUpdateBasePosHandler,
    msgspec.app.client.onUpdateBaseDir.id: OnUpdateBaseDirHandler,
    msgspec.app.client.onUpdateBasePosXZ.id: OnUpdateBasePosXZHandler,

    msgspec.app.client.onUpdateData.id: OnUpdateDataHandler,

    msgspec.app.client.onUpdateData_ypr.id: OnUpdateData_YPR_Handler,
    msgspec.app.client.onUpdateData_yp.id: OnUpdateData_YP_Handler,
    msgspec.app.client.onUpdateData_yr.id: OnUpdateData_YR_Handler,
    msgspec.app.client.onUpdateData_pr.id: OnUpdateData_PR_Handler,
    msgspec.app.client.onUpdateData_y.id: OnUpdateData_Y_Handler,
    msgspec.app.client.onUpdateData_p.id: OnUpdateData_P_Handler,
    msgspec.app.client.onUpdateData_r.id: OnUpdateData_R_Handler,

    msgspec.app.client.onUpdateData_xz.id: OnUpdateData_XZ_Handler,
    msgspec.app.client.onUpdateData_xz_ypr.id: OnUpdateData_XZ_YPR_Handler,
    msgspec.app.client.onUpdateData_xz_yp.id: OnUpdateData_XZ_YP_Handler,
    msgspec.app.client.onUpdateData_xz_yr.id: OnUpdateData_XZ_YR_Handler,
    msgspec.app.client.onUpdateData_xz_pr.id: OnUpdateData_XZ_PR_Handler,
    msgspec.app.client.onUpdateData_xz_y.id: OnUpdateData_XZ_Y_Handler,
    msgspec.app.client.onUpdateData_xz_p.id: OnUpdateData_XZ_P_Handler,
    msgspec.app.client.onUpdateData_xz_r.id: OnUpdateData_XZ_R_Handler,

    msgspec.app.client.onUpdateData_xyz.id: OnUpdateData_XYZ_Handler,
    msgspec.app.client.onUpdateData_xyz_ypr.id: OnUpdateData_XYZ_YPR_Handler,
    msgspec.app.client.onUpdateData_xyz_yp.id: OnUpdateData_XYZ_YP_Handler,
    msgspec.app.client.onUpdateData_xyz_yr.id: OnUpdateData_XYZ_YR_Handler,
    msgspec.app.client.onUpdateData_xyz_pr.id: OnUpdateData_XYZ_PR_Handler,
    msgspec.app.client.onUpdateData_xyz_y.id: OnUpdateData_XYZ_Y_Handler,
    msgspec.app.client.onUpdateData_xyz_p.id: OnUpdateData_XYZ_P_Handler,
    msgspec.app.client.onUpdateData_xyz_r.id: OnUpdateData_XYZ_R_Handler,

    msgspec.app.client.onUpdateData_ypr_optimized.id: OnUpdateData_YPR_OptimizedHandler,
    msgspec.app.client.onUpdateData_yp_optimized.id: OnUpdateData_YP_OptimizedHandler,
    msgspec.app.client.onUpdateData_yr_optimized.id: OnUpdateData_YR_OptimizedHandler,
    msgspec.app.client.onUpdateData_pr_optimized.id: OnUpdateData_PR_OptimizedHandler,
    msgspec.app.client.onUpdateData_y_optimized.id: OnUpdateData_Y_OptimizedHandler,
    msgspec.app.client.onUpdateData_p_optimized.id: OnUpdateData_P_OptimizedHandler,
    msgspec.app.client.onUpdateData_r_optimized.id: OnUpdateData_R_OptimizedHandler,

    msgspec.app.client.onUpdateData_xz_optimized.id: OnUpdateData_XZ_OptimizedHandler,
    msgspec.app.client.onUpdateData_xz_ypr_optimized.id: OnUpdateData_XZ_YPR_OptimizedHandler,
    msgspec.app.client.onUpdateData_xz_yp_optimized.id: OnUpdateData_XZ_YP_OptimizedHandler,
    msgspec.app.client.onUpdateData_xz_yr_optimized.id: OnUpdateData_XZ_YR_OptimizedHandler,
    msgspec.app.client.onUpdateData_xz_pr_optimized.id: OnUpdateData_XZ_PR_OptimizedHandler,
    msgspec.app.client.onUpdateData_xz_y_optimized.id: OnUpdateData_XZ_Y_OptimizedHandler,
    msgspec.app.client.onUpdateData_xz_p_optimized.id: OnUpdateData_XZ_P_OptimizedHandler,
    msgspec.app.client.onUpdateData_xz_r_optimized.id: OnUpdateData_XZ_R_OptimizedHandler,

    msgspec.app.client.onUpdateData_xyz_optimized.id: OnUpdateData_XYZ_OptimizedHandler,
    msgspec.app.client.onUpdateData_xyz_ypr_optimized.id: OnUpdateData_XYZ_YPR_OptimizedHandler,
    msgspec.app.client.onUpdateData_xyz_yp_optimized.id: OnUpdateData_XYZ_YP_OptimizedHandler,
    msgspec.app.client.onUpdateData_xyz_yr_optimized.id: OnUpdateData_XYZ_YR_OptimizedHandler,
    msgspec.app.client.onUpdateData_xyz_pr_optimized.id: OnUpdateData_XYZ_PR_OptimizedHandler,
    msgspec.app.client.onUpdateData_xyz_y_optimized.id: OnUpdateData_XYZ_Y_OptimizedHandler,
    msgspec.app.client.onUpdateData_xyz_p_optimized.id: OnUpdateData_XYZ_P_OptimizedHandler,
    msgspec.app.client.onUpdateData_xyz_r_optimized.id: OnUpdateData_XYZ_R_OptimizedHandler,

    msgspec.app.client.onControlEntity.id: OnControlEntityHandler,
}

# TODO: [2022-11-17 15:52 burov_alexey@mail.ru]:
# Хэндлеры ниже полностью реализованы, но нет проброса этих данных в игру.
# Но это односторонние обработчики, ничего на севрер не отправляют, с ними
# по проще должно быть
SD_HANDLER_CLS_BY_MSG_ID: dict[int, Type[SpaceDataHandler]] = {
    msgspec.app.client.initSpaceData.id: InitSpaceDataHandler,
    msgspec.app.client.setSpaceData.id: SetSpaceDataHandler,
    msgspec.app.client.delSpaceData.id: DelSpaceDataHandler,
}

STREAM_HANDLER_CLS_BY_MSG_ID: dict[int, Type[StreamDataHandler]] = {
    msgspec.app.client.onStreamDataStarted.id: OnStreamDataStartedHandler,
    msgspec.app.client.onStreamDataRecv.id: OnStreamDataRecvHandler,
    msgspec.app.client.onStreamDataCompleted.id: OnStreamDataCompletedHandler,
}

# Handlers by the server component name
SERVER_HANDLERS: dict[str, dict[int, Type[Handler]]] = {
    'machine': {
        msgspec.app.machine.onBroadcastInterface.id: machinehandler.OnBroadcastInterfaceHandler,
        msgspec.app.machine.onFindInterfaceAddr.id: machinehandler.OnFindInterfaceAddrHandler,
        msgspec.app.machine.queryComponentID.id: machinehandler.QueryComponentIDHandler,
    },
    'interfaces': {
        msgspec.app.interfaces.onRegisterNewApp.id: interfaceshandler.OnRegisterNewAppHandler,
    },
    'dbmgr': {
        msgspec.app.dbmgr.onRegisterNewApp.id: dbmgrhandler.OnRegisterNewAppHandler,
    },
}
