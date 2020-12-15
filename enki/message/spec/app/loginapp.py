"""Messages of Loginapp."""

from enki import message
from enki import kbetype

reqCreateAccount = message.MessageSpec(
    id=2,
    name='Loginapp::reqCreateAccount',
    field_types=tuple(),
    desc=''
)

login = message.MessageSpec(
    id=3,
    name='Loginapp::login',
    field_types=tuple(),
    desc=''
)

hello = message.MessageSpec(
    id=4,
    name='Loginapp::hello',
    field_types=tuple(),
    desc=''
)

importClientMessages = message.MessageSpec(
    id=5,
    name='Loginapp::importClientMessages',
    field_types=tuple(),
    desc=''
)

reqCreateMailAccount = message.MessageSpec(
    id=6,
    name='Loginapp::reqCreateMailAccount',
    field_types=tuple(),
    desc=''
)

importClientSDK = message.MessageSpec(
    id=7,
    name='Loginapp::importClientSDK',
    field_types=tuple(),
    desc=''
)

importServerErrorsDescr = message.MessageSpec(
    id=8,
    name='Loginapp::importServerErrorsDescr',
    field_types=tuple(),
    desc=''
)

onClientActiveTick = message.MessageSpec(
    id=11,
    name='Loginapp::onClientActiveTick',
    field_types=tuple(),
    desc=''
)

reqAccountResetPassword = message.MessageSpec(
    id=12,
    name='Loginapp::reqAccountResetPassword',
    field_types=(
        kbetype.STRING,
    ),
    desc=''
)
