"""Messages of Loginapp."""

from enki import kbeenum
from enki.net.kbeclient import kbetype
from enki.net.kbeclient.message import MsgDescr


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

__all__ = (
    'reqCreateAccount', 'login', 'hello',
    'importClientMessages', 'reqCreateMailAccount', 'importClientSDK',
    'importServerErrorsDescr', 'onClientActiveTick', 'reqAccountResetPassword'
)