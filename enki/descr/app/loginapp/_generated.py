"""Messages of Loginapp."""

from enki import kbetype, dcdescr

reqCreateAccount = dcdescr.MessageDescr(
    id=2,
    name='Loginapp::reqCreateAccount',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

login = dcdescr.MessageDescr(
    id=3,
    name='Loginapp::login',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

hello = dcdescr.MessageDescr(
    id=4,
    name='Loginapp::hello',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importClientMessages = dcdescr.MessageDescr(
    id=5,
    name='Loginapp::importClientMessages',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

reqCreateMailAccount = dcdescr.MessageDescr(
    id=6,
    name='Loginapp::reqCreateMailAccount',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importClientSDK = dcdescr.MessageDescr(
    id=7,
    name='Loginapp::importClientSDK',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importServerErrorsDescr = dcdescr.MessageDescr(
    id=8,
    name='Loginapp::importServerErrorsDescr',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

onClientActiveTick = dcdescr.MessageDescr(
    id=11,
    name='Loginapp::onClientActiveTick',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

reqAccountResetPassword = dcdescr.MessageDescr(
    id=12,
    name='Loginapp::reqAccountResetPassword',
    args_type=dcdescr.MsgArgsType.FIXED,
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
