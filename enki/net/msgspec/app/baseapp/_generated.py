"""Messages of Baseapp."""

from enki import kbeenum

from enki.net.kbeclient import kbetype
from enki.net.kbeclient.message import MsgDescr


logoutBaseapp = MsgDescr(
    id=24,
    lenght=12,
    name='Baseapp::logoutBaseapp',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT64,
        kbetype.INT32,
    ),
    desc=''
)

onUpdateDataFromClient = MsgDescr(
    id=27,
    lenght=-1,
    name='Baseapp::onUpdateDataFromClient',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateDataFromClientForControlledEntity = MsgDescr(
    id=28,
    lenght=-1,
    name='Baseapp::onUpdateDataFromClientForControlledEntity',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

reqAccountBindEmail = MsgDescr(
    id=51,
    lenght=-1,
    name='Baseapp::reqAccountBindEmail',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT32,
        kbetype.STRING,
        kbetype.STRING,
    ),
    desc=''
)

reqAccountNewPassword = MsgDescr(
    id=54,
    lenght=-1,
    name='Baseapp::reqAccountNewPassword',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT32,
        kbetype.STRING,
        kbetype.STRING,
    ),
    desc=''
)

forwardEntityMessageToCellappFromClient = MsgDescr(
    id=58,
    lenght=-1,
    name='Entity::forwardEntityMessageToCellappFromClient',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

hello = MsgDescr(
    id=200,
    lenght=-1,
    name='Baseapp::hello',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

loginBaseapp = MsgDescr(
    id=202,
    lenght=-1,
    name='Baseapp::loginBaseapp',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.STRING,
        kbetype.STRING,
    ),
    desc=''
)

reloginBaseapp = MsgDescr(
    id=204,
    lenght=-1,
    name='Baseapp::reloginBaseapp',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.STRING,
        kbetype.STRING,
        kbetype.UINT64,
        kbetype.INT32,
    ),
    desc=''
)

onRemoteCallCellMethodFromClient = MsgDescr(
    id=205,
    lenght=-1,
    name='Baseapp::onRemoteCallCellMethodFromClient',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onClientActiveTick = MsgDescr(
    id=206,
    lenght=0,
    name='Baseapp::onClientActiveTick',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importClientMessages = MsgDescr(
    id=207,
    lenght=0,
    name='Baseapp::importClientMessages',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importClientEntityDef = MsgDescr(
    id=208,
    lenght=0,
    name='Baseapp::importClientEntityDef',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

onRemoteMethodCall = MsgDescr(
    id=302,
    lenght=-1,
    name='Entity::onRemoteMethodCall',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

__all__ = (
    'logoutBaseapp', 'onUpdateDataFromClient', 'onUpdateDataFromClientForControlledEntity',
    'reqAccountBindEmail', 'reqAccountNewPassword', 'forwardEntityMessageToCellappFromClient',
    'hello', 'loginBaseapp', 'reloginBaseapp',
    'onRemoteCallCellMethodFromClient', 'onClientActiveTick', 'importClientMessages',
    'importClientEntityDef', 'onRemoteMethodCall'
)
