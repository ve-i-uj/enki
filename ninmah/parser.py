"""Parser of a message 'onImportClientMessages'."""

import collections
import dataclasses
import logging
from typing import List, Tuple, Type, Dict, Optional
from dataclasses import dataclass

from enki import kbetype, message, interface
from enki.misc import devonly

logger = logging.getLogger(__name__)


@dataclass
class ParsedPropertyData:
    uid: int  # unique identifier of the property
    ed_flag: int  # data distribution flag of the property
    alias_id: int  # predefined id (position, direction, spaceID = 1, 2, 3)
    name: str  # name of the property
    default: str  # default value of the property
    typesxml_id: int  # id of type from types.xml


@dataclass
class ParsedMethodData:
    uid: int  # unique identifier of the method
    alias_id: int  # ???
    name: str  # name of the method
    args_count: str  # number of arguments
    arg_types: List[int]  # types of arguments


@dataclass
class ParsedEntityData:
    name: str
    uid: int
    property_count: int
    client_methods_count: int
    base_methods_count: int
    cell_methods_count: int

    properties: List[ParsedPropertyData] = None
    client_methods: List[ParsedMethodData] = None
    base_methods: List[ParsedMethodData] = None
    cell_methods: List[ParsedMethodData] = None


@dataclass
class ParsedTypeData:
    id: int
    base_type_name: str
    name: str

    # FIXED_DICT data
    module_name: Optional[str] = None
    fd_type_id_by_key: Optional[Dict[str, int]] = None

    # ARRAY data
    arr_of_id: Optional[int] = None

    @property
    def is_alias(self) -> bool:
        return self.name != self.base_type_name

    @property
    def is_fixed_dict(self) -> bool:
        return self.fd_type_id_by_key is not None

    @property
    def is_array(self) -> bool:
        return self.arr_of_id is not None

    @property
    def type_name(self) -> str:
        if not self.name or self.name.startswith('_'):
            # It's an inner defined type
            return f'{self.base_type_name}_{self.id}'
        return self.name


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

    def parse_app_msges(self, data: memoryview) -> List[message.MessageSpec]:
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

    def _parse_fixed_dict(self, data: memoryview
                          ) -> Tuple[str, Dict[str, int], memoryview]:
        """Parse FIXED_DICT description."""
        key_count, shift = kbetype.UINT8.decode(data)
        data = data[shift:]
        module_name, shift = kbetype.STRING.decode(data)
        data = data[shift:]

        pairs = {}
        for _ in range(key_count):
            key_name, shift = kbetype.STRING.decode(data)
            data = data[shift:]
            type_id, shift = kbetype.DATATYPE_UID.decode(data)
            data = data[shift:]

            pairs[key_name] = type_id

        return module_name, pairs, data

    def _parse_types(self, data: memoryview
                     ) -> Tuple[List[ParsedTypeData], memoryview]:
        """Parse types from the file 'types.xml'."""
        types_number, shift = kbetype.UINT16.decode(data)
        data = data[shift:]

        types = []
        for _ in range(types_number):
            kwargs = {}
            kwargs['id'], shift = kbetype.DATATYPE_UID.decode(data)
            data = data[shift:]
            kwargs['base_type_name'], shift = kbetype.STRING.decode(data)
            data = data[shift:]
            kwargs['name'], shift = kbetype.STRING.decode(data)
            data = data[shift:]

            if kwargs['base_type_name'] == kbetype.FIXED_DICT.name:
                module_name, pairs, data = self._parse_fixed_dict(data)
                kwargs['module_name'] = module_name
                kwargs['fd_type_id_by_key'] = pairs
            elif kwargs['base_type_name'] == kbetype.ARRAY.name:
                array_type, shift = kbetype.UINT16.decode(data)
                data = data[shift:]
                kwargs['arr_of_id'] = array_type

            types.append(ParsedTypeData(**kwargs))

        return types, data

    def _parse_properties(self, count: int, data: memoryview
                          ) -> Tuple[List[ParsedPropertyData], memoryview]:
        """Parse properties of an entity."""
        spec = collections.OrderedDict(
            uid=kbetype.UINT16,  # unique identifier of the property
            ed_flag=kbetype.UINT32,  # data distribution flag of the property
            alias_id=kbetype.INT16,  # predefined id (position, direction, spaceID = 1, 2, 3)
            name=kbetype.STRING,  # name of the property
            default=kbetype.STRING,  # default value of the property
            typesxml_id=kbetype.UINT16,  # id of type from types.xml
        )
        properties = []
        for _ in range(count):
            kwargs = {}
            for field, field_type in spec.items():
                value, shift = field_type.decode(data)
                kwargs[field] = value
                data = data[shift:]
            properties.append(ParsedPropertyData(**kwargs))

        return properties, data

    def _parse_methods(self, count: int, data: memoryview
                       ) -> Tuple[List[ParsedMethodData], memoryview]:
        """Parse methods of an entity."""
        methods = []
        for _ in range(count):
            kwargs = {}
            kwargs['uid'], shift = kbetype.UINT16.decode(data)
            data = data[shift:]
            kwargs['alias_id'], shift = kbetype.INT16.decode(data)
            data = data[shift:]
            kwargs['name'], shift = kbetype.STRING.decode(data)
            data = data[shift:]
            kwargs['args_count'], shift = kbetype.UINT8.decode(data)
            data = data[shift:]

            kwargs['arg_types'] = []
            for _ in range(kwargs['args_count']):
                type_id, shift = kbetype.DATATYPE_UID.decode(data)
                kwargs['arg_types'].append(type_id)
                data = data[shift:]

            methods.append(ParsedMethodData(**kwargs))

        return methods, data

    def _parse_entity(self, data: memoryview) -> List[ParsedEntityData]:
        """Parse entity data."""
        entity_spec = collections.OrderedDict(
            name=kbetype.STRING,
            uid=kbetype.UINT16,
            property_count=kbetype.UINT16,
            client_methods_count=kbetype.UINT16,
            base_methods_count=kbetype.UINT16,
            cell_methods_count=kbetype.UINT16,
        )
        entities = []
        while data:
            kwargs = {}
            for field, field_type in entity_spec.items():
                value, shift = field_type.decode(data)
                kwargs[field] = value
                data = data[shift:]

            entity_data = ParsedEntityData(**kwargs)

            properties, data = self._parse_properties(entity_data.property_count,
                                                      data)
            client_methods, data = self._parse_methods(
                entity_data.client_methods_count,
                data
            )
            base_methods, data = self._parse_methods(
                entity_data.base_methods_count,
                data
            )
            cell_methods, data = self._parse_methods(
                entity_data.cell_methods_count,
                data
            )

            entity_data.properties = properties
            entity_data.client_methods = client_methods
            entity_data.base_methods = base_methods
            entity_data.cell_methods = cell_methods

            entities.append(entity_data)

        return entities

    def parse(self, data: memoryview) -> Tuple[List[ParsedTypeData],
                                               List[ParsedEntityData]]:
        """Parse communication protocol of entities."""
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
        types, data = self._parse_types(data)
        entities = self._parse_entity(data)

        return types, entities

    def __str__(self):
        return str(self.__class__.__name__)


class ServerErrorParser:
    """Parser of a 'Loginapp::importServerErrorsDescr' message."""

    _SPEC = (
        ('id', kbetype.INT16),
        ('name', kbetype.BLOB),
        ('desc', kbetype.BLOB),
    )

    def parse(self, data: memoryview) -> List[message.servererror.ServerErrorSpec]:
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
            specs.append(message.servererror.ServerErrorSpec(
                id=error_spec['id'],
                name=error_spec['name'].decode(),
                desc=error_spec['desc'].decode(),
            ))

        return specs

    def __str__(self):
        return str(self.__class__.__name__)

