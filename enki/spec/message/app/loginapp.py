"""Messages of Loginapp."""

from enki import message, kbetype

reqCreateAccount = message.MessageSpec(
    id=2,
    name='Loginapp::reqCreateAccount',
    args_type=message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

login = message.MessageSpec(
    id=3,
    name='Loginapp::login',
    args_type=message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

hello = message.MessageSpec(
    id=4,
    name='Loginapp::hello',
    args_type=message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importClientMessages = message.MessageSpec(
    id=5,
    name='Loginapp::importClientMessages',
    args_type=message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

reqCreateMailAccount = message.MessageSpec(
    id=6,
    name='Loginapp::reqCreateMailAccount',
    args_type=message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importClientSDK = message.MessageSpec(
    id=7,
    name='Loginapp::importClientSDK',
    args_type=message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importServerErrorsDescr = message.MessageSpec(
    id=8,
    name='Loginapp::importServerErrorsDescr',
    args_type=message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

onClientActiveTick = message.MessageSpec(
    id=11,
    name='Loginapp::onClientActiveTick',
    args_type=message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

reqAccountResetPassword = message.MessageSpec(
    id=12,
    name='Loginapp::reqAccountResetPassword',
    args_type=message.MsgArgsType.FIXED,
    field_types=(
        kbetype.STRING,
    ),
    desc=''
)
