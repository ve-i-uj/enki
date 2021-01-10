"""Messages of BaseApp."""

from enki import message
from enki import kbetype

__all__ = ('hello', 'importClientMessages', 'importClientEntityDef')


hello = message.MessageSpec(
    id=200,
    name='BaseApp::hello',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.STRING,  # server version
        kbetype.STRING,  # assets version
        kbetype.BLOB,    # encrypted key
    ),
    desc='hello'
)

importClientMessages = message.MessageSpec(
    id=207,
    name='Baseapp::importClientMessages',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(
    ),
    desc='The client requests to import the message protocol.'
)

importClientEntityDef = message.MessageSpec(
    id=208,
    name='Baseapp::importClientEntityDef',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=tuple(
    ),
    desc='Client entitydef export.'
)
