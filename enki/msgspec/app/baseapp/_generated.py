"""Messages of Baseapp."""

from enki import kbeenum

from enki.core import kbetype
from enki.core.message import MsgDescr

logoutBaseapp = MsgDescr(  # noqa: N816
    id=24,
    lenght=12,
    name='Baseapp::logoutBaseapp',
    args_type=FIXED,
    args=(
        UINT64,
        INT32,
    ),
    desc=''
)

onUpdateDataFromClient = MsgDescr(  # noqa: N816
    id=27,
    lenght=-1,
    name='Baseapp::onUpdateDataFromClient',
    args_type=VARIABLE,
    args=(UINT8_ARRAY, ),
    desc=''
)

onUpdateDataFromClientForControlledEntity = MsgDescr(  # noqa: N816
    id=28,
    lenght=-1,
    name='Baseapp::onUpdateDataFromClientForControlledEntity',
    args_type=VARIABLE,
    args=(UINT8_ARRAY, ),
    desc=''
)

reqAccountBindEmail = MsgDescr(  # noqa: N816
    id=51,
    lenght=-1,
    name='Baseapp::reqAccountBindEmail',
    args_type=FIXED,
    args=(
        INT32,
        STRING,
        STRING,
    ),
    desc=''
)

reqAccountNewPassword = MsgDescr(  # noqa: N816
    id=54,
    lenght=-1,
    name='Baseapp::reqAccountNewPassword',
    args_type=FIXED,
    args=(
        INT32,
        STRING,
        STRING,
    ),
    desc=''
)

forwardEntityMessageToCellappFromClient = MsgDescr(  # noqa: N816
    id=58,
    lenght=-1,
    name='Entity::forwardEntityMessageToCellappFromClient',
    args_type=VARIABLE,
    args=(UINT8_ARRAY, ),
    desc=''
)

hello = MsgDescr(  # noqa: N816
    id=200,
    lenght=-1,
    name='Baseapp::hello',
    args_type=VARIABLE,
    args=(UINT8_ARRAY, ),
    desc=''
)

loginBaseapp = MsgDescr(  # noqa: N816
    id=202,
    lenght=-1,
    name='Baseapp::loginBaseapp',
    args_type=FIXED,
    args=(
        STRING,
        STRING,
    ),
    desc=''
)

reloginBaseapp = MsgDescr(  # noqa: N816
    id=204,
    lenght=-1,
    name='Baseapp::reloginBaseapp',
    args_type=FIXED,
    args=(
        STRING,
        STRING,
        UINT64,
        INT32,
    ),
    desc=''
)

onRemoteCallCellMethodFromClient = MsgDescr(  # noqa: N816
    id=205,
    lenght=-1,
    name='Baseapp::onRemoteCallCellMethodFromClient',
    args_type=VARIABLE,
    args=(UINT8_ARRAY, ),
    desc=''
)

onClientActiveTick = MsgDescr(  # noqa: N816
    id=206,
    lenght=0,
    name='Baseapp::onClientActiveTick',
    args_type=FIXED,
    args=(),
    desc=''
)

importClientMessages = MsgDescr(  # noqa: N816
    id=207,
    lenght=0,
    name='Baseapp::importClientMessages',
    args_type=FIXED,
    args=(),
    desc=''
)

importClientEntityDef = MsgDescr(  # noqa: N816
    id=208,
    lenght=0,
    name='Baseapp::importClientEntityDef',
    args_type=FIXED,
    args=(),
    desc=''
)

onRemoteMethodCall = MsgDescr(  # noqa: N816
    id=302,
    lenght=-1,
    name='Entity::onRemoteMethodCall',
    args_type=VARIABLE,
    args=(UINT8_ARRAY, ),
    desc=''
)

SPEC_BY_ID = {
    logoutBaseapp.id: logoutBaseapp,
    onUpdateDataFromClient.id: onUpdateDataFromClient,
    onUpdateDataFromClientForControlledEntity.id: onUpdateDataFromClientForControlledEntity,
    reqAccountBindEmail.id: reqAccountBindEmail,
    reqAccountNewPassword.id: reqAccountNewPassword,
    forwardEntityMessageToCellappFromClient.id: forwardEntityMessageToCellappFromClient,
    hello.id: hello,
    loginBaseapp.id: loginBaseapp,
    reloginBaseapp.id: reloginBaseapp,
    onRemoteCallCellMethodFromClient.id: onRemoteCallCellMethodFromClient,
    onClientActiveTick.id: onClientActiveTick,
    importClientMessages.id: importClientMessages,
    importClientEntityDef.id: importClientEntityDef,
    onRemoteMethodCall.id: onRemoteMethodCall
}


__all__ = [
    'SPEC_BY_ID',
    'logoutBaseapp', 'onUpdateDataFromClient', 'onUpdateDataFromClientForControlledEntity',
    'reqAccountBindEmail', 'reqAccountNewPassword', 'forwardEntityMessageToCellappFromClient',
    'hello', 'loginBaseapp', 'reloginBaseapp',
    'onRemoteCallCellMethodFromClient', 'onClientActiveTick', 'importClientMessages',
    'importClientEntityDef', 'onRemoteMethodCall'
]
