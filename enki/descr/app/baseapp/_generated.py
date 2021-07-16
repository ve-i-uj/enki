"""Messages of Baseapp."""

from enki import kbetype, dcdescr

logoutBaseapp = dcdescr.MessageDescr(
    id=24,
    name='Baseapp::logoutBaseapp',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT64,
        kbetype.INT32,
    ),
    desc=''
)

onUpdateDataFromClient = dcdescr.MessageDescr(
    id=27,
    name='Baseapp::onUpdateDataFromClient',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateDataFromClientForControlledEntity = dcdescr.MessageDescr(
    id=28,
    name='Baseapp::onUpdateDataFromClientForControlledEntity',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

reqAccountBindEmail = dcdescr.MessageDescr(
    id=51,
    name='Baseapp::reqAccountBindEmail',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT32,
        kbetype.STRING,
        kbetype.STRING,
    ),
    desc=''
)

reqAccountNewPassword = dcdescr.MessageDescr(
    id=54,
    name='Baseapp::reqAccountNewPassword',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT32,
        kbetype.STRING,
        kbetype.STRING,
    ),
    desc=''
)

forwardEntityMessageToCellappFromClient = dcdescr.MessageDescr(
    id=58,
    name='Entity::forwardEntityMessageToCellappFromClient',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

hello = dcdescr.MessageDescr(
    id=200,
    name='Baseapp::hello',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

loginBaseapp = dcdescr.MessageDescr(
    id=202,
    name='Baseapp::loginBaseapp',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=(
        kbetype.STRING,
        kbetype.STRING,
    ),
    desc=''
)

reloginBaseapp = dcdescr.MessageDescr(
    id=204,
    name='Baseapp::reloginBaseapp',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=(
        kbetype.STRING,
        kbetype.STRING,
        kbetype.UINT64,
        kbetype.INT32,
    ),
    desc=''
)

onRemoteCallCellMethodFromClient = dcdescr.MessageDescr(
    id=205,
    name='Baseapp::onRemoteCallCellMethodFromClient',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onClientActiveTick = dcdescr.MessageDescr(
    id=206,
    name='Baseapp::onClientActiveTick',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importClientMessages = dcdescr.MessageDescr(
    id=207,
    name='Baseapp::importClientMessages',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importClientEntityDef = dcdescr.MessageDescr(
    id=208,
    name='Baseapp::importClientEntityDef',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

onRemoteMethodCall = dcdescr.MessageDescr(
    id=302,
    name='Entity::onRemoteMethodCall',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

__all__ = (
    'logoutBaseapp', 'onUpdateDataFromClient', 'onUpdateDataFromClientForControlledEntity',
    'reqAccountBindEmail', 'reqAccountNewPassword', 'forwardEntityMessageToCellappFromClient',
    'hello', 'loginBaseapp', 'reloginBaseapp',
    'onRemoteCallCellMethodFromClient', 'onClientActiveTick', 'importClientMessages',
    'importClientEntityDef', 'onRemoteMethodCall'
)
