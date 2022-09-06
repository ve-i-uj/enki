"""Messages of BaseApp."""

from enki import kbetype, dcdescr


hello = dcdescr.MessageDescr(
    id=200,
    lenght=-1,
    name='BaseApp::hello',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.STRING,  # server version
        kbetype.STRING,  # assets version
        kbetype.BLOB,    # encrypted key
    ),
    desc='hello'
)

importClientMessages = dcdescr.MessageDescr(
    id=207,
    lenght=0,
    name='Baseapp::importClientMessages',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=tuple(),
    desc='The client requests to import the message protocol.'
)

importClientEntityDef = dcdescr.MessageDescr(
    id=208,
    lenght=0,
    name='Baseapp::importClientEntityDef',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=tuple(),
    desc='Client entitydef export.'
)

onUpdateDataFromClient = dcdescr.MessageDescr(
    id=27,
    lenght=-1,
    name='Baseapp::onUpdateDataFromClient',
    args_type=dcdescr.MsgArgsType.VARIABLE,
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

onUpdateDataFromClientForControlledEntity = dcdescr.MessageDescr(
    id=28,
    lenght=-1,
    name='Baseapp::onUpdateDataFromClientForControlledEntity',
    args_type=dcdescr.MsgArgsType.VARIABLE,
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


__all__ = [
    'hello', 'importClientMessages', 'importClientEntityDef',
    'onUpdateDataFromClient', 'onUpdateDataFromClientForControlledEntity'
]
