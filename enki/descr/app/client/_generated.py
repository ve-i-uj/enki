"""Messages of Client."""

from enki import kbetype
from .. import _message

onReloginBaseappFailed = _message.MessageDescr(
    id=8,
    name='Client::onReloginBaseappFailed',
    args_type=_message.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT16,
    ),
    desc=''
)

onEntityLeaveWorldOptimized = _message.MessageDescr(
    id=9,
    name='Client::onEntityLeaveWorldOptimized',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onRemoteMethodCallOptimized = _message.MessageDescr(
    id=10,
    name='Client::onRemoteMethodCallOptimized',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdatePropertysOptimized = _message.MessageDescr(
    id=11,
    name='Client::onUpdatePropertysOptimized',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onSetEntityPosAndDir = _message.MessageDescr(
    id=12,
    name='Client::onSetEntityPosAndDir',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateBasePos = _message.MessageDescr(
    id=13,
    name='Client::onUpdateBasePos',
    args_type=_message.MsgArgsType.FIXED,
    field_types=(
        kbetype.FLOAT,
        kbetype.FLOAT,
        kbetype.FLOAT,
    ),
    desc=''
)

onUpdateBaseDir = _message.MessageDescr(
    id=14,
    name='Client::onUpdateBaseDir',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateBasePosXZ = _message.MessageDescr(
    id=15,
    name='Client::onUpdateBasePosXZ',
    args_type=_message.MsgArgsType.FIXED,
    field_types=(
        kbetype.FLOAT,
        kbetype.FLOAT,
    ),
    desc=''
)

onUpdateData = _message.MessageDescr(
    id=16,
    name='Client::onUpdateData',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_ypr = _message.MessageDescr(
    id=17,
    name='Client::onUpdateData_ypr',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_yp = _message.MessageDescr(
    id=18,
    name='Client::onUpdateData_yp',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_yr = _message.MessageDescr(
    id=19,
    name='Client::onUpdateData_yr',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_pr = _message.MessageDescr(
    id=20,
    name='Client::onUpdateData_pr',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_y = _message.MessageDescr(
    id=21,
    name='Client::onUpdateData_y',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_p = _message.MessageDescr(
    id=22,
    name='Client::onUpdateData_p',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_r = _message.MessageDescr(
    id=23,
    name='Client::onUpdateData_r',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz = _message.MessageDescr(
    id=24,
    name='Client::onUpdateData_xz',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_ypr = _message.MessageDescr(
    id=25,
    name='Client::onUpdateData_xz_ypr',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_yp = _message.MessageDescr(
    id=26,
    name='Client::onUpdateData_xz_yp',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_yr = _message.MessageDescr(
    id=27,
    name='Client::onUpdateData_xz_yr',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_pr = _message.MessageDescr(
    id=28,
    name='Client::onUpdateData_xz_pr',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_y = _message.MessageDescr(
    id=29,
    name='Client::onUpdateData_xz_y',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_p = _message.MessageDescr(
    id=30,
    name='Client::onUpdateData_xz_p',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_r = _message.MessageDescr(
    id=31,
    name='Client::onUpdateData_xz_r',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz = _message.MessageDescr(
    id=32,
    name='Client::onUpdateData_xyz',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_ypr = _message.MessageDescr(
    id=33,
    name='Client::onUpdateData_xyz_ypr',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_yp = _message.MessageDescr(
    id=34,
    name='Client::onUpdateData_xyz_yp',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_yr = _message.MessageDescr(
    id=35,
    name='Client::onUpdateData_xyz_yr',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_pr = _message.MessageDescr(
    id=36,
    name='Client::onUpdateData_xyz_pr',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_y = _message.MessageDescr(
    id=37,
    name='Client::onUpdateData_xyz_y',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_p = _message.MessageDescr(
    id=38,
    name='Client::onUpdateData_xyz_p',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_r = _message.MessageDescr(
    id=39,
    name='Client::onUpdateData_xyz_r',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_ypr_optimized = _message.MessageDescr(
    id=40,
    name='Client::onUpdateData_ypr_optimized',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_yp_optimized = _message.MessageDescr(
    id=41,
    name='Client::onUpdateData_yp_optimized',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_yr_optimized = _message.MessageDescr(
    id=42,
    name='Client::onUpdateData_yr_optimized',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_pr_optimized = _message.MessageDescr(
    id=43,
    name='Client::onUpdateData_pr_optimized',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_y_optimized = _message.MessageDescr(
    id=44,
    name='Client::onUpdateData_y_optimized',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_p_optimized = _message.MessageDescr(
    id=45,
    name='Client::onUpdateData_p_optimized',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_r_optimized = _message.MessageDescr(
    id=46,
    name='Client::onUpdateData_r_optimized',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_optimized = _message.MessageDescr(
    id=47,
    name='Client::onUpdateData_xz_optimized',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_ypr_optimized = _message.MessageDescr(
    id=48,
    name='Client::onUpdateData_xz_ypr_optimized',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_yp_optimized = _message.MessageDescr(
    id=49,
    name='Client::onUpdateData_xz_yp_optimized',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_yr_optimized = _message.MessageDescr(
    id=50,
    name='Client::onUpdateData_xz_yr_optimized',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_pr_optimized = _message.MessageDescr(
    id=51,
    name='Client::onUpdateData_xz_pr_optimized',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_y_optimized = _message.MessageDescr(
    id=52,
    name='Client::onUpdateData_xz_y_optimized',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_p_optimized = _message.MessageDescr(
    id=53,
    name='Client::onUpdateData_xz_p_optimized',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_r_optimized = _message.MessageDescr(
    id=54,
    name='Client::onUpdateData_xz_r_optimized',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_optimized = _message.MessageDescr(
    id=55,
    name='Client::onUpdateData_xyz_optimized',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_ypr_optimized = _message.MessageDescr(
    id=56,
    name='Client::onUpdateData_xyz_ypr_optimized',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_yp_optimized = _message.MessageDescr(
    id=57,
    name='Client::onUpdateData_xyz_yp_optimized',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_yr_optimized = _message.MessageDescr(
    id=58,
    name='Client::onUpdateData_xyz_yr_optimized',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_pr_optimized = _message.MessageDescr(
    id=59,
    name='Client::onUpdateData_xyz_pr_optimized',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_y_optimized = _message.MessageDescr(
    id=60,
    name='Client::onUpdateData_xyz_y_optimized',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_p_optimized = _message.MessageDescr(
    id=61,
    name='Client::onUpdateData_xyz_p_optimized',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_r_optimized = _message.MessageDescr(
    id=62,
    name='Client::onUpdateData_xyz_r_optimized',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onImportServerErrorsDescr = _message.MessageDescr(
    id=63,
    name='Client::onImportServerErrorsDescr',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onImportClientSDK = _message.MessageDescr(
    id=64,
    name='Client::onImportClientSDK',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

initSpaceData = _message.MessageDescr(
    id=65,
    name='Client::initSpaceData',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

setSpaceData = _message.MessageDescr(
    id=66,
    name='Client::setSpaceData',
    args_type=_message.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT32,
        kbetype.STRING,
        kbetype.STRING,
    ),
    desc=''
)

delSpaceData = _message.MessageDescr(
    id=67,
    name='Client::delSpaceData',
    args_type=_message.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT32,
        kbetype.STRING,
    ),
    desc=''
)

onReqAccountResetPasswordCB = _message.MessageDescr(
    id=68,
    name='Client::onReqAccountResetPasswordCB',
    args_type=_message.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT16,
    ),
    desc=''
)

onReqAccountBindEmailCB = _message.MessageDescr(
    id=69,
    name='Client::onReqAccountBindEmailCB',
    args_type=_message.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT16,
    ),
    desc=''
)

onReqAccountNewPasswordCB = _message.MessageDescr(
    id=70,
    name='Client::onReqAccountNewPasswordCB',
    args_type=_message.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT16,
    ),
    desc=''
)

onReloginBaseappSuccessfully = _message.MessageDescr(
    id=71,
    name='Client::onReloginBaseappSuccessfully',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onAppActiveTickCB = _message.MessageDescr(
    id=72,
    name='Client::onAppActiveTickCB',
    args_type=_message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

onCreateAccountResult = _message.MessageDescr(
    id=501,
    name='Client::onCreateAccountResult',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onLoginSuccessfully = _message.MessageDescr(
    id=502,
    name='Client::onLoginSuccessfully',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onLoginFailed = _message.MessageDescr(
    id=503,
    name='Client::onLoginFailed',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onCreatedProxies = _message.MessageDescr(
    id=504,
    name='Client::onCreatedProxies',
    args_type=_message.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT64,
        kbetype.INT32,
        kbetype.STRING,
    ),
    desc=''
)

onLoginBaseappFailed = _message.MessageDescr(
    id=505,
    name='Client::onLoginBaseappFailed',
    args_type=_message.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT16,
    ),
    desc=''
)

onRemoteMethodCall = _message.MessageDescr(
    id=506,
    name='Client::onRemoteMethodCall',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onEntityEnterWorld = _message.MessageDescr(
    id=507,
    name='Client::onEntityEnterWorld',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onEntityLeaveWorld = _message.MessageDescr(
    id=508,
    name='Client::onEntityLeaveWorld',
    args_type=_message.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT32,
    ),
    desc=''
)

onEntityEnterSpace = _message.MessageDescr(
    id=509,
    name='Client::onEntityEnterSpace',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onEntityLeaveSpace = _message.MessageDescr(
    id=510,
    name='Client::onEntityLeaveSpace',
    args_type=_message.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT32,
    ),
    desc=''
)

onUpdatePropertys = _message.MessageDescr(
    id=511,
    name='Client::onUpdatePropertys',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onEntityDestroyed = _message.MessageDescr(
    id=512,
    name='Client::onEntityDestroyed',
    args_type=_message.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT32,
    ),
    desc=''
)

onStreamDataStarted = _message.MessageDescr(
    id=514,
    name='Client::onStreamDataStarted',
    args_type=_message.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT16,
        kbetype.UINT32,
        kbetype.STRING,
    ),
    desc=''
)

onStreamDataRecv = _message.MessageDescr(
    id=515,
    name='Client::onStreamDataRecv',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onStreamDataCompleted = _message.MessageDescr(
    id=516,
    name='Client::onStreamDataCompleted',
    args_type=_message.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT16,
    ),
    desc=''
)

onKicked = _message.MessageDescr(
    id=517,
    name='Client::onKicked',
    args_type=_message.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT16,
    ),
    desc=''
)

onImportClientMessages = _message.MessageDescr(
    id=518,
    name='Client::onImportClientMessages',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onImportClientEntityDef = _message.MessageDescr(
    id=519,
    name='Client::onImportClientEntityDef',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onHelloCB = _message.MessageDescr(
    id=521,
    name='Client::onHelloCB',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onScriptVersionNotMatch = _message.MessageDescr(
    id=522,
    name='Client::onScriptVersionNotMatch',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onVersionNotMatch = _message.MessageDescr(
    id=523,
    name='Client::onVersionNotMatch',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onControlEntity = _message.MessageDescr(
    id=524,
    name='Client::onControlEntity',
    args_type=_message.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT32,
        kbetype.INT8,
    ),
    desc=''
)

SPEC_BY_ID = {
    onReloginBaseappFailed.id: onReloginBaseappFailed,
    onEntityLeaveWorldOptimized.id: onEntityLeaveWorldOptimized,
    onRemoteMethodCallOptimized.id: onRemoteMethodCallOptimized,
    onUpdatePropertysOptimized.id: onUpdatePropertysOptimized,
    onSetEntityPosAndDir.id: onSetEntityPosAndDir,
    onUpdateBasePos.id: onUpdateBasePos,
    onUpdateBaseDir.id: onUpdateBaseDir,
    onUpdateBasePosXZ.id: onUpdateBasePosXZ,
    onUpdateData.id: onUpdateData,
    onUpdateData_ypr.id: onUpdateData_ypr,
    onUpdateData_yp.id: onUpdateData_yp,
    onUpdateData_yr.id: onUpdateData_yr,
    onUpdateData_pr.id: onUpdateData_pr,
    onUpdateData_y.id: onUpdateData_y,
    onUpdateData_p.id: onUpdateData_p,
    onUpdateData_r.id: onUpdateData_r,
    onUpdateData_xz.id: onUpdateData_xz,
    onUpdateData_xz_ypr.id: onUpdateData_xz_ypr,
    onUpdateData_xz_yp.id: onUpdateData_xz_yp,
    onUpdateData_xz_yr.id: onUpdateData_xz_yr,
    onUpdateData_xz_pr.id: onUpdateData_xz_pr,
    onUpdateData_xz_y.id: onUpdateData_xz_y,
    onUpdateData_xz_p.id: onUpdateData_xz_p,
    onUpdateData_xz_r.id: onUpdateData_xz_r,
    onUpdateData_xyz.id: onUpdateData_xyz,
    onUpdateData_xyz_ypr.id: onUpdateData_xyz_ypr,
    onUpdateData_xyz_yp.id: onUpdateData_xyz_yp,
    onUpdateData_xyz_yr.id: onUpdateData_xyz_yr,
    onUpdateData_xyz_pr.id: onUpdateData_xyz_pr,
    onUpdateData_xyz_y.id: onUpdateData_xyz_y,
    onUpdateData_xyz_p.id: onUpdateData_xyz_p,
    onUpdateData_xyz_r.id: onUpdateData_xyz_r,
    onUpdateData_ypr_optimized.id: onUpdateData_ypr_optimized,
    onUpdateData_yp_optimized.id: onUpdateData_yp_optimized,
    onUpdateData_yr_optimized.id: onUpdateData_yr_optimized,
    onUpdateData_pr_optimized.id: onUpdateData_pr_optimized,
    onUpdateData_y_optimized.id: onUpdateData_y_optimized,
    onUpdateData_p_optimized.id: onUpdateData_p_optimized,
    onUpdateData_r_optimized.id: onUpdateData_r_optimized,
    onUpdateData_xz_optimized.id: onUpdateData_xz_optimized,
    onUpdateData_xz_ypr_optimized.id: onUpdateData_xz_ypr_optimized,
    onUpdateData_xz_yp_optimized.id: onUpdateData_xz_yp_optimized,
    onUpdateData_xz_yr_optimized.id: onUpdateData_xz_yr_optimized,
    onUpdateData_xz_pr_optimized.id: onUpdateData_xz_pr_optimized,
    onUpdateData_xz_y_optimized.id: onUpdateData_xz_y_optimized,
    onUpdateData_xz_p_optimized.id: onUpdateData_xz_p_optimized,
    onUpdateData_xz_r_optimized.id: onUpdateData_xz_r_optimized,
    onUpdateData_xyz_optimized.id: onUpdateData_xyz_optimized,
    onUpdateData_xyz_ypr_optimized.id: onUpdateData_xyz_ypr_optimized,
    onUpdateData_xyz_yp_optimized.id: onUpdateData_xyz_yp_optimized,
    onUpdateData_xyz_yr_optimized.id: onUpdateData_xyz_yr_optimized,
    onUpdateData_xyz_pr_optimized.id: onUpdateData_xyz_pr_optimized,
    onUpdateData_xyz_y_optimized.id: onUpdateData_xyz_y_optimized,
    onUpdateData_xyz_p_optimized.id: onUpdateData_xyz_p_optimized,
    onUpdateData_xyz_r_optimized.id: onUpdateData_xyz_r_optimized,
    onImportServerErrorsDescr.id: onImportServerErrorsDescr,
    onImportClientSDK.id: onImportClientSDK,
    initSpaceData.id: initSpaceData,
    setSpaceData.id: setSpaceData,
    delSpaceData.id: delSpaceData,
    onReqAccountResetPasswordCB.id: onReqAccountResetPasswordCB,
    onReqAccountBindEmailCB.id: onReqAccountBindEmailCB,
    onReqAccountNewPasswordCB.id: onReqAccountNewPasswordCB,
    onReloginBaseappSuccessfully.id: onReloginBaseappSuccessfully,
    onAppActiveTickCB.id: onAppActiveTickCB,
    onCreateAccountResult.id: onCreateAccountResult,
    onLoginSuccessfully.id: onLoginSuccessfully,
    onLoginFailed.id: onLoginFailed,
    onCreatedProxies.id: onCreatedProxies,
    onLoginBaseappFailed.id: onLoginBaseappFailed,
    onRemoteMethodCall.id: onRemoteMethodCall,
    onEntityEnterWorld.id: onEntityEnterWorld,
    onEntityLeaveWorld.id: onEntityLeaveWorld,
    onEntityEnterSpace.id: onEntityEnterSpace,
    onEntityLeaveSpace.id: onEntityLeaveSpace,
    onUpdatePropertys.id: onUpdatePropertys,
    onEntityDestroyed.id: onEntityDestroyed,
    onStreamDataStarted.id: onStreamDataStarted,
    onStreamDataRecv.id: onStreamDataRecv,
    onStreamDataCompleted.id: onStreamDataCompleted,
    onKicked.id: onKicked,
    onImportClientMessages.id: onImportClientMessages,
    onImportClientEntityDef.id: onImportClientEntityDef,
    onHelloCB.id: onHelloCB,
    onScriptVersionNotMatch.id: onScriptVersionNotMatch,
    onVersionNotMatch.id: onVersionNotMatch,
    onControlEntity.id: onControlEntity
}

__all__ = (
    'onReloginBaseappFailed', 'onEntityLeaveWorldOptimized', 'onRemoteMethodCallOptimized',
    'onUpdatePropertysOptimized', 'onSetEntityPosAndDir', 'onUpdateBasePos',
    'onUpdateBaseDir', 'onUpdateBasePosXZ', 'onUpdateData',
    'onUpdateData_ypr', 'onUpdateData_yp', 'onUpdateData_yr',
    'onUpdateData_pr', 'onUpdateData_y', 'onUpdateData_p',
    'onUpdateData_r', 'onUpdateData_xz', 'onUpdateData_xz_ypr',
    'onUpdateData_xz_yp', 'onUpdateData_xz_yr', 'onUpdateData_xz_pr',
    'onUpdateData_xz_y', 'onUpdateData_xz_p', 'onUpdateData_xz_r',
    'onUpdateData_xyz', 'onUpdateData_xyz_ypr', 'onUpdateData_xyz_yp',
    'onUpdateData_xyz_yr', 'onUpdateData_xyz_pr', 'onUpdateData_xyz_y',
    'onUpdateData_xyz_p', 'onUpdateData_xyz_r', 'onUpdateData_ypr_optimized',
    'onUpdateData_yp_optimized', 'onUpdateData_yr_optimized', 'onUpdateData_pr_optimized',
    'onUpdateData_y_optimized', 'onUpdateData_p_optimized', 'onUpdateData_r_optimized',
    'onUpdateData_xz_optimized', 'onUpdateData_xz_ypr_optimized', 'onUpdateData_xz_yp_optimized',
    'onUpdateData_xz_yr_optimized', 'onUpdateData_xz_pr_optimized', 'onUpdateData_xz_y_optimized',
    'onUpdateData_xz_p_optimized', 'onUpdateData_xz_r_optimized', 'onUpdateData_xyz_optimized',
    'onUpdateData_xyz_ypr_optimized', 'onUpdateData_xyz_yp_optimized', 'onUpdateData_xyz_yr_optimized',
    'onUpdateData_xyz_pr_optimized', 'onUpdateData_xyz_y_optimized', 'onUpdateData_xyz_p_optimized',
    'onUpdateData_xyz_r_optimized', 'onImportServerErrorsDescr', 'onImportClientSDK',
    'initSpaceData', 'setSpaceData', 'delSpaceData',
    'onReqAccountResetPasswordCB', 'onReqAccountBindEmailCB', 'onReqAccountNewPasswordCB',
    'onReloginBaseappSuccessfully', 'onAppActiveTickCB', 'onCreateAccountResult',
    'onLoginSuccessfully', 'onLoginFailed', 'onCreatedProxies',
    'onLoginBaseappFailed', 'onRemoteMethodCall', 'onEntityEnterWorld',
    'onEntityLeaveWorld', 'onEntityEnterSpace', 'onEntityLeaveSpace',
    'onUpdatePropertys', 'onEntityDestroyed', 'onStreamDataStarted',
    'onStreamDataRecv', 'onStreamDataCompleted', 'onKicked',
    'onImportClientMessages', 'onImportClientEntityDef', 'onHelloCB',
    'onScriptVersionNotMatch', 'onVersionNotMatch', 'onControlEntity',
    'SPEC_BY_ID'
)
