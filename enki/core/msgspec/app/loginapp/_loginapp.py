"""Messages of LoginApp"""

from enki.core import kbeenum
from enki.core import kbetype
from enki.core.message import MsgDescr


# The "importClientMessages" response contains wrong message description of
# the "hello". I override the description here.
hello = MsgDescr(
    id=4,
    lenght=-1,
    name='Loginapp::hello',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.STRING,     # for what version of kbe client the plugin is
        kbetype.STRING,     # for what version of server scripts the plugin is
        kbetype.BLOB,       # encrypted key
    ),
    desc='hello'
)

# These is the real description of the "login" message.
# The "importClientMessages" response has wrong one.
login = MsgDescr(
    id=3,
    lenght=-1,
    name='Loginapp::login',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT8,       # client type (see ClientType)
        kbetype.BLOB,       # binary data for "onRequestLogin" callback of script layer
        kbetype.STRING,     # account name
        kbetype.STRING,     # password
        kbetype.STRING,     # force login for "bots" client type (not empty value is true)
    ),
    desc='The client requests to log in to the loginapp process of the server. After receiving the request, the process will return a gateway address after verification.'  # noqa
)

importClientMessages = MsgDescr(
    id=5,
    lenght=0,
    name='Loginapp::importClientMessages',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc='The client requests to import the message protocol.'
)

importServerErrorsDescr = MsgDescr(
    id=8,
    lenght=0,
    name='Loginapp::importServerErrorsDescr',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

reqCreateAccount = MsgDescr(
    id=2,
    lenght=-1,
    name='Loginapp::reqCreateAccount',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.STRING,
        kbetype.STRING,
        kbetype.BLOB
    ),
    desc=''
)

reqCreateMailAccount = MsgDescr(
    id=6,
    lenght=-1,
    name='Loginapp::reqCreateMailAccount',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.STRING,
        kbetype.STRING,
        kbetype.BLOB
    ),
    desc=''
)

importClientSDK = MsgDescr(
    id=7,
    lenght=-1,
    name='Loginapp::importClientSDK',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.STRING,  # "ue4"
        kbetype.INT32,  # TCP_RECV_BUFFER_MAX = 1024;
        kbetype.STRING, # callbackIP = ""
        kbetype.UINT16, # callbackPort = 0
    ),
    desc=''
)

lookApp = MsgDescr(
    id=9,
    lenght=-1,
    name='Baseapp::lookApp',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
    ]),
    desc='Check the component is alive'
)

onDbmgrInitCompleted = MsgDescr(
    id=14,
    lenght=-1,
    name='Loginapp::onDbmgrInitCompleted',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=tuple([
        kbetype.GAME_TIME,  # gametime
        kbetype.ENTITY_ID,  # startID
        kbetype.ENTITY_ID,  # endID
        kbetype.COMPONENT_ORDER,  # startGlobalOrder
        kbetype.COMPONENT_ORDER,  # startGroupOrder
        kbetype.STRING,  # digest
    ]),
    desc='An app requests to obtain a callback for an entityID segment (???)'
)

onBaseappInitProgress = MsgDescr(
    id=24,
    lenght=8,
    name='Loginapp::onBaseappInitProgress',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
        kbetype.FLOAT,  # progress
    ]),
    desc='baseapp synchronizes its own initialization information'
)

onAppActiveTick = MsgDescr(
    id=55106,
    lenght=12,
    name='Loginapp::onAppActiveTick',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
        kbetype.COMPONENT_TYPE,  # componentType
        kbetype.COMPONENT_ID,  # componentID
    ]),
    desc='Компонент сообщает, что он живой'
)

SPEC_BY_ID = {
    hello.id: hello,
    login.id: login,
    importClientMessages.id: importClientMessages,
    importServerErrorsDescr.id: importServerErrorsDescr,
    reqCreateAccount.id: reqCreateAccount,
    reqCreateMailAccount.id: reqCreateMailAccount,
    importClientSDK.id: importClientSDK,

    lookApp.id: lookApp,
    onDbmgrInitCompleted.id: onDbmgrInitCompleted,
    onBaseappInitProgress.id: onBaseappInitProgress,
    onAppActiveTick.id: onAppActiveTick,
}

__all__ = [
    'SPEC_BY_ID',
    'hello',
    'login',
    'importClientMessages',
    'importServerErrorsDescr',
    'reqCreateAccount',
    'reqCreateMailAccount',
    'importClientSDK',

    'lookApp',
    'onDbmgrInitCompleted',
    'onBaseappInitProgress',
    'onAppActiveTick',
]
