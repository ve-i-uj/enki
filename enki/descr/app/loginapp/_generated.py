"""Messages of Loginapp."""

from enki import kbetype
from .. import _message

reqCreateAccount = _message.MessageSpec(
    id=2,
    name='Loginapp::reqCreateAccount',
    args_type=_message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

login = _message.MessageSpec(
    id=3,
    name='Loginapp::login',
    args_type=_message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

hello = _message.MessageSpec(
    id=4,
    name='Loginapp::hello',
    args_type=_message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importClientMessages = _message.MessageSpec(
    id=5,
    name='Loginapp::importClientMessages',
    args_type=_message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

reqCreateMailAccount = _message.MessageSpec(
    id=6,
    name='Loginapp::reqCreateMailAccount',
    args_type=_message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importClientSDK = _message.MessageSpec(
    id=7,
    name='Loginapp::importClientSDK',
    args_type=_message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importServerErrorsDescr = _message.MessageSpec(
    id=8,
    name='Loginapp::importServerErrorsDescr',
    args_type=_message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

onClientActiveTick = _message.MessageSpec(
    id=11,
    name='Loginapp::onClientActiveTick',
    args_type=_message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

reqAccountResetPassword = _message.MessageSpec(
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
