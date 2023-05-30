"""Messages of BaseApp."""

from enki.core import kbeenum
from enki.core import kbetype
from enki.core.message import MsgDescr


hello = MsgDescr(
    id=200,
    lenght=-1,
    name='BaseApp::hello',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.STRING,  # server version
        kbetype.STRING,  # assets version
        kbetype.BLOB,    # encrypted key
    ),
    desc='hello'
)

importClientMessages = MsgDescr(
    id=207,
    lenght=0,
    name='Baseapp::importClientMessages',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc='The client requests to import the message protocol.'
)

importClientEntityDef = MsgDescr(
    id=208,
    lenght=0,
    name='Baseapp::importClientEntityDef',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc='TCPClient entitydef export.'
)

onUpdateDataFromClient = MsgDescr(
    id=27,
    lenght=-1,
    name='Baseapp::onUpdateDataFromClient',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.FLOAT,
        kbetype.FLOAT,
        kbetype.FLOAT,
        kbetype.FLOAT,
        kbetype.FLOAT,
        kbetype.FLOAT,
        kbetype.BOOL,
        kbetype.SPACE_ID,
    ),
    desc=''
)

onUpdateDataFromClientForControlledEntity = MsgDescr(
    id=28,
    lenght=-1,
    name='Baseapp::onUpdateDataFromClientForControlledEntity',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.ENTITY_ID,
        kbetype.FLOAT,
        kbetype.FLOAT,
        kbetype.FLOAT,
        kbetype.FLOAT,
        kbetype.FLOAT,
        kbetype.FLOAT,
        kbetype.BOOL,
        kbetype.SPACE_ID,
    ),
    desc=''
)

lookApp = MsgDescr(
    id=8,
    lenght=-1,
    name='Baseapp::lookApp',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
    ]),
    desc='Check the component is alive'
)

SPEC_BY_ID = {
    lookApp.id: lookApp,
}

__all__ = [
    'hello', 'importClientMessages', 'importClientEntityDef',
    'onUpdateDataFromClient', 'onUpdateDataFromClientForControlledEntity',
    'lookApp',
    'SPEC_BY_ID'
]
