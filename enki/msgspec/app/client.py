"""Messages of Client component."""

from enki import message
from enki import kbetype

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

MSG_MAP = {
    521: onHelloCB
}