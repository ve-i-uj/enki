"""Parser of a message 'onImportClientMessages'."""

import logging
from typing import List, Tuple, Any

from enki import kbetype, message, deftype, servererror
from enki import spec
from enki.misc import devonly

logger = logging.getLogger(__name__)


class ClientMsgesParser:
    """Parser of a 'onImportClientMessages' message."""

    _SPEC = (
        ('id', kbetype.UINT16),  # message id
        ('msg_len', kbetype.INT16),  # length of arguments in bytes
        # (-1 if length is variable or no arguments)
        ('name', kbetype.STRING),  # message name
        ('args_type', kbetype.INT8),  # MsgArgsType
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


class EntityDefParser:
    """Parser of a 'onImportClientEntityDef' message."""

    _TYPES_SPEC = (
        ('id', kbetype.DATATYPE_UID),
        ('base_type_name', kbetype.STRING),
        ('name', kbetype.STRING),
    )

    def _parse_fixed_dict(self, data: bytes) -> Tuple[int, Any]:
        """Parse FIXED_DICT description."""
        logger.warning('[%s]  (%s)', self, devonly.func_args_values())

    def _parse_array(self, data: bytes) -> Tuple[int, Any]:
        """Parse ARRAY description."""
        logger.warning('[%s]  (%s)', self, devonly.func_args_values())

    def _parse_types(self, data) -> List[deftype.DataTypeSpec]:
        """Parse types from the file 'types.xml'."""
        types_number, shift = kbetype.UINT16.decode(data)
        data = data[shift:]

        types = []
        for _ in range(types_number):
            type_spec = {}
            for field, field_type in self._TYPES_SPEC:
                value, shift = field_type.decode(data)
                type_spec[field] = value
                data = data[shift:]

            if type_spec['base_type_name'] == kbetype.FIXED_DICT.name:
                self._parse_fixed_dict(data)
            elif type_spec['base_type_name'] == kbetype.ARRAY.name:
                self._parse_array(data)

            types.append(message.DataTypeSpec(**type_spec))

        return types

    def parse_entity_defs(self, data: bytes):
        """Parse communication protocol of entities."""
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
        types = self._parse_types(data)
        print()

    def __str__(self):
        return str(self.__class__.__name__)


class ServerErrorParser:
    """Parser of a 'Loginapp::importServerErrorsDescr' message."""

    _SPEC = (
        ('id', kbetype.INT16),
        ('name', kbetype.BLOB),
        ('desc', kbetype.BLOB),
    )

    def parse(self, data: bytes) -> List[servererror.ServerErrorSpec]:
        """Parse server errors."""
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
        size, shift = kbetype.UINT16.decode(data)
        data = data[shift:]
        specs = []
        for _ in range(size):
            error_spec = {}
            for field, field_type in self._SPEC:
                value, shift = field_type.decode(data)
                error_spec[field] = value
                data = data[shift:]
            specs.append(servererror.ServerErrorSpec(
                id=error_spec['id'],
                name=error_spec['name'].decode(),
                desc=error_spec['desc'].decode(),
            ))

        return specs

    def __str__(self):
        return str(self.__class__.__name__)


