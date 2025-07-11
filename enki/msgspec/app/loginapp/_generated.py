"""Messages of Loginapp."""

from enki import kbeenum
from enki.core import kbetype
from enki.core.message import MsgDescr
from enki.__tmp.custom import SPEC_BY_ID


reqCreateAccount = MsgDescr(  # noqa: N816
    id=2,
    lenght=-1,
    name='Loginapp::reqCreateAccount',
    args_type=FIXED,
    args=(),
    desc=''
)

login = MsgDescr(  # noqa: N816
    id=3,
    lenght=-1,
    name='Loginapp::login',
    args_type=FIXED,
    args=(),
    desc=''
)

hello = MsgDescr(  # noqa: N816
    id=4,
    lenght=-1,
    name='Loginapp::hello',
    args_type=FIXED,
    args=(),
    desc=''
)

importClientMessages = MsgDescr(  # noqa: N816
    id=5,
    lenght=0,
    name='Loginapp::importClientMessages',
    args_type=FIXED,
    args=(),
    desc=''
)

reqCreateMailAccount = MsgDescr(  # noqa: N816
    id=6,
    lenght=-1,
    name='Loginapp::reqCreateMailAccount',
    args_type=FIXED,
    args=(),
    desc=''
)

importClientSDK = MsgDescr(  # noqa: N816
    id=7,
    lenght=-1,
    name='Loginapp::importClientSDK',
    args_type=FIXED,
    args=(),
    desc=''
)

importServerErrorsDescr = MsgDescr(  # noqa: N816
    id=8,
    lenght=0,
    name='Loginapp::importServerErrorsDescr',
    args_type=FIXED,
    args=(),
    desc=''
)

onClientActiveTick = MsgDescr(  # noqa: N816
    id=11,
    lenght=0,
    name='Loginapp::onClientActiveTick',
    args_type=FIXED,
    args=(),
    desc=''
)

reqAccountResetPassword = MsgDescr(  # noqa: N816
    id=12,
    lenght=-1,
    name='Loginapp::reqAccountResetPassword',
    args_type=FIXED,
    args=(
        STRING,
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
