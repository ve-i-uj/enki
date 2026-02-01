"""Messages of LoginApp."""

from enki.kbeenum import ComponentType
from enki.kbetype.decoders.basic_data_type_decoders import (
    BLOB,
    BOOL,
    FLOAT,
    INT8,
    INT32,
    STRING,
    UINT8_ARRAY,
    UINT16,
    UINT32,
    UINT64,
)
from enki.kbetype.decoders.custom_decoders import (
    COMPONENT_ID,
    COMPONENT_TYPE,
    DBID,
    ENTITY_ID,
    SERVER_ERROR_CODE,
)
from enki.msg.msg_descr import FIXED, VARIABLE, MsgDescr, MsgSpecById

from . import custom

# The "importClientMessages" response contains wrong message description of
# the "hello". I override the description here.
hello = MsgDescr(
    id=4,
    lenght=-1,
    name="Loginapp::hello",
    args_type=VARIABLE,
    args=(
        STRING,  # for what version of kbe client the plugin is
        STRING,  # for what version of server scripts the plugin is
        BLOB,  # encrypted key
    ),
    desc="hello",
)

# [2026-02-01 08:45 burov_alexey@mail.ru]:
# Скорей всего, если в конце строка или тип с нулевым символом в конце, то не
# записывается длина сообщения при сериализации. Поэтому я пока поставил
# lenght=-2, чтобы пока парсилось это сообщение. В KBEngine путано механизм
# парсинга и определения длины сделан.

# These is the real description of the "login" message.
# The "importClientMessages" response has wrong one.
login = MsgDescr(
    id=3,
    lenght=-1,
    name="Loginapp::login",
    args_type=VARIABLE,
    args=(
        INT8,  # client type (see ClientType)
        BLOB,  # binary data for "onRequestLogin" callback of script layer
        STRING,  # account name
        STRING,  # password
        STRING,  # digest
        STRING,  # force login for "bots" client type (not empty value is true)
    ),
    desc=(
        "The client requests to log in to the loginapp process of the server. "
        "After receiving the request, the process will return a gateway "
        "address after verification."
    ),
)

reqClose = MsgDescr(  # noqa: N816
    id=1,
    lenght=0,
    name="Loginapp::reqClose",
    args_type=FIXED,
    args=(),
    desc="",
)

onClientActiveTick = MsgDescr(  # noqa: N816
    id=11,
    lenght=0,
    name="Loginapp::onClientActiveTick",
    args_type=FIXED,
    args=(),
    desc="",
)

importClientMessages = MsgDescr(  # noqa: N816
    id=5,
    lenght=0,
    name="Loginapp::importClientMessages",
    args_type=FIXED,
    args=(),
    desc="The client requests to import the message protocol.",
)

importServerErrorsDescr = MsgDescr(  # noqa: N816
    id=8,
    lenght=0,
    name="Loginapp::importServerErrorsDescr",
    args_type=FIXED,
    args=(),
    desc="",
)

reqCreateAccount = MsgDescr(  # noqa: N816
    id=2,
    lenght=-1,
    name="Loginapp::reqCreateAccount",
    args_type=VARIABLE,
    args=(STRING, STRING, UINT8_ARRAY),
    desc="",
)

reqCreateMailAccount = MsgDescr(  # noqa: N816
    id=6,
    lenght=-1,
    name="Loginapp::reqCreateMailAccount",
    args_type=FIXED,
    args=(STRING, STRING, BLOB),
    desc="",
)

importClientSDK = MsgDescr(  # noqa: N816
    id=7,
    lenght=-1,
    name="Loginapp::importClientSDK",
    args_type=FIXED,
    args=(
        STRING,  # options
        INT32,  # clientWindowSize
        STRING,  # callbackIP
        UINT16,  # callbackPort
    ),
    desc="",
)

lookApp = MsgDescr(  # noqa: N816
    id=9,
    lenght=-1,
    name="Loginapp::lookApp",
    args_type=FIXED,
    args=(),
    desc="Check the component is alive",
)

queryLoad = MsgDescr(  # noqa: N816
    id=10,
    lenght=0,
    name="Loginapp::queryLoad",
    args_type=FIXED,
    args=(),
    desc="",
)

onDbmgrInitCompleted = MsgDescr(  # noqa: N816
    id=14,
    lenght=-1,
    name="Loginapp::onDbmgrInitCompleted",
    args_type=VARIABLE,
    args=(
        UINT32,  # gametime
        INT32,  # startID
        INT32,  # endID
        INT32,  # startGlobalOrder
        INT32,  # startGroupOrder
        STRING,  # digest
    ),
    desc="An app requests to obtain a callback for an entityID segment (???)",
)

onBaseappInitProgress = MsgDescr(  # noqa: N816
    id=24,
    lenght=8,
    name="Loginapp::onBaseappInitProgress",
    args_type=FIXED,
    args=(FLOAT,),  # progress
    desc="baseapp synchronizes its own initialization information",
)

onAppActiveTick = MsgDescr(  # noqa: N816
    id=55106,
    lenght=12,
    name="Loginapp::onAppActiveTick",
    args_type=FIXED,
    args=(
        INT32,  # componentType
        UINT64,  # componentID
    ),
    desc="Компонент сообщает, что он живой",
)

reqCloseServer = MsgDescr(  # noqa: N816
    id=23,
    lenght=-1,
    name="Loginapp::reqCloseServer",
    args_type=VARIABLE,
    args=(),
    desc="Отправить сигнал компоненту, что ему нужно остановиться",
)

reqAccountResetPassword = MsgDescr(  # noqa: N816
    id=12,
    lenght=-1,
    name="Loginapp::reqAccountResetPassword",
    args_type=FIXED,
    args=(STRING,),  # accountName
    desc="",
)

onReqAccountResetPasswordCB = MsgDescr(  # noqa: N816
    id=13,
    lenght=-1,
    name="Loginapp::onReqAccountResetPasswordCB",
    args_type=FIXED,
    args=(
        STRING,  # accountName
        STRING,  # email
        SERVER_ERROR_CODE,  # failedcode
        STRING,  # code
    ),
    desc="",
)

onLoginAccountQueryResultFromDbmgr = MsgDescr(  # noqa: N816
    id=15,
    lenght=-1,
    name="Loginapp::onLoginAccountQueryResultFromDbmgr",
    args_type=FIXED,
    args=(
        UINT16,  # ret_code
        STRING,  # login
        STRING,  # account_name
        STRING,  # password
        BOOL,  # needCheckPassword
        COMPONENT_ID,  # componentID
        ENTITY_ID,  # entityID
        DBID,  # dbid
        UINT32,  # flags
        UINT64,  # deadline
        STRING,  # datas
    ),
    desc="",
)

onLoginAccountQueryBaseappAddrFromBaseappmgr = MsgDescr(  # noqa: N816
    id=16,
    lenght=-1,
    name="Loginapp::onLoginAccountQueryBaseappAddrFromBaseappmgr",
    args_type=FIXED,
    args=(
        STRING,  # loginName
        STRING,  # accountName
        STRING,  # addr
        UINT16,  # tcp_port
        UINT16,  # udp_port
    ),
    desc="",
)

onReqCreateAccountResult = MsgDescr(  # noqa: N816
    id=17,
    lenght=-1,
    name="Loginapp::onReqCreateAccountResult",
    args_type=FIXED,
    args=(
        SERVER_ERROR_CODE,  # failedcode
        STRING,  # registerName
        STRING,  # password
        BLOB,  # getdatas
    ),
    desc="",
)

onReqCreateMailAccountResult = MsgDescr(  # noqa: N816
    id=18,
    lenght=-1,
    name="Loginapp::onReqCreateMailAccountResult",
    args_type=FIXED,
    args=(
        SERVER_ERROR_CODE,  # failedcode
        STRING,  # registerName
        STRING,  # password
        BLOB,  # getdatas
    ),
    desc="",
)

onAccountActivated = MsgDescr(  # noqa: N816
    id=19,
    lenght=-1,
    name="Loginapp::onAccountActivated",
    args_type=FIXED,
    args=(
        STRING,  # code
        BOOL,  # success
    ),
    desc="",
)

onAccountBindedEmail = MsgDescr(  # noqa: N816
    id=20,
    lenght=-1,
    name="Loginapp::onAccountBindedEmail",
    args_type=FIXED,
    args=(
        STRING,  # code
        BOOL,  # success
    ),
    desc="",
)

onAccountResetPassword = MsgDescr(  # noqa: N816
    id=21,
    lenght=-1,
    name="Loginapp::onAccountResetPassword",
    args_type=FIXED,
    args=(
        STRING,  # code
        BOOL,  # success
    ),
    desc="",
)

onReqAccountBindEmailAllocCallbackLoginapp = MsgDescr(  # noqa: N816
    id=22,
    lenght=-1,
    name="Loginapp::onReqAccountBindEmailAllocCallbackLoginapp",
    args_type=FIXED,
    args=(
        COMPONENT_ID,  # reqBaseappID
        ENTITY_ID,  # entityID
        STRING,  # accountName
        STRING,  # email
        SERVER_ERROR_CODE,  # failedcode
        STRING,  # code
    ),
    desc="",
)

startProfile = MsgDescr(  # noqa: N816
    id=25,
    lenght=0,
    name="Loginapp::startProfile",
    args_type=VARIABLE,
    args=(
        STRING,  # profileName
        INT8,  # profileType
        UINT32,  # timelen
    ),
    desc="",
)

reqKillServer = MsgDescr(  # noqa: N816
    id=26,
    lenght=0,
    name="Loginapp::reqKillServer",
    args_type=VARIABLE,
    args=(
        COMPONENT_ID,
        COMPONENT_TYPE,
        STRING,  # username
        INT32,  # uid
        STRING,  # reason
    ),
    desc="",
)

queryWatcher = MsgDescr(  # noqa: N816
    id=41003,
    lenght=-1,
    name="Loginapp::queryWatcher",
    args_type=VARIABLE,
    args=(STRING,),  # path
    desc="",
)


onLookApp = custom.change_component_owner(  # noqa: N816
    custom.onLookApp, ComponentType.LOGINAPP
)
onReqCloseServer = custom.change_component_owner(  # noqa: N816
    custom.onReqCloseServer, ComponentType.LOGINAPP
)

SPEC_BY_ID: MsgSpecById = {
    onLoginAccountQueryBaseappAddrFromBaseappmgr.id: onLoginAccountQueryBaseappAddrFromBaseappmgr,  # noqa: E501
    onLookApp.id: onLookApp,
    onReqCloseServer.id: onReqCloseServer,
    hello.id: hello,
    login.id: login,
    reqClose.id: reqClose,
    onClientActiveTick.id: onClientActiveTick,
    importClientMessages.id: importClientMessages,
    importServerErrorsDescr.id: importServerErrorsDescr,
    reqCreateAccount.id: reqCreateAccount,
    reqCreateMailAccount.id: reqCreateMailAccount,
    importClientSDK.id: importClientSDK,
    lookApp.id: lookApp,
    queryLoad.id: queryLoad,
    onDbmgrInitCompleted.id: onDbmgrInitCompleted,
    onBaseappInitProgress.id: onBaseappInitProgress,
    onAppActiveTick.id: onAppActiveTick,
    reqCloseServer.id: reqCloseServer,
    reqAccountResetPassword.id: reqAccountResetPassword,
    onReqAccountResetPasswordCB.id: onReqAccountResetPasswordCB,
    onLoginAccountQueryResultFromDbmgr.id: onLoginAccountQueryResultFromDbmgr,
    onReqCreateAccountResult.id: onReqCreateAccountResult,
    onReqCreateMailAccountResult.id: onReqCreateMailAccountResult,
    onAccountActivated.id: onAccountActivated,
    onAccountBindedEmail.id: onAccountBindedEmail,
    onAccountResetPassword.id: onAccountResetPassword,
    onReqAccountBindEmailAllocCallbackLoginapp.id: onReqAccountBindEmailAllocCallbackLoginapp,  # noqa: E501
    startProfile.id: startProfile,
    reqKillServer.id: reqKillServer,
    queryWatcher.id: queryWatcher,
}

__all__ = [
    "SPEC_BY_ID",
    "hello",
    "importClientMessages",
    "importClientSDK",
    "importServerErrorsDescr",
    "login",
    "lookApp",
    "onAccountActivated",
    "onAccountBindedEmail",
    "onAccountResetPassword",
    "onAppActiveTick",
    "onBaseappInitProgress",
    "onClientActiveTick",
    "onDbmgrInitCompleted",
    "onLoginAccountQueryBaseappAddrFromBaseappmgr",
    "onLoginAccountQueryResultFromDbmgr",
    "onLookApp",
    "onReqAccountBindEmailAllocCallbackLoginapp",
    "onReqAccountResetPasswordCB",
    "onReqCloseServer",
    "onReqCreateAccountResult",
    "onReqCreateMailAccountResult",
    "queryLoad",
    "queryWatcher",
    "reqAccountResetPassword",
    "reqClose",
    "reqCloseServer",
    "reqCreateAccount",
    "reqCreateMailAccount",
    "reqKillServer",
    "startProfile",
]
