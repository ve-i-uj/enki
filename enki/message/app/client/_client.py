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

onUpdatePropertys = message.MessageSpec(
    id=511,
    name='Client::onUpdatePropertys',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.ENTITY_ID,
    ),
    desc=''
)

onLoginFailed = message.MessageSpec(
    id=503,
    name='Client::onLoginFailed',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.SERVER_ERROR,  # see kbeenum.ServerError
        kbetype.BLOB,  # data from the second argument of "login" message
    ),
    desc=''
)

onVersionNotMatch = message.MessageSpec(
    id=523,
    name='Client::onVersionNotMatch',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.STRING,      # actual KBEngine version
    ),
    desc=''
)

onScriptVersionNotMatch = message.MessageSpec(
    id=522,
    name='Client::onScriptVersionNotMatch',
    args_type=message.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.STRING,
    ),
    desc=''
)


SPEC_BY_ID = {
    onHelloCB.id: onHelloCB,
    onLoginSuccessfully.id: onLoginSuccessfully,
    onImportClientMessages.id: onImportClientMessages,
    onImportClientEntityDef.id: onImportClientEntityDef,
    onImportServerErrorsDescr.id: onImportServerErrorsDescr,
    onUpdatePropertys.id: onUpdatePropertys,
    onLoginFailed.id: onLoginFailed,
    onVersionNotMatch.id: onVersionNotMatch,
    onScriptVersionNotMatch.id: onScriptVersionNotMatch,
}


__all__ = (
    'onHelloCB', 'onLoginSuccessfully', 'onImportClientMessages',
    'onImportClientEntityDef', 'onImportServerErrorsDescr', 'onUpdatePropertys',
    'onLoginFailed', 'onVersionNotMatch', 'onScriptVersionNotMatch',
    'SPEC_BY_ID'
)
