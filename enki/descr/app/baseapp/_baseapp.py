"""Messages of BaseApp."""

from enki import kbetype
from .. import _message

__all__ = ('hello', 'importClientMessages', 'importClientEntityDef')


hello = _message.MessageDescr(
    id=200,
    name='BaseApp::hello',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.STRING,  # server version
        kbetype.STRING,  # assets version
        kbetype.BLOB,    # encrypted key
    ),
    desc='hello'
)

importClientMessages = _message.MessageDescr(
    id=207,
    name='Baseapp::importClientMessages',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(
    ),
    desc='The client requests to import the message protocol.'
)

importClientEntityDef = _message.MessageDescr(
    id=208,
    name='Baseapp::importClientEntityDef',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=tuple(
    ),
    desc='Client entitydef export.'
)

# TODO: [02.07.2021 burov_alexey@mail.ru]:
# Почему это сообщение здесь.
onUpdateDataFromClient = _message.MessageDescr(
    id=27,
    name='Baseapp::onUpdateDataFromClient',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.FLOAT,  # x
        kbetype.FLOAT,  # y
        kbetype.FLOAT,  # z
        kbetype.FLOAT,  # roll
        kbetype.FLOAT,  # pitch
        kbetype.FLOAT,  # yaw
        kbetype.BOOL,  # isOnGround
        kbetype.SPACE_ID  # spaceID
    ),
    desc='Update spatial arrangement on CellApp'
)
