"""Parser of a message 'onImportClientMessages'."""

import dataclasses
import logging
from typing import List, Tuple, Type, Dict
from dataclasses import dataclass

from enki import kbetype, message, interface
from enki.misc import devonly

logger = logging.getLogger(__name__)


@dataclass
class _PackedData:
    """Format of packed data (base class)."""

    @classmethod
    def get_fmt(cls):
        return [(k, v) for k, v in cls.__annotations__.items()
                if isinstance(v, interface.IKBEType)]


def _parse_iterator(data_cls: Type[_PackedData], size: int, data: memoryview
                    ) -> Tuple[_PackedData, memoryview]:
    """Parse iterator encoded data."""
    elems = []
    for _ in range(size):
        kwargs = {}
        for field, field_type in data_cls.get_fmt():
            value, shift = field_type.decode(data)
            kwargs[field] = value
            data = data[shift:]
        elems.append(data_cls(**kwargs))

    return elems, data


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

    # TODO: [05.02.2021 0:07]
    # Их нужно делать публичными
    @dataclass
    class _TypeData(_PackedData):
        # TODO: [05.02.2021 0:07]
        # А их делать типами или офорлять эти датаклассы по другому.
        # Например через = описание
        id: kbetype.DATATYPE_UID
        base_type_name: kbetype.STRING
        name: kbetype.STRING

    @dataclass
    class _FixedDictData(_PackedData):
        key_count: kbetype.UINT8
        module_name: kbetype.STRING

        pairs: Dict[str, int]  # kbetype.STRING, kbetype.DATATYPE_UID

    @dataclass
    class _ArrayData(_PackedData):
        of: kbetype.UINT16

    @dataclass
    class _PropertyData(_PackedData):
        uid: kbetype.UINT16  # unique identifier of the property
        ed_flag: kbetype.UINT32  # data distribution flag of the property
        alias_id: kbetype.INT16  # predefined id (position, direction, spaceID = 1, 2, 3)
        name: kbetype.STRING  # name of the property
        default: kbetype.STRING  # default value of the property
        typesxml_id: kbetype.UINT16  # id of type from types.xml

    @dataclass
    class _MethodData(_PackedData):
        uid: kbetype.UINT16  # unique identifier of the method
        alias_id: kbetype.INT16  # ???
        name: kbetype.STRING  # name of the method
        args_count: kbetype.UINT8  # number of arguments

        arg_types: List[interface.IKBEType]  # types of arguments

    @dataclass
    class _EntityData(_PackedData):
        name: kbetype.STRING
        uid: kbetype.UINT16
        property_count: kbetype.UINT16
        client_methods_count: kbetype.UINT16
        base_methods_count: kbetype.UINT16
        cell_methods_count: kbetype.UINT16

        properties: List['_PropertyData'] = None
        client_methods: List['_MethodData'] = None
        base_methods: List['_MethodData'] = None
        cell_methods: List['_MethodData'] = None

    def _parse_fixed_dict(self, data: memoryview) -> Tuple[_FixedDictData, memoryview]:
        """Parse FIXED_DICT description."""
        logger.warning('[%s]  (%s)', self, devonly.func_args_values())
        kwargs = {}
        for field, field_type in self._FixedDictData.get_fmt():
            value, shift = field_type.decode(data)
            kwargs[field] = value
            data = data[shift:]

        kwargs['pairs'] = {}
        for _ in range(kwargs['key_count']):
            key_name, shift = kbetype.STRING.decode(data)
            data = data[shift:]
            type_id, shift = kbetype.DATATYPE_UID.decode(data)
            data = data[shift:]

            kwargs['pairs'][key_name] = type_id

        return self._FixedDictData(**kwargs), data

    def _parse_array(self, data: memoryview) -> Tuple[_ArrayData, memoryview]:
        """Parse ARRAY description."""
        logger.warning('[%s]  (%s)', self, devonly.func_args_values())
        kwargs = {}
        for field, field_type in self._ArrayData.get_fmt():
            value, shift = field_type.decode(data)
            kwargs[field] = value
            data = data[shift:]

        return self._ArrayData(**kwargs), data

    def _parse_types(self, data: memoryview
                     ) -> Tuple[List[message.deftype.DataTypeSpec], memoryview]:
        """Parse types from the file 'types.xml'."""
        types_number, shift = kbetype.UINT16.decode(data)
        data = data[shift:]

        types = []
        for _ in range(types_number):
            kwargs = {}
            for field, field_type in self._TypeData.get_fmt():
                value, shift = field_type.decode(data)
                kwargs[field] = value
                data = data[shift:]

            type_data = message.deftype.DataTypeSpec(**kwargs)

            if type_data.base_type_name == kbetype.FIXED_DICT.name:
                fd_data, data = self._parse_fixed_dict(data)
                type_data.module_name = fd_data.module_name
                type_data.pairs = fd_data.pairs
            elif type_data.base_type_name == kbetype.ARRAY.name:
                a_data, data = self._parse_array(data)
                type_data.of = a_data.of

            types.append(type_data)

        return types, data

    def _parse_properties(self, count: int, data: memoryview
                          ) -> Tuple[List[_PropertyData], memoryview]:
        """Parse properties of an entity."""
        return _parse_iterator(self._PropertyData, count, data)

    def _parse_methods(self, count: int, data: memoryview
                       ) -> Tuple[List[_MethodData], memoryview]:
        """Parse methods of an entity."""
        methods = []
        for _ in range(count):
            kwargs = {}
            for field, field_type in self._MethodData.get_fmt():
                value, shift = field_type.decode(data)
                kwargs[field] = value
                data = data[shift:]

            kwargs['arg_types'] = []
            for _ in range(kwargs['args_count']):
                type_id, shift = kbetype.DATATYPE_UID.decode(data)
                kwargs['arg_types'].append(type_id)
                data = data[shift:]

            methods.append(self._MethodData(**kwargs))

        return methods, data

    def _parse_entity(self, data: memoryview) -> List[_EntityData]:
        """Parse an entity data."""
        entities = []
        while data:
            kwargs = {}
            for field, field_type in self._EntityData.get_fmt():
                value, shift = field_type.decode(data)
                kwargs[field] = value
                data = data[shift:]

            entity_data = self._EntityData(**kwargs)

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

    def parse(self, data: memoryview) -> Tuple[List[message.deftype.DataTypeSpec],
                                               List[_EntityData]]:
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


