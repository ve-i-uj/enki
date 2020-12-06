"""Messages of Client component."""

from enki import kbetype
from enki import message

onHelloCB = message.MessageSpec(
    id=521,
    name='Client::onHelloCB',
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
    field_types=(
        kbetype.STRING,
        kbetype.STRING,
        kbetype.UINT16,
        kbetype.UINT16,
        kbetype.BLOB,
    ),
    desc='The client logs in to loginapp, and the server returns success.'
)

SPEC_BY_ID = {
    onHelloCB.id: onHelloCB,
    onLoginSuccessfully.id: onLoginSuccessfully,
}
