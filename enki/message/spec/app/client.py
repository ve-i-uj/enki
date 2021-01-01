"""Messages of Client."""

from enki import message
from enki import kbetype

onReloginBaseappFailed = message.MessageSpec(
    id=8,
    name='Client::onReloginBaseappFailed',
    args_type=message.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT16,
    ),
    desc=''
)

onEntityLeaveWorldOptimized = message.MessageSpec(
    id=9,
    name='Client::onEntityLeaveWorldOptimized',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onRemoteMethodCallOptimized = message.MessageSpec(
    id=10,
    name='Client::onRemoteMethodCallOptimized',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdatePropertysOptimized = message.MessageSpec(
    id=11,
    name='Client::onUpdatePropertysOptimized',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onSetEntityPosAndDir = message.MessageSpec(
    id=12,
    name='Client::onSetEntityPosAndDir',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateBasePos = message.MessageSpec(
    id=13,
    name='Client::onUpdateBasePos',
    args_type=message.MsgArgsType.FIXED,
    field_types=(
        kbetype.FLOAT,
        kbetype.FLOAT,
        kbetype.FLOAT,
    ),
    desc=''
)

onUpdateBaseDir = message.MessageSpec(
    id=14,
    name='Client::onUpdateBaseDir',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateBasePosXZ = message.MessageSpec(
    id=15,
    name='Client::onUpdateBasePosXZ',
    args_type=message.MsgArgsType.FIXED,
    field_types=(
        kbetype.FLOAT,
        kbetype.FLOAT,
    ),
    desc=''
)

onUpdateData = message.MessageSpec(
    id=16,
    name='Client::onUpdateData',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_ypr = message.MessageSpec(
    id=17,
    name='Client::onUpdateData_ypr',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_yp = message.MessageSpec(
    id=18,
    name='Client::onUpdateData_yp',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_yr = message.MessageSpec(
    id=19,
    name='Client::onUpdateData_yr',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_pr = message.MessageSpec(
    id=20,
    name='Client::onUpdateData_pr',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_y = message.MessageSpec(
    id=21,
    name='Client::onUpdateData_y',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_p = message.MessageSpec(
    id=22,
    name='Client::onUpdateData_p',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_r = message.MessageSpec(
    id=23,
    name='Client::onUpdateData_r',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz = message.MessageSpec(
    id=24,
    name='Client::onUpdateData_xz',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_ypr = message.MessageSpec(
    id=25,
    name='Client::onUpdateData_xz_ypr',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_yp = message.MessageSpec(
    id=26,
    name='Client::onUpdateData_xz_yp',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_yr = message.MessageSpec(
    id=27,
    name='Client::onUpdateData_xz_yr',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_pr = message.MessageSpec(
    id=28,
    name='Client::onUpdateData_xz_pr',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_y = message.MessageSpec(
    id=29,
    name='Client::onUpdateData_xz_y',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_p = message.MessageSpec(
    id=30,
    name='Client::onUpdateData_xz_p',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_r = message.MessageSpec(
    id=31,
    name='Client::onUpdateData_xz_r',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz = message.MessageSpec(
    id=32,
    name='Client::onUpdateData_xyz',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_ypr = message.MessageSpec(
    id=33,
    name='Client::onUpdateData_xyz_ypr',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_yp = message.MessageSpec(
    id=34,
    name='Client::onUpdateData_xyz_yp',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_yr = message.MessageSpec(
    id=35,
    name='Client::onUpdateData_xyz_yr',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_pr = message.MessageSpec(
    id=36,
    name='Client::onUpdateData_xyz_pr',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_y = message.MessageSpec(
    id=37,
    name='Client::onUpdateData_xyz_y',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_p = message.MessageSpec(
    id=38,
    name='Client::onUpdateData_xyz_p',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_r = message.MessageSpec(
    id=39,
    name='Client::onUpdateData_xyz_r',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_ypr_optimized = message.MessageSpec(
    id=40,
    name='Client::onUpdateData_ypr_optimized',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_yp_optimized = message.MessageSpec(
    id=41,
    name='Client::onUpdateData_yp_optimized',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_yr_optimized = message.MessageSpec(
    id=42,
    name='Client::onUpdateData_yr_optimized',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_pr_optimized = message.MessageSpec(
    id=43,
    name='Client::onUpdateData_pr_optimized',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_y_optimized = message.MessageSpec(
    id=44,
    name='Client::onUpdateData_y_optimized',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_p_optimized = message.MessageSpec(
    id=45,
    name='Client::onUpdateData_p_optimized',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_r_optimized = message.MessageSpec(
    id=46,
    name='Client::onUpdateData_r_optimized',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_optimized = message.MessageSpec(
    id=47,
    name='Client::onUpdateData_xz_optimized',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_ypr_optimized = message.MessageSpec(
    id=48,
    name='Client::onUpdateData_xz_ypr_optimized',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_yp_optimized = message.MessageSpec(
    id=49,
    name='Client::onUpdateData_xz_yp_optimized',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_yr_optimized = message.MessageSpec(
    id=50,
    name='Client::onUpdateData_xz_yr_optimized',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_pr_optimized = message.MessageSpec(
    id=51,
    name='Client::onUpdateData_xz_pr_optimized',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_y_optimized = message.MessageSpec(
    id=52,
    name='Client::onUpdateData_xz_y_optimized',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_p_optimized = message.MessageSpec(
    id=53,
    name='Client::onUpdateData_xz_p_optimized',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xz_r_optimized = message.MessageSpec(
    id=54,
    name='Client::onUpdateData_xz_r_optimized',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_optimized = message.MessageSpec(
    id=55,
    name='Client::onUpdateData_xyz_optimized',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_ypr_optimized = message.MessageSpec(
    id=56,
    name='Client::onUpdateData_xyz_ypr_optimized',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_yp_optimized = message.MessageSpec(
    id=57,
    name='Client::onUpdateData_xyz_yp_optimized',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_yr_optimized = message.MessageSpec(
    id=58,
    name='Client::onUpdateData_xyz_yr_optimized',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_pr_optimized = message.MessageSpec(
    id=59,
    name='Client::onUpdateData_xyz_pr_optimized',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_y_optimized = message.MessageSpec(
    id=60,
    name='Client::onUpdateData_xyz_y_optimized',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_p_optimized = message.MessageSpec(
    id=61,
    name='Client::onUpdateData_xyz_p_optimized',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateData_xyz_r_optimized = message.MessageSpec(
    id=62,
    name='Client::onUpdateData_xyz_r_optimized',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onImportServerErrorsDescr = message.MessageSpec(
    id=63,
    name='Client::onImportServerErrorsDescr',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onImportClientSDK = message.MessageSpec(
    id=64,
    name='Client::onImportClientSDK',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

initSpaceData = message.MessageSpec(
    id=65,
    name='Client::initSpaceData',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

setSpaceData = message.MessageSpec(
    id=66,
    name='Client::setSpaceData',
    args_type=message.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT32,
        kbetype.STRING,
        kbetype.STRING,
    ),
    desc=''
)

delSpaceData = message.MessageSpec(
    id=67,
    name='Client::delSpaceData',
    args_type=message.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT32,
        kbetype.STRING,
    ),
    desc=''
)

onReqAccountResetPasswordCB = message.MessageSpec(
    id=68,
    name='Client::onReqAccountResetPasswordCB',
    args_type=message.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT16,
    ),
    desc=''
)

onReqAccountBindEmailCB = message.MessageSpec(
    id=69,
    name='Client::onReqAccountBindEmailCB',
    args_type=message.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT16,
    ),
    desc=''
)

onReqAccountNewPasswordCB = message.MessageSpec(
    id=70,
    name='Client::onReqAccountNewPasswordCB',
    args_type=message.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT16,
    ),
    desc=''
)

onReloginBaseappSuccessfully = message.MessageSpec(
    id=71,
    name='Client::onReloginBaseappSuccessfully',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onAppActiveTickCB = message.MessageSpec(
    id=72,
    name='Client::onAppActiveTickCB',
    args_type=message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

onCreateAccountResult = message.MessageSpec(
    id=501,
    name='Client::onCreateAccountResult',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onLoginSuccessfully = message.MessageSpec(
    id=502,
    name='Client::onLoginSuccessfully',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onLoginFailed = message.MessageSpec(
    id=503,
    name='Client::onLoginFailed',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onCreatedProxies = message.MessageSpec(
    id=504,
    name='Client::onCreatedProxies',
    args_type=message.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT64,
        kbetype.INT32,
        kbetype.STRING,
    ),
    desc=''
)

onLoginBaseappFailed = message.MessageSpec(
    id=505,
    name='Client::onLoginBaseappFailed',
    args_type=message.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT16,
    ),
    desc=''
)

onRemoteMethodCall = message.MessageSpec(
    id=506,
    name='Client::onRemoteMethodCall',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onEntityEnterWorld = message.MessageSpec(
    id=507,
    name='Client::onEntityEnterWorld',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onEntityLeaveWorld = message.MessageSpec(
    id=508,
    name='Client::onEntityLeaveWorld',
    args_type=message.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT32,
    ),
    desc=''
)

onEntityEnterSpace = message.MessageSpec(
    id=509,
    name='Client::onEntityEnterSpace',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onEntityLeaveSpace = message.MessageSpec(
    id=510,
    name='Client::onEntityLeaveSpace',
    args_type=message.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT32,
    ),
    desc=''
)

onUpdatePropertys = message.MessageSpec(
    id=511,
    name='Client::onUpdatePropertys',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onEntityDestroyed = message.MessageSpec(
    id=512,
    name='Client::onEntityDestroyed',
    args_type=message.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT32,
    ),
    desc=''
)

onStreamDataStarted = message.MessageSpec(
    id=514,
    name='Client::onStreamDataStarted',
    args_type=message.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT16,
        kbetype.UINT32,
        kbetype.STRING,
    ),
    desc=''
)

onStreamDataRecv = message.MessageSpec(
    id=515,
    name='Client::onStreamDataRecv',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onStreamDataCompleted = message.MessageSpec(
    id=516,
    name='Client::onStreamDataCompleted',
    args_type=message.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT16,
    ),
    desc=''
)

onKicked = message.MessageSpec(
    id=517,
    name='Client::onKicked',
    args_type=message.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT16,
    ),
    desc=''
)

onImportClientMessages = message.MessageSpec(
    id=518,
    name='Client::onImportClientMessages',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onImportClientEntityDef = message.MessageSpec(
    id=519,
    name='Client::onImportClientEntityDef',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onHelloCB = message.MessageSpec(
    id=521,
    name='Client::onHelloCB',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onScriptVersionNotMatch = message.MessageSpec(
    id=522,
    name='Client::onScriptVersionNotMatch',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onVersionNotMatch = message.MessageSpec(
    id=523,
    name='Client::onVersionNotMatch',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onControlEntity = message.MessageSpec(
    id=524,
    name='Client::onControlEntity',
    args_type=message.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT32,
        kbetype.INT8,
    ),
    desc=''
)
