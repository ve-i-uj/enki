"""Messages of Baseapp."""

from enki import kbetype
from .. import _message

logoutBaseapp = _message.MessageDescr(
    id=24,
    name='Baseapp::logoutBaseapp',
    args_type=_message.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT64,
        kbetype.INT32,
    ),
    desc=''
)

onUpdateDataFromClient = _message.MessageDescr(
    id=27,
    name='Baseapp::onUpdateDataFromClient',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onUpdateDataFromClientForControlledEntity = _message.MessageDescr(
    id=28,
    name='Baseapp::onUpdateDataFromClientForControlledEntity',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

reqAccountBindEmail = _message.MessageDescr(
    id=50,
    name='Baseapp::reqAccountBindEmail',
    args_type=_message.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT32,
        kbetype.STRING,
        kbetype.STRING,
    ),
    desc=''
)

reqAccountNewPassword = _message.MessageDescr(
    id=53,
    name='Baseapp::reqAccountNewPassword',
    args_type=_message.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT32,
        kbetype.STRING,
        kbetype.STRING,
    ),
    desc=''
)

forwardEntityMessageToCellappFromClient = _message.MessageDescr(
    id=57,
    name='Entity::forwardEntityMessageToCellappFromClient',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

hello = _message.MessageDescr(
    id=200,
    name='Baseapp::hello',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

loginBaseapp = _message.MessageDescr(
    id=202,
    name='Baseapp::loginBaseapp',
    args_type=_message.MsgArgsType.FIXED,
    field_types=(
        kbetype.STRING,
        kbetype.STRING,
    ),
    desc=''
)

reloginBaseapp = _message.MessageDescr(
    id=204,
    name='Baseapp::reloginBaseapp',
    args_type=_message.MsgArgsType.FIXED,
    field_types=(
        kbetype.STRING,
        kbetype.STRING,
        kbetype.UINT64,
        kbetype.INT32,
    ),
    desc=''
)

onRemoteCallCellMethodFromClient = _message.MessageDescr(
    id=205,
    name='Baseapp::onRemoteCallCellMethodFromClient',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc=''
)

onClientActiveTick = _message.MessageDescr(
    id=206,
    name='Baseapp::onClientActiveTick',
    args_type=_message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importClientMessages = _message.MessageDescr(
    id=207,
    name='Baseapp::importClientMessages',
    args_type=_message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importClientEntityDef = _message.MessageDescr(
    id=208,
    name='Baseapp::importClientEntityDef',
    args_type=_message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

onRemoteMethodCall = _message.MessageDescr(
    id=302,
    name='Entity::onRemoteMethodCall',
    args_type=_message.MsgArgsType.VARIABLE,
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
