"""Messages of Loginapp."""

from enki import kbetype, kbeenum, dcdescr

reqCreateAccount = dcdescr.MessageDescr(
    id=2,
    lenght=-1,
    name='Loginapp::reqCreateAccount',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

login = dcdescr.MessageDescr(
    id=3,
    lenght=-1,
    name='Loginapp::login',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

hello = dcdescr.MessageDescr(
    id=4,
    lenght=-1,
    name='Loginapp::hello',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importClientMessages = dcdescr.MessageDescr(
    id=5,
    lenght=0,
    name='Loginapp::importClientMessages',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

reqCreateMailAccount = dcdescr.MessageDescr(
    id=6,
    lenght=-1,
    name='Loginapp::reqCreateMailAccount',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importClientSDK = dcdescr.MessageDescr(
    id=7,
    lenght=-1,
    name='Loginapp::importClientSDK',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importServerErrorsDescr = dcdescr.MessageDescr(
    id=8,
    lenght=0,
    name='Loginapp::importServerErrorsDescr',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

onClientActiveTick = dcdescr.MessageDescr(
    id=11,
    lenght=0,
    name='Loginapp::onClientActiveTick',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

reqAccountResetPassword = dcdescr.MessageDescr(
    id=12,
    lenght=-1,
    name='Loginapp::reqAccountResetPassword',
    args_type=kbeenum.MsgArgsType.FIXED,
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
