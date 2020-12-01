"""Messages of LoginApp"""

from enki import message
from enki import kbetype

hello = message.MessageSpec(
    id=4,
    name='Loginapp::hello',
    field_types=(
        kbetype.STRING,
        kbetype.STRING,
        kbetype.BLOB,
    ),
    desc='hello'
)
