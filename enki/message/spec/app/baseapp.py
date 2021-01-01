"""Messages of Baseapp."""

from enki import message
from enki import kbetype

logoutBaseapp = message.MessageSpec(
    id=24,
    name='Baseapp::logoutBaseapp',
    args_type=message.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT64,
        kbetype.INT32,
    ),
    desc=''
)

onUpdateDataFromClient = message.MessageSpec(
    id=27,
    name='Baseapp::onUpdateDataFromClient',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateDataFromClientForControlledEntity = message.MessageSpec(
    id=28,
    name='Baseapp::onUpdateDataFromClientForControlledEntity',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

reqAccountBindEmail = message.MessageSpec(
    id=50,
    name='Baseapp::reqAccountBindEmail',
    args_type=message.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT32,
        kbetype.STRING,
        kbetype.STRING,
    ),
    desc=''
)

reqAccountNewPassword = message.MessageSpec(
    id=53,
    name='Baseapp::reqAccountNewPassword',
    args_type=message.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT32,
        kbetype.STRING,
        kbetype.STRING,
    ),
    desc=''
)

forwardEntityMessageToCellappFromClient = message.MessageSpec(
    id=57,
    name='Entity::forwardEntityMessageToCellappFromClient',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

hello = message.MessageSpec(
    id=200,
    name='Baseapp::hello',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

loginBaseapp = message.MessageSpec(
    id=202,
    name='Baseapp::loginBaseapp',
    args_type=message.MsgArgsType.FIXED,
    field_types=(
        kbetype.STRING,
        kbetype.STRING,
    ),
    desc=''
)

reloginBaseapp = message.MessageSpec(
    id=204,
    name='Baseapp::reloginBaseapp',
    args_type=message.MsgArgsType.FIXED,
    field_types=(
        kbetype.STRING,
        kbetype.STRING,
        kbetype.UINT64,
        kbetype.INT32,
    ),
    desc=''
)

onRemoteCallCellMethodFromClient = message.MessageSpec(
    id=205,
    name='Baseapp::onRemoteCallCellMethodFromClient',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onClientActiveTick = message.MessageSpec(
    id=206,
    name='Baseapp::onClientActiveTick',
    args_type=message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importClientMessages = message.MessageSpec(
    id=207,
    name='Baseapp::importClientMessages',
    args_type=message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importClientEntityDef = message.MessageSpec(
    id=208,
    name='Baseapp::importClientEntityDef',
    args_type=message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

onRemoteMethodCall = message.MessageSpec(
    id=302,
    name='Entity::onRemoteMethodCall',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)
