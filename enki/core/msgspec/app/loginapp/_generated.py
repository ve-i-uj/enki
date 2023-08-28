"""Messages of Loginapp."""

from enki.core import kbeenum
from enki.core import kbetype
from enki.core.message import MsgDescr
from enki.core.msgspec.custom import SPEC_BY_ID


reqCreateAccount = MsgDescr(
    id=2,
    lenght=-1,
    name='Loginapp::reqCreateAccount',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

login = MsgDescr(
    id=3,
    lenght=-1,
    name='Loginapp::login',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

hello = MsgDescr(
    id=4,
    lenght=-1,
    name='Loginapp::hello',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importClientMessages = MsgDescr(
    id=5,
    lenght=0,
    name='Loginapp::importClientMessages',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

reqCreateMailAccount = MsgDescr(
    id=6,
    lenght=-1,
    name='Loginapp::reqCreateMailAccount',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importClientSDK = MsgDescr(
    id=7,
    lenght=-1,
    name='Loginapp::importClientSDK',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

importServerErrorsDescr = MsgDescr(
    id=8,
    lenght=0,
    name='Loginapp::importServerErrorsDescr',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

onClientActiveTick = MsgDescr(
    id=11,
    lenght=0,
    name='Loginapp::onClientActiveTick',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

reqAccountResetPassword = MsgDescr(
    id=12,
    lenght=-1,
    name='Loginapp::reqAccountResetPassword',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.STRING,
    ),
    desc=''
)

SPEC_BY_ID = {
    reqCreateAccount.id: reqCreateAccount,
    login.id: login,
    hello.id: hello,
    importClientMessages.id: importClientMessages,
    reqCreateMailAccount.id: reqCreateMailAccount,
    importClientSDK.id: importClientSDK,
    importServerErrorsDescr.id: importServerErrorsDescr,
    onClientActiveTick.id: onClientActiveTick,
    reqAccountResetPassword.id: reqAccountResetPassword
}

__all__ = [
    'SPEC_BY_ID',
    'reqCreateAccount', 'login', 'hello',
    'importClientMessages', 'reqCreateMailAccount', 'importClientSDK',
    'importServerErrorsDescr', 'onClientActiveTick', 'reqAccountResetPassword'
]
