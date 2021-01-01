"""Code generators of KBE messages."""

import pathlib
from typing import List

from enki import message

_HEADER_TEMPLATE = '''"""Messages of {name}."""

from enki import message
from enki import kbetype
'''


class MessagesCodeGen:
    """Code generator of KBE messages.

    ``dst_path`` - file to write messages in,
    """

    def __init__(self, dst_path: pathlib.Path):
        self._dst_path = dst_path

    @property
    def dst_path(self):
        return self._dst_path

    def write(self, msg_specs: List[message.MessageSpec]):
        """Write messages to the file."""
        name = self._dst_path.name.split('.')[0].capitalize()
        self._dst_path.parent.mkdir(parents=True, exist_ok=True)
        with self._dst_path.open('w') as fh:
            fh.write(_HEADER_TEMPLATE.format(name=name))
            for msg in msg_specs:
                fh.write(msg.to_string())
