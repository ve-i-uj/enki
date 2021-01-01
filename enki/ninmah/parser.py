"""Parser of a message 'onImportClientMessages'."""

import logging
from typing import List

from enki import kbetype, message

logger = logging.getLogger(__name__)


class ClientMsgesParser:
    """Parser of a 'importClientMessages' message."""

    _SPEC = (
        ('id', kbetype.UINT16),          # message id
        ('msg_len', kbetype.INT16),      # length of arguments in bytes
                                         # (-1 if length is variable or no arguments)
        ('name', kbetype.STRING),        # message name
        ('args_type', kbetype.INT8),     # MsgArgsType
        ('arg_number', kbetype.UINT8),   # Number of arguments
    )

    def parse_app_msges(self, data: bytes) -> List[message.MessageSpec]:
        msg_number, shift = kbetype.UINT16.decode(data)
        data = data[shift:]
        msg_specs = []
        while data:
            msg_spec = {}
            for field, field_type in self._SPEC:
                value, shift = field_type.decode(data)
                msg_spec[field] = value
                data = data[shift:]

            arg_types = []
            arg_number = msg_spec.pop('arg_number')
            if arg_number > 0:
                for _ in range(arg_number):
                    code, shift = kbetype.UINT8.decode(data)
                    type_ = kbetype.TYPE_BY_CODE[code]
                    arg_types.append(type_)
                    data = data[shift:]
            msg_spec['arg_types'] = arg_types

            name = msg_spec['name']
            name = name.replace('_', '::', 1)
            msg_spec['name'] = name

            msg_specs.append(message.MessageSpec(
                id=msg_spec['id'],
                name=msg_spec['name'],
                args_type=message.MsgArgsType(msg_spec['args_type']),
                field_types=msg_spec['arg_types'],
                desc=''
            ))

        return msg_specs
