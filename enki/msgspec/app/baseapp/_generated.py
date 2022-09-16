"""Messages of Baseapp."""

from enki import kbetype, kbeenum, dcdescr

logoutBaseapp = dcdescr.MessageDescr(
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

onUpdateDataFromClient = dcdescr.MessageDescr(
    id=27,
    lenght=-1,
    name='Baseapp::onUpdateDataFromClient',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onUpdateDataFromClientForControlledEntity = dcdescr.MessageDescr(
    id=28,
    lenght=-1,
    name='Baseapp::onUpdateDataFromClientForControlledEntity',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

reqAccountBindEmail = dcdescr.MessageDescr(
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

reqAccountNewPassword = dcdescr.MessageDescr(
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

forwardEntityMessageToCellappFromClient = dcdescr.MessageDescr(
    id=58,
    lenght=-1,
    name='Entity::forwardEntityMessageToCellappFromClient',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

hello = dcdescr.MessageDescr(
    id=200,
    lenght=-1,
    name='Baseapp::hello',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

loginBaseapp = dcdescr.MessageDescr(
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

reloginBaseapp = dcdescr.MessageDescr(
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

onRemoteCallCellMethodFromClient = dcdescr.MessageDescr(
    id=205,
    lenght=-1,
    name='Baseapp::onRemoteCallCellMethodFromClient',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onClientActiveTick = dcdescr.MessageDescr(
    id=206,
    lenght=0,
    name='Baseapp::onClientActiveTick',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importClientMessages = dcdescr.MessageDescr(
    id=207,
    lenght=0,
    name='Baseapp::importClientMessages',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importClientEntityDef = dcdescr.MessageDescr(
    id=208,
    lenght=0,
    name='Baseapp::importClientEntityDef',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

onRemoteMethodCall = dcdescr.MessageDescr(
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
