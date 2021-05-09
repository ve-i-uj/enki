"""Messages of Loginapp."""

from enki import kbetype
from .. import _message

reqCreateAccount = _message.MessageDescr(
    id=2,
    name='Loginapp::reqCreateAccount',
    args_type=_message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

login = _message.MessageDescr(
    id=3,
    name='Loginapp::login',
    args_type=_message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

hello = _message.MessageDescr(
    id=4,
    name='Loginapp::hello',
    args_type=_message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importClientMessages = _message.MessageDescr(
    id=5,
    name='Loginapp::importClientMessages',
    args_type=_message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

reqCreateMailAccount = _message.MessageDescr(
    id=6,
    name='Loginapp::reqCreateMailAccount',
    args_type=_message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importClientSDK = _message.MessageDescr(
    id=7,
    name='Loginapp::importClientSDK',
    args_type=_message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importServerErrorsDescr = _message.MessageDescr(
    id=8,
    name='Loginapp::importServerErrorsDescr',
    args_type=_message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

onClientActiveTick = _message.MessageDescr(
    id=11,
    name='Loginapp::onClientActiveTick',
    args_type=_message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

reqAccountResetPassword = _message.MessageDescr(
    id=12,
    name='Loginapp::reqAccountResetPassword',
    args_type=_message.MsgArgsType.FIXED,
    field_types=(
        kbetype.STRING,
    ),
    desc=''
)

__all__ = (
    'reqCreateAccount', 'login', 'hello',
    'importClientMessages', 'reqCreateMailAccount', 'importClientSDK',
    'importServerErrorsDescr', 'onClientActiveTick', 'reqAccountResetPassword'
)
