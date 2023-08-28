"""Messages of TCPClient component.

These messages are predefined by the plugin (not generated).
We need to know these messages to start the code generation.
"""

from enki.core import kbeenum
from enki.core import kbetype
from enki.core.message import MsgDescr

onHelloCB = MsgDescr(
    id=521,
    lenght=-1,
    name='Client::onHelloCB',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    # field_types=(kbetype.UINT8_ARRAY, ),
    field_types=(
        kbetype.STRING,
        kbetype.STRING,
        kbetype.STRING,
        kbetype.STRING,
        kbetype.INT32,
    ),
    desc=''
)

onLoginSuccessfully = MsgDescr(
    id=502,
    lenght=-1,
    name='Client::onLoginSuccessfully',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc='The client logs in to loginapp, and the server returns success.'
)

onImportClientMessages = MsgDescr(
    id=518,
    lenght=-1,
    name='Client::onImportClientMessages',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.UINT8_ARRAY,    # binary data for parsing
    ),
    desc='The protocol packet returned by the server.'
)

onImportClientEntityDef = MsgDescr(
    id=519,
    lenght=-1,
    name='Client::onImportClientEntityDef',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc='The entitydef data returned by the server.'
)

onImportServerErrorsDescr = MsgDescr(
    id=63,
    lenght=-1,
    name='Client::onImportServerErrorsDescr',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onLoginFailed = MsgDescr(
    id=503,
    lenght=-1,
    name='Client::onLoginFailed',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onVersionNotMatch = MsgDescr(
    id=523,
    lenght=-1,
    name='Client::onVersionNotMatch',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onScriptVersionNotMatch = MsgDescr(
    id=522,
    lenght=-1,
    name='Client::onScriptVersionNotMatch',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onLoginFailed = MsgDescr(
    id=503,
    lenght=-1,
    name='Client::onLoginFailed',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onVersionNotMatch = MsgDescr(
    id=523,
    lenght=-1,
    name='Client::onVersionNotMatch',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onScriptVersionNotMatch = MsgDescr(
    id=522,
    lenght=-1,
    name='Client::onScriptVersionNotMatch',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

# The generaged message has invalid parameters types.
onStreamDataStarted = MsgDescr(
    id=514,
    lenght=-1,
    name='Client::onStreamDataStarted',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT16,
        kbetype.UINT32,
        kbetype.STRING,
        kbetype.INT8,
    ),
    desc=''
)

SPEC_BY_ID = {
    onHelloCB.id: onHelloCB,
    onLoginSuccessfully.id: onLoginSuccessfully,
    onImportClientMessages.id: onImportClientMessages,
    onImportClientEntityDef.id: onImportClientEntityDef,
    onImportServerErrorsDescr.id: onImportServerErrorsDescr,
    onLoginFailed.id: onLoginFailed,
    onVersionNotMatch.id: onVersionNotMatch,
    onScriptVersionNotMatch.id: onScriptVersionNotMatch,
    onStreamDataStarted.id: onStreamDataStarted,
}

__all__ = [
    "SPEC_BY_ID",
    "onHelloCB",
    "onLoginSuccessfully",
    "onImportClientMessages",
    "onImportClientEntityDef",
    "onImportServerErrorsDescr",
    "onLoginFailed",
    "onVersionNotMatch",
    "onScriptVersionNotMatch",
    "onStreamDataStarted",
]
