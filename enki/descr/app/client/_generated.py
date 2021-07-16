"""Messages of Client."""

from enki import kbetype, dcdescr

onReloginBaseappFailed = dcdescr.MessageDescr(
    id=8,
    name='Client::onReloginBaseappFailed',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT16,
    ),
    desc=''
)

onEntityLeaveWorldOptimized = dcdescr.MessageDescr(
    id=9,
    name='Client::onEntityLeaveWorldOptimized',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onRemoteMethodCallOptimized = dcdescr.MessageDescr(
    id=10,
    name='Client::onRemoteMethodCallOptimized',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdatePropertysOptimized = dcdescr.MessageDescr(
    id=11,
    name='Client::onUpdatePropertysOptimized',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onSetEntityPosAndDir = dcdescr.MessageDescr(
    id=12,
    name='Client::onSetEntityPosAndDir',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateBasePos = dcdescr.MessageDescr(
    id=13,
    name='Client::onUpdateBasePos',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=(
        kbetype.FLOAT,
        kbetype.FLOAT,
        kbetype.FLOAT,
    ),
    desc=''
)

onUpdateBaseDir = dcdescr.MessageDescr(
    id=14,
    name='Client::onUpdateBaseDir',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateBasePosXZ = dcdescr.MessageDescr(
    id=15,
    name='Client::onUpdateBasePosXZ',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=(
        kbetype.FLOAT,
        kbetype.FLOAT,
    ),
    desc=''
)

onUpdateData = dcdescr.MessageDescr(
    id=16,
    name='Client::onUpdateData',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_ypr = dcdescr.MessageDescr(
    id=17,
    name='Client::onUpdateData_ypr',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_yp = dcdescr.MessageDescr(
    id=18,
    name='Client::onUpdateData_yp',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_yr = dcdescr.MessageDescr(
    id=19,
    name='Client::onUpdateData_yr',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_pr = dcdescr.MessageDescr(
    id=20,
    name='Client::onUpdateData_pr',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_y = dcdescr.MessageDescr(
    id=21,
    name='Client::onUpdateData_y',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_p = dcdescr.MessageDescr(
    id=22,
    name='Client::onUpdateData_p',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_r = dcdescr.MessageDescr(
    id=23,
    name='Client::onUpdateData_r',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz = dcdescr.MessageDescr(
    id=24,
    name='Client::onUpdateData_xz',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_ypr = dcdescr.MessageDescr(
    id=25,
    name='Client::onUpdateData_xz_ypr',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_yp = dcdescr.MessageDescr(
    id=26,
    name='Client::onUpdateData_xz_yp',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_yr = dcdescr.MessageDescr(
    id=27,
    name='Client::onUpdateData_xz_yr',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_pr = dcdescr.MessageDescr(
    id=28,
    name='Client::onUpdateData_xz_pr',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_y = dcdescr.MessageDescr(
    id=29,
    name='Client::onUpdateData_xz_y',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_p = dcdescr.MessageDescr(
    id=30,
    name='Client::onUpdateData_xz_p',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_r = dcdescr.MessageDescr(
    id=31,
    name='Client::onUpdateData_xz_r',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz = dcdescr.MessageDescr(
    id=32,
    name='Client::onUpdateData_xyz',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_ypr = dcdescr.MessageDescr(
    id=33,
    name='Client::onUpdateData_xyz_ypr',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_yp = dcdescr.MessageDescr(
    id=34,
    name='Client::onUpdateData_xyz_yp',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_yr = dcdescr.MessageDescr(
    id=35,
    name='Client::onUpdateData_xyz_yr',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_pr = dcdescr.MessageDescr(
    id=36,
    name='Client::onUpdateData_xyz_pr',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_y = dcdescr.MessageDescr(
    id=37,
    name='Client::onUpdateData_xyz_y',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_p = dcdescr.MessageDescr(
    id=38,
    name='Client::onUpdateData_xyz_p',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_r = dcdescr.MessageDescr(
    id=39,
    name='Client::onUpdateData_xyz_r',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_ypr_optimized = dcdescr.MessageDescr(
    id=40,
    name='Client::onUpdateData_ypr_optimized',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_yp_optimized = dcdescr.MessageDescr(
    id=41,
    name='Client::onUpdateData_yp_optimized',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_yr_optimized = dcdescr.MessageDescr(
    id=42,
    name='Client::onUpdateData_yr_optimized',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_pr_optimized = dcdescr.MessageDescr(
    id=43,
    name='Client::onUpdateData_pr_optimized',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_y_optimized = dcdescr.MessageDescr(
    id=44,
    name='Client::onUpdateData_y_optimized',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_p_optimized = dcdescr.MessageDescr(
    id=45,
    name='Client::onUpdateData_p_optimized',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_r_optimized = dcdescr.MessageDescr(
    id=46,
    name='Client::onUpdateData_r_optimized',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_optimized = dcdescr.MessageDescr(
    id=47,
    name='Client::onUpdateData_xz_optimized',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_ypr_optimized = dcdescr.MessageDescr(
    id=48,
    name='Client::onUpdateData_xz_ypr_optimized',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_yp_optimized = dcdescr.MessageDescr(
    id=49,
    name='Client::onUpdateData_xz_yp_optimized',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_yr_optimized = dcdescr.MessageDescr(
    id=50,
    name='Client::onUpdateData_xz_yr_optimized',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_pr_optimized = dcdescr.MessageDescr(
    id=51,
    name='Client::onUpdateData_xz_pr_optimized',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_y_optimized = dcdescr.MessageDescr(
    id=52,
    name='Client::onUpdateData_xz_y_optimized',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_p_optimized = dcdescr.MessageDescr(
    id=53,
    name='Client::onUpdateData_xz_p_optimized',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_r_optimized = dcdescr.MessageDescr(
    id=54,
    name='Client::onUpdateData_xz_r_optimized',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_optimized = dcdescr.MessageDescr(
    id=55,
    name='Client::onUpdateData_xyz_optimized',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_ypr_optimized = dcdescr.MessageDescr(
    id=56,
    name='Client::onUpdateData_xyz_ypr_optimized',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_yp_optimized = dcdescr.MessageDescr(
    id=57,
    name='Client::onUpdateData_xyz_yp_optimized',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_yr_optimized = dcdescr.MessageDescr(
    id=58,
    name='Client::onUpdateData_xyz_yr_optimized',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_pr_optimized = dcdescr.MessageDescr(
    id=59,
    name='Client::onUpdateData_xyz_pr_optimized',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_y_optimized = dcdescr.MessageDescr(
    id=60,
    name='Client::onUpdateData_xyz_y_optimized',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_p_optimized = dcdescr.MessageDescr(
    id=61,
    name='Client::onUpdateData_xyz_p_optimized',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_r_optimized = dcdescr.MessageDescr(
    id=62,
    name='Client::onUpdateData_xyz_r_optimized',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onImportServerErrorsDescr = dcdescr.MessageDescr(
    id=63,
    name='Client::onImportServerErrorsDescr',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onImportClientSDK = dcdescr.MessageDescr(
    id=64,
    name='Client::onImportClientSDK',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

initSpaceData = dcdescr.MessageDescr(
    id=65,
    name='Client::initSpaceData',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

setSpaceData = dcdescr.MessageDescr(
    id=66,
    name='Client::setSpaceData',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT32,
        kbetype.STRING,
        kbetype.STRING,
    ),
    desc=''
)

delSpaceData = dcdescr.MessageDescr(
    id=67,
    name='Client::delSpaceData',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT32,
        kbetype.STRING,
    ),
    desc=''
)

onReqAccountResetPasswordCB = dcdescr.MessageDescr(
    id=68,
    name='Client::onReqAccountResetPasswordCB',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT16,
    ),
    desc=''
)

onReqAccountBindEmailCB = dcdescr.MessageDescr(
    id=69,
    name='Client::onReqAccountBindEmailCB',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT16,
    ),
    desc=''
)

onReqAccountNewPasswordCB = dcdescr.MessageDescr(
    id=70,
    name='Client::onReqAccountNewPasswordCB',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT16,
    ),
    desc=''
)

onReloginBaseappSuccessfully = dcdescr.MessageDescr(
    id=71,
    name='Client::onReloginBaseappSuccessfully',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onAppActiveTickCB = dcdescr.MessageDescr(
    id=72,
    name='Client::onAppActiveTickCB',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

onCreateAccountResult = dcdescr.MessageDescr(
    id=501,
    name='Client::onCreateAccountResult',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onLoginSuccessfully = dcdescr.MessageDescr(
    id=502,
    name='Client::onLoginSuccessfully',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onLoginFailed = dcdescr.MessageDescr(
    id=503,
    name='Client::onLoginFailed',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onCreatedProxies = dcdescr.MessageDescr(
    id=504,
    name='Client::onCreatedProxies',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT64,
        kbetype.INT32,
        kbetype.STRING,
    ),
    desc=''
)

onLoginBaseappFailed = dcdescr.MessageDescr(
    id=505,
    name='Client::onLoginBaseappFailed',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT16,
    ),
    desc=''
)

onRemoteMethodCall = dcdescr.MessageDescr(
    id=506,
    name='Client::onRemoteMethodCall',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onEntityEnterWorld = dcdescr.MessageDescr(
    id=507,
    name='Client::onEntityEnterWorld',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onEntityLeaveWorld = dcdescr.MessageDescr(
    id=508,
    name='Client::onEntityLeaveWorld',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT32,
    ),
    desc=''
)

onEntityEnterSpace = dcdescr.MessageDescr(
    id=509,
    name='Client::onEntityEnterSpace',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onEntityLeaveSpace = dcdescr.MessageDescr(
    id=510,
    name='Client::onEntityLeaveSpace',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT32,
    ),
    desc=''
)

onUpdatePropertys = dcdescr.MessageDescr(
    id=511,
    name='Client::onUpdatePropertys',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onEntityDestroyed = dcdescr.MessageDescr(
    id=512,
    name='Client::onEntityDestroyed',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT32,
    ),
    desc=''
)

onStreamDataStarted = dcdescr.MessageDescr(
    id=514,
    name='Client::onStreamDataStarted',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT16,
        kbetype.UINT32,
        kbetype.STRING,
    ),
    desc=''
)

onStreamDataRecv = dcdescr.MessageDescr(
    id=515,
    name='Client::onStreamDataRecv',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onStreamDataCompleted = dcdescr.MessageDescr(
    id=516,
    name='Client::onStreamDataCompleted',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT16,
    ),
    desc=''
)

onKicked = dcdescr.MessageDescr(
    id=517,
    name='Client::onKicked',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT16,
    ),
    desc=''
)

onImportClientMessages = dcdescr.MessageDescr(
    id=518,
    name='Client::onImportClientMessages',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onImportClientEntityDef = dcdescr.MessageDescr(
    id=519,
    name='Client::onImportClientEntityDef',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onHelloCB = dcdescr.MessageDescr(
    id=521,
    name='Client::onHelloCB',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onScriptVersionNotMatch = dcdescr.MessageDescr(
    id=522,
    name='Client::onScriptVersionNotMatch',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onVersionNotMatch = dcdescr.MessageDescr(
    id=523,
    name='Client::onVersionNotMatch',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onControlEntity = dcdescr.MessageDescr(
    id=524,
    name='Client::onControlEntity',
    args_type=dcdescr.MsgArgsType.FIXED,
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
