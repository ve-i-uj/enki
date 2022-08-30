import logging
from typing import Type

from enki import descr
from enki.interface import IMessage

from .base import IHandler, HandlerResult
from .ehandler import *
from .sdhandler import *

logger = logging.getLogger(__name__)


E_HANDLER_CLS_BY_MSG_ID: dict[int, Type[EntityHandler]] = {
    descr.app.client.onUpdatePropertys.id: OnUpdatePropertysHandler,
    descr.app.client.onUpdatePropertysOptimized.id: OnUpdatePropertysOptimizedHandler,

    descr.app.client.onRemoteMethodCall.id: OnRemoteMethodCallHandler,

    descr.app.client.onCreatedProxies.id: OnCreatedProxiesHandler,
    descr.app.client.onEntityDestroyed.id: OnEntityDestroyedHandler,
    descr.app.client.onEntityEnterWorld.id: OnEntityEnterWorldHandler,
    descr.app.client.onEntityLeaveWorld.id: OnEntityLeaveWorldHandler,
    descr.app.client.onEntityLeaveWorldOptimized.id: OnEntityLeaveWorldOptimizedHandler,
    descr.app.client.onEntityEnterSpace.id: OnEntityEnterSpaceHandler,
    descr.app.client.onEntityLeaveSpace.id: OnEntityLeaveSpaceHandler,

    descr.app.client.onSetEntityPosAndDir.id: OnSetEntityPosAndDirHandler,

    descr.app.client.onUpdateBasePos.id: OnUpdateBasePosHandler,
    descr.app.client.onUpdateBasePosXZ.id: OnUpdateBasePosXZHandler,

    descr.app.client.onUpdateData_ypr.id: OnUpdateData_YPR_Handler,
    descr.app.client.onUpdateData_yp.id: OnUpdateData_YP_Handler,
    descr.app.client.onUpdateData_yr.id: OnUpdateData_YR_Handler,
    descr.app.client.onUpdateData_pr.id: OnUpdateData_PR_Handler,
    descr.app.client.onUpdateData_y.id: OnUpdateData_Y_Handler,
    descr.app.client.onUpdateData_p.id: OnUpdateData_P_Handler,
    descr.app.client.onUpdateData_r.id: OnUpdateData_R_Handler,

    descr.app.client.onUpdateData_xz.id: OnUpdateData_XZ_Handler,
    descr.app.client.onUpdateData_xz_ypr.id: OnUpdateData_XZ_YPR_Handler,
    descr.app.client.onUpdateData_xz_yp.id: OnUpdateData_XZ_YP_Handler,
    descr.app.client.onUpdateData_xz_yr.id: OnUpdateData_XZ_YR_Handler,
    descr.app.client.onUpdateData_xz_pr.id: OnUpdateData_XZ_PR_Handler,
    descr.app.client.onUpdateData_xz_y.id: OnUpdateData_XZ_Y_Handler,
    descr.app.client.onUpdateData_xz_p.id: OnUpdateData_XZ_P_Handler,
    descr.app.client.onUpdateData_xz_r.id: OnUpdateData_XZ_R_Handler,

    descr.app.client.onUpdateData_xyz.id: OnUpdateData_XYZ_Handler,
    descr.app.client.onUpdateData_xyz_ypr.id: OnUpdateData_XYZ_YPR_Handler,
    descr.app.client.onUpdateData_xyz_yp.id: OnUpdateData_XYZ_YP_Handler,
    descr.app.client.onUpdateData_xyz_yr.id: OnUpdateData_XYZ_YR_Handler,
    descr.app.client.onUpdateData_xyz_pr.id: OnUpdateData_XYZ_PR_Handler,
    descr.app.client.onUpdateData_xyz_y.id: OnUpdateData_XYZ_Y_Handler,
    descr.app.client.onUpdateData_xyz_p.id: OnUpdateData_XYZ_P_Handler,
    descr.app.client.onUpdateData_xyz_r.id: OnUpdateData_XYZ_R_Handler,

    descr.app.client.onUpdateData_y_optimized.id: OnUpdateData_Y_OptimizedHandler,
    descr.app.client.onUpdateData_p_optimized.id: OnUpdateData_P_OptimizedHandler,
    descr.app.client.onUpdateData_r_optimized.id: OnUpdateData_R_OptimizedHandler,
}

S_HANDLER_CLS_BY_MSG_ID: dict[int, Type[SpaceDataHandler]] = {
    descr.app.client.initSpaceData.id: InitSpaceDataHandler,
    descr.app.client.setSpaceData.id: SetSpaceDataHandler,
    descr.app.client.delSpaceData.id: DelSpaceDataHandler,
}
