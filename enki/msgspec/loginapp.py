"""Messages of LoginApp."""

from enki.kbeenum import ComponentType
from enki.kbetype import (
    BLOB,
    FLOAT,
    INT8,
    INT32,
    STRING,
    UINT16,
)
from enki.kbetype.decoders.custom_decoders import (
    COMPONENT_ID,
    COMPONENT_ORDER,
    COMPONENT_TYPE,
    ENTITY_ID,
    GAME_TIME,
)
from enki.msg.msg_descr import FIXED, VARIABLE, MsgDescr, MsgSpecById

from . import custom

# The "importClientMessages" response contains wrong message description of
# the "hello". I override the description here.
hello = MsgDescr(
    id=4,
    lenght=-1,
    name="Loginapp::hello",
    args_type=FIXED,
    args=(
        STRING,  # for what version of kbe client the plugin is
        STRING,  # for what version of server scripts the plugin is
        BLOB,  # encrypted key
    ),
    desc="hello",
)

# These is the real description of the "login" message.
# The "importClientMessages" response has wrong one.
login = MsgDescr(
    id=3,
    lenght=-1,
    name="Loginapp::login",
    args_type=FIXED,
    args=(
        INT8,  # client type (see ClientType)
        BLOB,  # binary data for "onRequestLogin" callback of script layer
        STRING,  # account name
        STRING,  # password
        STRING,  # force login for "bots" client type (not empty value is true)
    ),
    desc=(
        "The client requests to log in to the loginapp process of the server. "
        "After receiving the request, the process will return a gateway "
        "address after verification."
    ),
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
    args_type=FIXED,
    args=(STRING, STRING, BLOB),
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
        STRING,  # "ue4"
        INT32,  # TCP_RECV_BUFFER_MAX = 1024;
        STRING,  # callbackIP = ""
        UINT16,  # callbackPort = 0
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

onDbmgrInitCompleted = MsgDescr(  # noqa: N816
    id=14,
    lenght=-1,
    name="Loginapp::onDbmgrInitCompleted",
    args_type=VARIABLE,
    args=(
        GAME_TIME,  # gametime
        ENTITY_ID,  # startID
        ENTITY_ID,  # endID
        COMPONENT_ORDER,  # startGlobalOrder
        COMPONENT_ORDER,  # startGroupOrder
        STRING,  # digest
    ),
    desc="An app requests to obtain a callback for an entityID segment (???)",
)

onBaseappInitProgress = MsgDescr(  # noqa: N816
    id=24,
    lenght=8,
    name="Loginapp::onBaseappInitProgress",
    args_type=FIXED,
    args=(
        FLOAT,  # progress
    ),
    desc="baseapp synchronizes its own initialization information",
)

onAppActiveTick = MsgDescr(  # noqa: N816
    id=55106,
    lenght=12,
    name="Loginapp::onAppActiveTick",
    args_type=FIXED,
    args=(
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
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
    args=(STRING,),
    desc="",
)

onLookApp = custom.change_component_owner(  # noqa: N816
    custom.onLookApp, ComponentType.LOGINAPP
)
onReqCloseServer = custom.change_component_owner(  # noqa: N816
    custom.onReqCloseServer, ComponentType.LOGINAPP
)

SPEC_BY_ID: MsgSpecById = {
    onLookApp.id: onLookApp,
    onReqCloseServer.id: onReqCloseServer,
    hello.id: hello,
    login.id: login,
    onClientActiveTick.id: onClientActiveTick,
    importClientMessages.id: importClientMessages,
    importServerErrorsDescr.id: importServerErrorsDescr,
    reqCreateAccount.id: reqCreateAccount,
    reqCreateMailAccount.id: reqCreateMailAccount,
    importClientSDK.id: importClientSDK,
    lookApp.id: lookApp,
    onDbmgrInitCompleted.id: onDbmgrInitCompleted,
    onBaseappInitProgress.id: onBaseappInitProgress,
    onAppActiveTick.id: onAppActiveTick,
    reqCloseServer.id: reqCloseServer,
    reqAccountResetPassword.id: reqAccountResetPassword,
}

__all__ = [
    "SPEC_BY_ID",
    "hello",
    "importClientMessages",
    "importClientSDK",
    "importServerErrorsDescr",
    "login",
    "lookApp",
    "onAppActiveTick",
    "onBaseappInitProgress",
    "onClientActiveTick",
    "onDbmgrInitCompleted",
    "onLookApp",
    "onReqCloseServer",
    "reqAccountResetPassword",
    "reqCloseServer",
    "reqCreateAccount",
    "reqCreateMailAccount",
]
