"""Messages of Client component.

These messages are predefined by the plugin (not generated).
We need to know the messages to start the code generation.
"""

from enki import kbetype, dcdescr

onHelloCB = dcdescr.MessageDescr(
    id=521,
    name='Client::onHelloCB',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.STRING,
        kbetype.STRING,
        kbetype.STRING,
        kbetype.STRING,
        kbetype.INT16,
    ),
    desc='hello response'
)

onLoginSuccessfully = dcdescr.MessageDescr(
    id=502,
    name='Client::onLoginSuccessfully',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.STRING,  # accountName
        kbetype.STRING,  # host
        kbetype.UINT16,  # tcp port
        kbetype.UINT16,  # udp port
        kbetype.BLOB,    # server data
    ),
    desc='The client logs in to loginapp, and the server returns success.'
)

onImportClientMessages = dcdescr.MessageDescr(
    id=518,
    name='Client::onImportClientMessages',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.UINT8_ARRAY,    # binary data for parsing
    ),
    desc='The protocol packet returned by the server.'
)

onImportClientEntityDef = dcdescr.MessageDescr(
    id=519,
    name='Client::onImportClientEntityDef',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.UINT8_ARRAY,
    ),
    desc='The entitydef data returned by the server.'
)

onImportServerErrorsDescr = dcdescr.MessageDescr(
    id=63,
    name='Client::onImportServerErrorsDescr',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.UINT8_ARRAY,
    ),
    desc=''
)

onUpdatePropertys = dcdescr.MessageDescr(
    id=511,
    name='Client::onUpdatePropertys',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.ENTITY_ID,
        kbetype.UINT8_ARRAY
    ),
    desc=''
)

onLoginFailed = dcdescr.MessageDescr(
    id=503,
    name='Client::onLoginFailed',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.SERVER_ERROR,   # see kbeenum.ServerError
        kbetype.BLOB,           # sent data or modified by scripts "onRequestLogin"
    ),
    desc=''
)

onVersionNotMatch = dcdescr.MessageDescr(
    id=523,
    name='Client::onVersionNotMatch',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.STRING,      # actual KBEngine version
    ),
    desc=''
)

onScriptVersionNotMatch = dcdescr.MessageDescr(
    id=522,
    name='Client::onScriptVersionNotMatch',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.STRING,
    ),
    desc=''
)

onLoginFailed = dcdescr.MessageDescr(
    id=503,
    name='Client::onLoginFailed',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.SERVER_ERROR,   # see kbeenum.ServerError
        kbetype.BLOB,           # sent data or modified by scripts "onRequestLogin"
    ),
    desc=''
)

onVersionNotMatch = dcdescr.MessageDescr(
    id=523,
    name='Client::onVersionNotMatch',
    args_type=dcdescr.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.STRING,      # actual KBEngine version
    ),
    desc=''
)

onScriptVersionNotMatch = dcdescr.MessageDescr(
    id=522,
    name='Client::onScriptVersionNotMatch',
    args_type=dcdescr.MsgArgsType.VARIABLE,
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
