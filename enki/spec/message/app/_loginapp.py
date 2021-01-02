"""Messages of LoginApp"""

from enki import message
from enki import kbetype

hello = message.MessageSpec(
    id=4,
    name='Loginapp::hello',
    args_type=message.MsgArgsType.FIXED,
    field_types=(
        kbetype.STRING,
        kbetype.STRING,
        kbetype.BLOB,
    ),
    desc='hello'
)

login = message.MessageSpec(
    id=3,
    name='Loginapp::login',
    args_type=message.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT8,
        kbetype.BLOB,
        kbetype.STRING,
        kbetype.STRING,
        kbetype.STRING,
    ),
    desc='The client requests to log in to the loginapp process of the server. After receiving the request, the process will return a gateway address after verification.'  # noqa
)

importClientMessages = message.MessageSpec(
    id=5,
    name='Loginapp::importClientMessages',
    args_type=message.MsgArgsType.FIXED,
    field_types=tuple(
    ),
    desc='The client requests to import the message protocol.'
)

importServerErrorsDescr = message.MessageSpec(
    id=8,
    name='Loginapp::importServerErrorsDescr',
    args_type=message.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)
