"""Messages of Client component."""

from enki import message
from enki import kbetype

onHelloCB = message.MessageSpec(
    id=521,
    name='Client::onHelloCB',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.STRING,
        kbetype.STRING,
        kbetype.STRING,
        kbetype.STRING,
        kbetype.INT16,
    ),
    desc='hello response'
)

onLoginSuccessfully = message.MessageSpec(
    id=502,
    name='Client::onLoginSuccessfully',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.STRING,  # accountName
        kbetype.STRING,  # host
        kbetype.UINT16,  # tcp port
        kbetype.UINT16,  # udp port
        kbetype.BLOB,    # server data
    ),
    desc='The client logs in to loginapp, and the server returns success.'
)

onImportClientMessages = message.MessageSpec(
    id=518,
    name='Client::onImportClientMessages',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.UINT8_ARRAY,
    ),
    desc='The protocol packet returned by the server.'
)

onImportClientEntityDef = message.MessageSpec(
    id=519,
    name='Client::onImportClientEntityDef',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.UINT8_ARRAY,
    ),
    desc='The entitydef data returned by the server.'
)

onImportServerErrorsDescr = message.MessageSpec(
    id=63,
    name='Client::onImportServerErrorsDescr',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.UINT8_ARRAY,
    ),
    desc=''
)

SPEC_BY_ID = {
    onHelloCB.id: onHelloCB,
    onLoginSuccessfully.id: onLoginSuccessfully,
    onImportClientMessages.id: onImportClientMessages,
    onImportClientEntityDef.id: onImportClientEntityDef,
    onImportServerErrorsDescr.id: onImportServerErrorsDescr
}
