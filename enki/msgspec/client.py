"""Messages of ClientApp."""

from enki.kbetype import (
    FLOAT,
    INT8,
    INT16,
    INT32,
    STRING,
    UINT8_ARRAY,
    UINT16,
    UINT32,
    UINT64,
)
from enki.msg.msg_descr import FIXED, VARIABLE, MsgDescr

onReloginBaseappFailed = MsgDescr(  # noqa: N816
    id=8,
    lenght=2,
    name="Client::onReloginBaseappFailed",
    args_type=FIXED,
    args=(UINT16,),
    desc="",
)

onEntityLeaveWorldOptimized = MsgDescr(  # noqa: N816
    id=9,
    lenght=-1,
    name="Client::onEntityLeaveWorldOptimized",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onRemoteMethodCallOptimized = MsgDescr(  # noqa: N816
    id=10,
    lenght=-1,
    name="Client::onRemoteMethodCallOptimized",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdatePropertysOptimized = MsgDescr(  # noqa: N816
    id=11,
    lenght=-1,
    name="Client::onUpdatePropertysOptimized",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onSetEntityPosAndDir = MsgDescr(  # noqa: N816
    id=12,
    lenght=-1,
    name="Client::onSetEntityPosAndDir",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateBasePos = MsgDescr(  # noqa: N816
    id=13,
    lenght=12,
    name="Client::onUpdateBasePos",
    args_type=FIXED,
    args=(
        FLOAT,
        FLOAT,
        FLOAT,
    ),
    desc="",
)

onUpdateBaseDir = MsgDescr(  # noqa: N816
    id=14,
    lenght=-1,
    name="Client::onUpdateBaseDir",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateBasePosXZ = MsgDescr(  # noqa: N816
    id=15,
    lenght=8,
    name="Client::onUpdateBasePosXZ",
    args_type=FIXED,
    args=(
        FLOAT,
        FLOAT,
    ),
    desc="",
)

onUpdateData = MsgDescr(  # noqa: N816
    id=16,
    lenght=-1,
    name="Client::onUpdateData",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_ypr = MsgDescr(  # noqa: N816
    id=17,
    lenght=-1,
    name="Client::onUpdateData_ypr",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_yp = MsgDescr(  # noqa: N816
    id=18,
    lenght=-1,
    name="Client::onUpdateData_yp",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_yr = MsgDescr(  # noqa: N816
    id=19,
    lenght=-1,
    name="Client::onUpdateData_yr",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_pr = MsgDescr(  # noqa: N816
    id=20,
    lenght=-1,
    name="Client::onUpdateData_pr",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_y = MsgDescr(  # noqa: N816
    id=21,
    lenght=-1,
    name="Client::onUpdateData_y",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_p = MsgDescr(  # noqa: N816
    id=22,
    lenght=-1,
    name="Client::onUpdateData_p",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_r = MsgDescr(  # noqa: N816
    id=23,
    lenght=-1,
    name="Client::onUpdateData_r",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xz = MsgDescr(  # noqa: N816
    id=24,
    lenght=-1,
    name="Client::onUpdateData_xz",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xz_ypr = MsgDescr(  # noqa: N816
    id=25,
    lenght=-1,
    name="Client::onUpdateData_xz_ypr",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xz_yp = MsgDescr(  # noqa: N816
    id=26,
    lenght=-1,
    name="Client::onUpdateData_xz_yp",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xz_yr = MsgDescr(  # noqa: N816
    id=27,
    lenght=-1,
    name="Client::onUpdateData_xz_yr",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xz_pr = MsgDescr(  # noqa: N816
    id=28,
    lenght=-1,
    name="Client::onUpdateData_xz_pr",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xz_y = MsgDescr(  # noqa: N816
    id=29,
    lenght=-1,
    name="Client::onUpdateData_xz_y",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xz_p = MsgDescr(  # noqa: N816
    id=30,
    lenght=-1,
    name="Client::onUpdateData_xz_p",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xz_r = MsgDescr(  # noqa: N816
    id=31,
    lenght=-1,
    name="Client::onUpdateData_xz_r",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xyz = MsgDescr(  # noqa: N816
    id=32,
    lenght=-1,
    name="Client::onUpdateData_xyz",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xyz_ypr = MsgDescr(  # noqa: N816
    id=33,
    lenght=-1,
    name="Client::onUpdateData_xyz_ypr",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xyz_yp = MsgDescr(  # noqa: N816
    id=34,
    lenght=-1,
    name="Client::onUpdateData_xyz_yp",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xyz_yr = MsgDescr(  # noqa: N816
    id=35,
    lenght=-1,
    name="Client::onUpdateData_xyz_yr",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xyz_pr = MsgDescr(  # noqa: N816
    id=36,
    lenght=-1,
    name="Client::onUpdateData_xyz_pr",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xyz_y = MsgDescr(  # noqa: N816
    id=37,
    lenght=-1,
    name="Client::onUpdateData_xyz_y",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xyz_p = MsgDescr(  # noqa: N816
    id=38,
    lenght=-1,
    name="Client::onUpdateData_xyz_p",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xyz_r = MsgDescr(  # noqa: N816
    id=39,
    lenght=-1,
    name="Client::onUpdateData_xyz_r",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_ypr_optimized = MsgDescr(  # noqa: N816
    id=40,
    lenght=-1,
    name="Client::onUpdateData_ypr_optimized",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_yp_optimized = MsgDescr(  # noqa: N816
    id=41,
    lenght=-1,
    name="Client::onUpdateData_yp_optimized",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_yr_optimized = MsgDescr(  # noqa: N816
    id=42,
    lenght=-1,
    name="Client::onUpdateData_yr_optimized",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_pr_optimized = MsgDescr(  # noqa: N816
    id=43,
    lenght=-1,
    name="Client::onUpdateData_pr_optimized",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_y_optimized = MsgDescr(  # noqa: N816
    id=44,
    lenght=-1,
    name="Client::onUpdateData_y_optimized",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_p_optimized = MsgDescr(  # noqa: N816
    id=45,
    lenght=-1,
    name="Client::onUpdateData_p_optimized",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_r_optimized = MsgDescr(  # noqa: N816
    id=46,
    lenght=-1,
    name="Client::onUpdateData_r_optimized",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xz_optimized = MsgDescr(  # noqa: N816
    id=47,
    lenght=-1,
    name="Client::onUpdateData_xz_optimized",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xz_ypr_optimized = MsgDescr(  # noqa: N816
    id=48,
    lenght=-1,
    name="Client::onUpdateData_xz_ypr_optimized",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xz_yp_optimized = MsgDescr(  # noqa: N816
    id=49,
    lenght=-1,
    name="Client::onUpdateData_xz_yp_optimized",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xz_yr_optimized = MsgDescr(  # noqa: N816
    id=50,
    lenght=-1,
    name="Client::onUpdateData_xz_yr_optimized",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xz_pr_optimized = MsgDescr(  # noqa: N816
    id=51,
    lenght=-1,
    name="Client::onUpdateData_xz_pr_optimized",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xz_y_optimized = MsgDescr(  # noqa: N816
    id=52,
    lenght=-1,
    name="Client::onUpdateData_xz_y_optimized",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xz_p_optimized = MsgDescr(  # noqa: N816
    id=53,
    lenght=-1,
    name="Client::onUpdateData_xz_p_optimized",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xz_r_optimized = MsgDescr(  # noqa: N816
    id=54,
    lenght=-1,
    name="Client::onUpdateData_xz_r_optimized",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xyz_optimized = MsgDescr(  # noqa: N816
    id=55,
    lenght=-1,
    name="Client::onUpdateData_xyz_optimized",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xyz_ypr_optimized = MsgDescr(  # noqa: N816
    id=56,
    lenght=-1,
    name="Client::onUpdateData_xyz_ypr_optimized",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xyz_yp_optimized = MsgDescr(  # noqa: N816
    id=57,
    lenght=-1,
    name="Client::onUpdateData_xyz_yp_optimized",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xyz_yr_optimized = MsgDescr(  # noqa: N816
    id=58,
    lenght=-1,
    name="Client::onUpdateData_xyz_yr_optimized",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xyz_pr_optimized = MsgDescr(  # noqa: N816
    id=59,
    lenght=-1,
    name="Client::onUpdateData_xyz_pr_optimized",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xyz_y_optimized = MsgDescr(  # noqa: N816
    id=60,
    lenght=-1,
    name="Client::onUpdateData_xyz_y_optimized",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xyz_p_optimized = MsgDescr(  # noqa: N816
    id=61,
    lenght=-1,
    name="Client::onUpdateData_xyz_p_optimized",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onUpdateData_xyz_r_optimized = MsgDescr(  # noqa: N816
    id=62,
    lenght=-1,
    name="Client::onUpdateData_xyz_r_optimized",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onImportClientSDK = MsgDescr(  # noqa: N816
    id=64,
    lenght=-1,
    name="Client::onImportClientSDK",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

initSpaceData = MsgDescr(  # noqa: N816
    id=65,
    lenght=-1,
    name="Client::initSpaceData",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

setSpaceData = MsgDescr(  # noqa: N816
    id=66,
    lenght=-1,
    name="Client::setSpaceData",
    args_type=FIXED,
    args=(
        UINT32,
        STRING,
        STRING,
    ),
    desc="",
)

delSpaceData = MsgDescr(  # noqa: N816
    id=67,
    lenght=-1,
    name="Client::delSpaceData",
    args_type=FIXED,
    args=(
        UINT32,
        STRING,
    ),
    desc="",
)

onReqAccountResetPasswordCB = MsgDescr(  # noqa: N816
    id=68,
    lenght=2,
    name="Client::onReqAccountResetPasswordCB",
    args_type=FIXED,
    args=(UINT16,),
    desc="",
)

onReqAccountBindEmailCB = MsgDescr(  # noqa: N816
    id=69,
    lenght=2,
    name="Client::onReqAccountBindEmailCB",
    args_type=FIXED,
    args=(UINT16,),
    desc="",
)

onReqAccountNewPasswordCB = MsgDescr(  # noqa: N816
    id=70,
    lenght=2,
    name="Client::onReqAccountNewPasswordCB",
    args_type=FIXED,
    args=(UINT16,),
    desc="",
)

onReloginBaseappSuccessfully = MsgDescr(  # noqa: N816
    id=71,
    lenght=-1,
    name="Client::onReloginBaseappSuccessfully",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onAppActiveTickCB = MsgDescr(  # noqa: N816
    id=72,
    lenght=0,
    name="Client::onAppActiveTickCB",
    args_type=FIXED,
    args=(),
    desc="",
)

onCreateAccountResult = MsgDescr(  # noqa: N816
    id=501,
    lenght=-1,
    name="Client::onCreateAccountResult",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onCreatedProxies = MsgDescr(  # noqa: N816
    id=504,
    lenght=-1,
    name="Client::onCreatedProxies",
    args_type=FIXED,
    args=(
        UINT64,
        INT32,
        STRING,
    ),
    desc="",
)

onLoginBaseappFailed = MsgDescr(  # noqa: N816
    id=505,
    lenght=2,
    name="Client::onLoginBaseappFailed",
    args_type=FIXED,
    args=(UINT16,),
    desc="",
)

onRemoteMethodCall = MsgDescr(  # noqa: N816
    id=506,
    lenght=-1,
    name="Client::onRemoteMethodCall",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onEntityEnterWorld = MsgDescr(  # noqa: N816
    id=507,
    lenght=-1,
    name="Client::onEntityEnterWorld",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onEntityLeaveWorld = MsgDescr(  # noqa: N816
    id=508,
    lenght=4,
    name="Client::onEntityLeaveWorld",
    args_type=FIXED,
    args=(INT32,),
    desc="",
)

onEntityEnterSpace = MsgDescr(  # noqa: N816
    id=509,
    lenght=-1,
    name="Client::onEntityEnterSpace",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onEntityLeaveSpace = MsgDescr(  # noqa: N816
    id=510,
    lenght=4,
    name="Client::onEntityLeaveSpace",
    args_type=FIXED,
    args=(INT32,),
    desc="",
)

onUpdatePropertys = MsgDescr(  # noqa: N816
    id=511,
    lenght=-1,
    name="Client::onUpdatePropertys",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onEntityDestroyed = MsgDescr(  # noqa: N816
    id=512,
    lenght=4,
    name="Client::onEntityDestroyed",
    args_type=FIXED,
    args=(INT32,),
    desc="",
)

onStreamDataRecv = MsgDescr(  # noqa: N816
    id=515,
    lenght=-1,
    name="Client::onStreamDataRecv",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onStreamDataCompleted = MsgDescr(  # noqa: N816
    id=516,
    lenght=2,
    name="Client::onStreamDataCompleted",
    args_type=FIXED,
    args=(INT16,),
    desc="",
)

onKicked = MsgDescr(  # noqa: N816
    id=517,
    lenght=2,
    name="Client::onKicked",
    args_type=FIXED,
    args=(UINT16,),
    desc="",
)

onControlEntity = MsgDescr(  # noqa: N816
    id=524,
    lenght=5,
    name="Client::onControlEntity",
    args_type=FIXED,
    args=(
        INT32,
        INT8,
    ),
    desc="",
)

onHelloCB = MsgDescr(  # noqa: N816
    id=521,
    lenght=-1,
    name="Client::onHelloCB",
    args_type=VARIABLE,
    args=(
        STRING,
        STRING,
        STRING,
        STRING,
        INT32,
    ),
    desc="Ответ на hello",
)

onLoginSuccessfully = MsgDescr(  # noqa: N816
    id=502,
    lenght=-1,
    name="Client::onLoginSuccessfully",
    args_type=VARIABLE,
    args=(
        # Есть небольшое отличие у сообщений в KBEngine 1.x и 2.x, поэтому в
        # парсере парсится
        UINT8_ARRAY,
    ),
    desc="The client logs in to loginapp, and the server returns success.",
)

onImportClientMessages = MsgDescr(  # noqa: N816
    id=518,
    lenght=-1,
    name="Client::onImportClientMessages",
    args_type=VARIABLE,
    args=(
        UINT8_ARRAY,  # binary data for parsing
    ),
    desc="The protocol packet returned by the server.",
)

onImportClientEntityDef = MsgDescr(  # noqa: N816
    id=519,
    lenght=-1,
    name="Client::onImportClientEntityDef",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="The entitydef data returned by the server.",
)

onImportServerErrorsDescr = MsgDescr(  # noqa: N816
    id=63,
    lenght=-1,
    name="Client::onImportServerErrorsDescr",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onLoginFailed = MsgDescr(  # noqa: N816
    id=503,
    lenght=-1,
    name="Client::onLoginFailed",
    args_type=VARIABLE,
    args=(UINT16, UINT8_ARRAY),
    desc="",
)

onVersionNotMatch = MsgDescr(  # noqa: N816
    id=523,
    lenght=-1,
    name="Client::onVersionNotMatch",
    args_type=VARIABLE,
    args=(STRING,),
    desc="",
)

onScriptVersionNotMatch = MsgDescr(  # noqa: N816
    id=522,
    lenght=-1,
    name="Client::onScriptVersionNotMatch",
    args_type=VARIABLE,
    args=(STRING,),
    desc="",
)

# The generaged message has invalid parameters types.
onStreamDataStarted = MsgDescr(  # noqa: N816
    id=514,
    lenght=-1,
    name="Client::onStreamDataStarted",
    args_type=FIXED,
    args=(
        INT16,
        UINT32,
        STRING,
        INT8,
    ),
    desc="Начать приём стрима данных от Baseapp (файл или поток из tcp)",
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
    onControlEntity.id: onControlEntity,
}

__all__ = (
    "SPEC_BY_ID",
    "delSpaceData",
    "initSpaceData",
    "onAppActiveTickCB",
    "onControlEntity",
    "onCreateAccountResult",
    "onCreatedProxies",
    "onEntityDestroyed",
    "onEntityEnterSpace",
    "onEntityEnterWorld",
    "onEntityLeaveSpace",
    "onEntityLeaveWorld",
    "onEntityLeaveWorldOptimized",
    "onHelloCB",
    "onImportClientEntityDef",
    "onImportClientMessages",
    "onImportClientSDK",
    "onImportServerErrorsDescr",
    "onKicked",
    "onLoginBaseappFailed",
    "onLoginFailed",
    "onLoginSuccessfully",
    "onReloginBaseappFailed",
    "onReloginBaseappSuccessfully",
    "onRemoteMethodCall",
    "onRemoteMethodCallOptimized",
    "onReqAccountBindEmailCB",
    "onReqAccountNewPasswordCB",
    "onReqAccountResetPasswordCB",
    "onScriptVersionNotMatch",
    "onSetEntityPosAndDir",
    "onStreamDataCompleted",
    "onStreamDataRecv",
    "onStreamDataStarted",
    "onUpdateBaseDir",
    "onUpdateBasePos",
    "onUpdateBasePosXZ",
    "onUpdateData",
    "onUpdateData_p",
    "onUpdateData_p_optimized",
    "onUpdateData_pr",
    "onUpdateData_pr_optimized",
    "onUpdateData_r",
    "onUpdateData_r_optimized",
    "onUpdateData_xyz",
    "onUpdateData_xyz_optimized",
    "onUpdateData_xyz_p",
    "onUpdateData_xyz_p_optimized",
    "onUpdateData_xyz_pr",
    "onUpdateData_xyz_pr_optimized",
    "onUpdateData_xyz_r",
    "onUpdateData_xyz_r_optimized",
    "onUpdateData_xyz_y",
    "onUpdateData_xyz_y_optimized",
    "onUpdateData_xyz_yp",
    "onUpdateData_xyz_yp_optimized",
    "onUpdateData_xyz_ypr",
    "onUpdateData_xyz_ypr_optimized",
    "onUpdateData_xyz_yr",
    "onUpdateData_xyz_yr_optimized",
    "onUpdateData_xz",
    "onUpdateData_xz_optimized",
    "onUpdateData_xz_p",
    "onUpdateData_xz_p_optimized",
    "onUpdateData_xz_pr",
    "onUpdateData_xz_pr_optimized",
    "onUpdateData_xz_r",
    "onUpdateData_xz_r_optimized",
    "onUpdateData_xz_y",
    "onUpdateData_xz_y_optimized",
    "onUpdateData_xz_yp",
    "onUpdateData_xz_yp_optimized",
    "onUpdateData_xz_ypr",
    "onUpdateData_xz_ypr_optimized",
    "onUpdateData_xz_yr",
    "onUpdateData_xz_yr_optimized",
    "onUpdateData_y",
    "onUpdateData_y_optimized",
    "onUpdateData_yp",
    "onUpdateData_yp_optimized",
    "onUpdateData_ypr",
    "onUpdateData_ypr_optimized",
    "onUpdateData_yr",
    "onUpdateData_yr_optimized",
    "onUpdatePropertys",
    "onUpdatePropertysOptimized",
    "onVersionNotMatch",
    "setSpaceData",
)
