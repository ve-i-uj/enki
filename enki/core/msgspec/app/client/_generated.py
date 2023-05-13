"""Messages of TCPClient."""

from enki.core import kbeenum
from enki.core import kbetype
from enki.core.message import MsgDescr


onReloginBaseappFailed = MsgDescr(
    id=8,
    lenght=2,
    name='Client::onReloginBaseappFailed',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT16,
    ),
    desc=''
)

onEntityLeaveWorldOptimized = MsgDescr(
    id=9,
    lenght=-1,
    name='Client::onEntityLeaveWorldOptimized',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onRemoteMethodCallOptimized = MsgDescr(
    id=10,
    lenght=-1,
    name='Client::onRemoteMethodCallOptimized',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdatePropertysOptimized = MsgDescr(
    id=11,
    lenght=-1,
    name='Client::onUpdatePropertysOptimized',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onSetEntityPosAndDir = MsgDescr(
    id=12,
    lenght=-1,
    name='Client::onSetEntityPosAndDir',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateBasePos = MsgDescr(
    id=13,
    lenght=12,
    name='Client::onUpdateBasePos',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.FLOAT,
        kbetype.FLOAT,
        kbetype.FLOAT,
    ),
    desc=''
)

onUpdateBaseDir = MsgDescr(
    id=14,
    lenght=-1,
    name='Client::onUpdateBaseDir',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateBasePosXZ = MsgDescr(
    id=15,
    lenght=8,
    name='Client::onUpdateBasePosXZ',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.FLOAT,
        kbetype.FLOAT,
    ),
    desc=''
)

onUpdateData = MsgDescr(
    id=16,
    lenght=-1,
    name='Client::onUpdateData',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_ypr = MsgDescr(
    id=17,
    lenght=-1,
    name='Client::onUpdateData_ypr',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_yp = MsgDescr(
    id=18,
    lenght=-1,
    name='Client::onUpdateData_yp',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_yr = MsgDescr(
    id=19,
    lenght=-1,
    name='Client::onUpdateData_yr',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_pr = MsgDescr(
    id=20,
    lenght=-1,
    name='Client::onUpdateData_pr',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_y = MsgDescr(
    id=21,
    lenght=-1,
    name='Client::onUpdateData_y',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_p = MsgDescr(
    id=22,
    lenght=-1,
    name='Client::onUpdateData_p',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_r = MsgDescr(
    id=23,
    lenght=-1,
    name='Client::onUpdateData_r',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xz = MsgDescr(
    id=24,
    lenght=-1,
    name='Client::onUpdateData_xz',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xz_ypr = MsgDescr(
    id=25,
    lenght=-1,
    name='Client::onUpdateData_xz_ypr',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xz_yp = MsgDescr(
    id=26,
    lenght=-1,
    name='Client::onUpdateData_xz_yp',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xz_yr = MsgDescr(
    id=27,
    lenght=-1,
    name='Client::onUpdateData_xz_yr',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xz_pr = MsgDescr(
    id=28,
    lenght=-1,
    name='Client::onUpdateData_xz_pr',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xz_y = MsgDescr(
    id=29,
    lenght=-1,
    name='Client::onUpdateData_xz_y',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xz_p = MsgDescr(
    id=30,
    lenght=-1,
    name='Client::onUpdateData_xz_p',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xz_r = MsgDescr(
    id=31,
    lenght=-1,
    name='Client::onUpdateData_xz_r',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xyz = MsgDescr(
    id=32,
    lenght=-1,
    name='Client::onUpdateData_xyz',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xyz_ypr = MsgDescr(
    id=33,
    lenght=-1,
    name='Client::onUpdateData_xyz_ypr',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xyz_yp = MsgDescr(
    id=34,
    lenght=-1,
    name='Client::onUpdateData_xyz_yp',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xyz_yr = MsgDescr(
    id=35,
    lenght=-1,
    name='Client::onUpdateData_xyz_yr',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xyz_pr = MsgDescr(
    id=36,
    lenght=-1,
    name='Client::onUpdateData_xyz_pr',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xyz_y = MsgDescr(
    id=37,
    lenght=-1,
    name='Client::onUpdateData_xyz_y',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xyz_p = MsgDescr(
    id=38,
    lenght=-1,
    name='Client::onUpdateData_xyz_p',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xyz_r = MsgDescr(
    id=39,
    lenght=-1,
    name='Client::onUpdateData_xyz_r',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_ypr_optimized = MsgDescr(
    id=40,
    lenght=-1,
    name='Client::onUpdateData_ypr_optimized',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_yp_optimized = MsgDescr(
    id=41,
    lenght=-1,
    name='Client::onUpdateData_yp_optimized',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_yr_optimized = MsgDescr(
    id=42,
    lenght=-1,
    name='Client::onUpdateData_yr_optimized',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_pr_optimized = MsgDescr(
    id=43,
    lenght=-1,
    name='Client::onUpdateData_pr_optimized',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_y_optimized = MsgDescr(
    id=44,
    lenght=-1,
    name='Client::onUpdateData_y_optimized',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_p_optimized = MsgDescr(
    id=45,
    lenght=-1,
    name='Client::onUpdateData_p_optimized',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_r_optimized = MsgDescr(
    id=46,
    lenght=-1,
    name='Client::onUpdateData_r_optimized',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xz_optimized = MsgDescr(
    id=47,
    lenght=-1,
    name='Client::onUpdateData_xz_optimized',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xz_ypr_optimized = MsgDescr(
    id=48,
    lenght=-1,
    name='Client::onUpdateData_xz_ypr_optimized',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xz_yp_optimized = MsgDescr(
    id=49,
    lenght=-1,
    name='Client::onUpdateData_xz_yp_optimized',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xz_yr_optimized = MsgDescr(
    id=50,
    lenght=-1,
    name='Client::onUpdateData_xz_yr_optimized',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xz_pr_optimized = MsgDescr(
    id=51,
    lenght=-1,
    name='Client::onUpdateData_xz_pr_optimized',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xz_y_optimized = MsgDescr(
    id=52,
    lenght=-1,
    name='Client::onUpdateData_xz_y_optimized',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xz_p_optimized = MsgDescr(
    id=53,
    lenght=-1,
    name='Client::onUpdateData_xz_p_optimized',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xz_r_optimized = MsgDescr(
    id=54,
    lenght=-1,
    name='Client::onUpdateData_xz_r_optimized',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xyz_optimized = MsgDescr(
    id=55,
    lenght=-1,
    name='Client::onUpdateData_xyz_optimized',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xyz_ypr_optimized = MsgDescr(
    id=56,
    lenght=-1,
    name='Client::onUpdateData_xyz_ypr_optimized',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xyz_yp_optimized = MsgDescr(
    id=57,
    lenght=-1,
    name='Client::onUpdateData_xyz_yp_optimized',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xyz_yr_optimized = MsgDescr(
    id=58,
    lenght=-1,
    name='Client::onUpdateData_xyz_yr_optimized',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xyz_pr_optimized = MsgDescr(
    id=59,
    lenght=-1,
    name='Client::onUpdateData_xyz_pr_optimized',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xyz_y_optimized = MsgDescr(
    id=60,
    lenght=-1,
    name='Client::onUpdateData_xyz_y_optimized',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xyz_p_optimized = MsgDescr(
    id=61,
    lenght=-1,
    name='Client::onUpdateData_xyz_p_optimized',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateData_xyz_r_optimized = MsgDescr(
    id=62,
    lenght=-1,
    name='Client::onUpdateData_xyz_r_optimized',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onImportServerErrorsDescr = MsgDescr(
    id=63,
    lenght=-1,
    name='Client::onImportServerErrorsDescr',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onImportClientSDK = MsgDescr(
    id=64,
    lenght=-1,
    name='Client::onImportClientSDK',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

initSpaceData = MsgDescr(
    id=65,
    lenght=-1,
    name='Client::initSpaceData',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

setSpaceData = MsgDescr(
    id=66,
    lenght=-1,
    name='Client::setSpaceData',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT32,
        kbetype.STRING,
        kbetype.STRING,
    ),
    desc=''
)

delSpaceData = MsgDescr(
    id=67,
    lenght=-1,
    name='Client::delSpaceData',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT32,
        kbetype.STRING,
    ),
    desc=''
)

onReqAccountResetPasswordCB = MsgDescr(
    id=68,
    lenght=2,
    name='Client::onReqAccountResetPasswordCB',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT16,
    ),
    desc=''
)

onReqAccountBindEmailCB = MsgDescr(
    id=69,
    lenght=2,
    name='Client::onReqAccountBindEmailCB',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT16,
    ),
    desc=''
)

onReqAccountNewPasswordCB = MsgDescr(
    id=70,
    lenght=2,
    name='Client::onReqAccountNewPasswordCB',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT16,
    ),
    desc=''
)

onReloginBaseappSuccessfully = MsgDescr(
    id=71,
    lenght=-1,
    name='Client::onReloginBaseappSuccessfully',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onAppActiveTickCB = MsgDescr(
    id=72,
    lenght=0,
    name='Client::onAppActiveTickCB',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

onCreateAccountResult = MsgDescr(
    id=501,
    lenght=-1,
    name='Client::onCreateAccountResult',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onLoginSuccessfully = MsgDescr(
    id=502,
    lenght=-1,
    name='Client::onLoginSuccessfully',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onLoginFailed = MsgDescr(
    id=503,
    lenght=-1,
    name='Client::onLoginFailed',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onCreatedProxies = MsgDescr(
    id=504,
    lenght=-1,
    name='Client::onCreatedProxies',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT64,
        kbetype.INT32,
        kbetype.STRING,
    ),
    desc=''
)

onLoginBaseappFailed = MsgDescr(
    id=505,
    lenght=2,
    name='Client::onLoginBaseappFailed',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT16,
    ),
    desc=''
)

onRemoteMethodCall = MsgDescr(
    id=506,
    lenght=-1,
    name='Client::onRemoteMethodCall',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onEntityEnterWorld = MsgDescr(
    id=507,
    lenght=-1,
    name='Client::onEntityEnterWorld',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onEntityLeaveWorld = MsgDescr(
    id=508,
    lenght=4,
    name='Client::onEntityLeaveWorld',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT32,
    ),
    desc=''
)

onEntityEnterSpace = MsgDescr(
    id=509,
    lenght=-1,
    name='Client::onEntityEnterSpace',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onEntityLeaveSpace = MsgDescr(
    id=510,
    lenght=4,
    name='Client::onEntityLeaveSpace',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT32,
    ),
    desc=''
)

onUpdatePropertys = MsgDescr(
    id=511,
    lenght=-1,
    name='Client::onUpdatePropertys',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onEntityDestroyed = MsgDescr(
    id=512,
    lenght=4,
    name='Client::onEntityDestroyed',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT32,
    ),
    desc=''
)

onStreamDataStarted = MsgDescr(
    id=514,
    lenght=-1,
    name='Client::onStreamDataStarted',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT16,
        kbetype.UINT32,
        kbetype.STRING,
    ),
    desc=''
)

onStreamDataRecv = MsgDescr(
    id=515,
    lenght=-1,
    name='Client::onStreamDataRecv',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onStreamDataCompleted = MsgDescr(
    id=516,
    lenght=2,
    name='Client::onStreamDataCompleted',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT16,
    ),
    desc=''
)

onKicked = MsgDescr(
    id=517,
    lenght=2,
    name='Client::onKicked',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT16,
    ),
    desc=''
)

onImportClientMessages = MsgDescr(
    id=518,
    lenght=-1,
    name='Client::onImportClientMessages',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onImportClientEntityDef = MsgDescr(
    id=519,
    lenght=-1,
    name='Client::onImportClientEntityDef',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onHelloCB = MsgDescr(
    id=521,
    lenght=-1,
    name='Client::onHelloCB',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onScriptVersionNotMatch = MsgDescr(
    id=522,
    lenght=-1,
    name='Client::onScriptVersionNotMatch',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onVersionNotMatch = MsgDescr(
    id=523,
    lenght=-1,
    name='Client::onVersionNotMatch',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onControlEntity = MsgDescr(
    id=524,
    lenght=5,
    name='Client::onControlEntity',
    args_type=kbeenum.MsgArgsType.FIXED,
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
