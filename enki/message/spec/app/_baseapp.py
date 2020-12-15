"""Messages of BaseApp."""

from enki import message
from enki import kbetype

hello = message.MessageSpec(
    id=200,
    name='BaseApp::hello',
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
    field_types=tuple(
    ),
    desc='The client requests to import the message protocol.'
)

importClientEntityDef = message.MessageSpec(
    id=208,
    name='Baseapp::importClientEntityDef',
    field_types=tuple(
    ),
    desc='Client entitydef export.'
)
