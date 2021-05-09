"""Messages of Client component."""

from enki import kbetype
from .. import _message

onHelloCB = _message.MessageSpec(
    id=521,
    name='Client::onHelloCB',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.STRING,
        kbetype.STRING,
        kbetype.STRING,
        kbetype.STRING,
        kbetype.INT16,
    ),
    desc='hello response'
)

onLoginSuccessfully = _message.MessageSpec(
    id=502,
    name='Client::onLoginSuccessfully',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.STRING,  # accountName
        kbetype.STRING,  # host
        kbetype.UINT16,  # tcp port
        kbetype.UINT16,  # udp port
        kbetype.BLOB,    # server data
    ),
    desc='The client logs in to loginapp, and the server returns success.'
)

onImportClientMessages = _message.MessageSpec(
    id=518,
    name='Client::onImportClientMessages',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.UINT8_ARRAY,    # binary data for parsing
    ),
    desc='The protocol packet returned by the server.'
)

onImportClientEntityDef = _message.MessageSpec(
    id=519,
    name='Client::onImportClientEntityDef',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.UINT8_ARRAY,
    ),
    desc='The entitydef data returned by the server.'
)

onImportServerErrorsDescr = _message.MessageSpec(
    id=63,
    name='Client::onImportServerErrorsDescr',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.UINT8_ARRAY,
    ),
    desc=''
)

onUpdatePropertys = _message.MessageSpec(
    id=511,
    name='Client::onUpdatePropertys',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.ENTITY_ID,
        kbetype.UINT8_ARRAY
    ),
    desc=''
)

onLoginFailed = _message.MessageSpec(
    id=503,
    name='Client::onLoginFailed',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.SERVER_ERROR,   # see kbeenum.ServerError
        kbetype.BLOB,           # sent data or modified by scripts "onRequestLogin"
    ),
    desc=''
)

onVersionNotMatch = _message.MessageSpec(
    id=523,
    name='Client::onVersionNotMatch',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.STRING,      # actual KBEngine version
    ),
    desc=''
)

onScriptVersionNotMatch = _message.MessageSpec(
    id=522,
    name='Client::onScriptVersionNotMatch',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.STRING,
    ),
    desc=''
)

onLoginFailed = _message.MessageSpec(
    id=503,
    name='Client::onLoginFailed',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.SERVER_ERROR,   # see kbeenum.ServerError
        kbetype.BLOB,           # sent data or modified by scripts "onRequestLogin"
    ),
    desc=''
)

onVersionNotMatch = _message.MessageSpec(
    id=523,
    name='Client::onVersionNotMatch',
    args_type=_message.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.STRING,      # actual KBEngine version
    ),
    desc=''
)

onScriptVersionNotMatch = _message.MessageSpec(
    id=522,
    name='Client::onScriptVersionNotMatch',
    args_type=_message.MsgArgsType.VARIABLE,
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
