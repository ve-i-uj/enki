"""Парсеры данных KBEngine."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from enki.kbeenum import DistributionFlag
from enki.kbetype.decoders.basic_data_type_decoders import BLOB, INT16, INT8, STRING, UINT16, UINT8


if TYPE_CHECKING:
    from collections import OrderedDict

logger = logging.getLogger(__name__)



@dataclass
class ParsedServerErrorInfo:
    id: int
    name: str
    desc: str


@dataclass
class ParsedPropertyInfo:
    uid: int  # unique identifier of the property
    ed_flag: int  # data distribution flag of the property
    alias_id: int  # predefined id (position, direction, spaceID = 1, 2, 3)
    name: str  # name of the property
    default: str  # default value of the property
    typesxml_id: int  # id of type from types.xml

    @property
    def need_set_method(self) -> bool:
        need_set = (
            DistributionFlag(self.ed_flag)
            in DistributionFlag.get_set_method_flags()
        )
        return need_set


@dataclass
class ParsedMethodInfo:
    uid: int  # unique identifier of the method
    alias_id: int  # ???
    name: str  # name of the method
    args_count: str  # number of arguments
    arg_types: list[int]  # types of arguments


@dataclass
class ParsedEntityInfo:
    name: str
    uid: int
    property_count: int
    client_methods_count: int
    base_methods_count: int
    cell_methods_count: int

    properties: list[ParsedPropertyInfo] | None = None
    client_methods: list[ParsedMethodInfo] | None = None
    base_methods: list[ParsedMethodInfo] | None = None
    cell_methods: list[ParsedMethodInfo] | None = None


@dataclass
class ParsedTypeInfo:
    id: int
    base_type_name: str
    name: str

    # FIXED_DICT data
    module_name: str | None = None
    fd_type_id_by_key: OrderedDict[str, int] | None = None

    # ARRAY data
    arr_of_id: int | None = None

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
        if not self.name or self.name.startswith("_"):
            # It's an inner defined type
            return f"{self.base_type_name}_{self.id}"
        return self.name


class EntityDefParser:
    """Parser of a 'onImportClientEntityDef' message."""

    def _parse_fixed_dict(
        self, data: memoryview
    ) -> Tuple[str, collections.OrderedDict, memoryview]:
        """Parse FIXED_DICT description."""
        key_count, shift = UINT8.decode(data)
        data = data[shift:]
        module_name, shift = STRING.decode(data)
        data = data[shift:]

        pairs = collections.OrderedDict()
        for _ in range(key_count):
            key_name, shift = STRING.decode(data)
            data = data[shift:]
            type_id, shift = DATATYPE_UID.decode(data)
            data = data[shift:]

            pairs[key_name] = type_id

        return module_name, pairs, data

    def _parse_types(
        self, data: memoryview
    ) -> Tuple[list[ParsedTypeInfo], memoryview]:
        """Parse types from the file 'types.xml'."""
        types_number, shift = UINT16.decode(data)
        data = data[shift:]

        types = []
        for _ in range(types_number):
            kwargs = {}
            kwargs["id"], shift = DATATYPE_UID.decode(data)
            data = data[shift:]
            kwargs["base_type_name"], shift = STRING.decode(data)
            data = data[shift:]
            kwargs["name"], shift = STRING.decode(data)
            data = data[shift:]

            if kwargs["base_type_name"] == FIXED_DICT.name:
                module_name, pairs, data = self._parse_fixed_dict(data)
                kwargs["module_name"] = module_name
                kwargs["fd_type_id_by_key"] = pairs
            elif kwargs["base_type_name"] == ARRAY.name:
                array_type, shift = UINT16.decode(data)
                data = data[shift:]
                kwargs["arr_of_id"] = array_type

            types.append(ParsedTypeInfo(**kwargs))

        return types, data

    def _parse_properties(
        self, count: int, data: memoryview
    ) -> Tuple[list[ParsedPropertyInfo], memoryview]:
        """Parse properties of an entity."""
        spec = collections.OrderedDict(
            uid=UINT16,  # unique identifier of the property
            ed_flag=UINT32,  # data distribution flag of the property
            alias_id=INT16,  # predefined id (position, direction, spaceID = 1, 2, 3)
            name=STRING,  # name of the property
            default=STRING,  # default value of the property
            typesxml_id=UINT16,  # id of type from types.xml
        )
        properties = []
        for _ in range(count):
            kwargs = {}
            for field, field_type in spec.items():
                value, shift = field_type.decode(data)
                kwargs[field] = value
                data = data[shift:]
            properties.append(ParsedPropertyInfo(**kwargs))

        return properties, data

    def _parse_methods(
        self, count: int, data: memoryview
    ) -> Tuple[list[ParsedMethodInfo], memoryview]:
        """Parse methods of an entity."""
        methods = []
        for _ in range(count):
            kwargs = {}
            kwargs["uid"], shift = UINT16.decode(data)
            data = data[shift:]
            kwargs["alias_id"], shift = INT16.decode(data)
            data = data[shift:]
            kwargs["name"], shift = STRING.decode(data)
            data = data[shift:]
            kwargs["args_count"], shift = UINT8.decode(data)
            data = data[shift:]

            kwargs["arg_types"] = []
            for _ in range(kwargs["args_count"]):
                type_id, shift = DATATYPE_UID.decode(data)
                kwargs["arg_types"].append(type_id)
                data = data[shift:]

            methods.append(ParsedMethodInfo(**kwargs))

        return methods, data

    def _parse_entity(self, data: memoryview) -> list[ParsedEntityInfo]:
        """Parse entity data."""
        entity_spec = collections.OrderedDict(
            name=STRING,
            uid=UINT16,
            property_count=UINT16,
            client_methods_count=UINT16,
            base_methods_count=UINT16,
            cell_methods_count=UINT16,
        )
        entities = []
        while data:
            kwargs = {}
            for field, field_type in entity_spec.items():
                value, shift = field_type.decode(data)
                kwargs[field] = value
                data = data[shift:]

            entity_data = ParsedEntityInfo(**kwargs)

            properties, data = self._parse_properties(
                entity_data.property_count, data
            )
            client_methods, data = self._parse_methods(
                entity_data.client_methods_count, data
            )
            base_methods, data = self._parse_methods(
                entity_data.base_methods_count, data
            )
            cell_methods, data = self._parse_methods(
                entity_data.cell_methods_count, data
            )

            entity_data.properties = properties
            entity_data.client_methods = client_methods
            entity_data.base_methods = base_methods
            entity_data.cell_methods = cell_methods

            entities.append(entity_data)

        return entities

    def parse(
        self, data: memoryview
    ) -> Tuple[list[ParsedTypeInfo], list[ParsedEntityInfo]]:
        """Parse communication protocol of entities."""
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())
        types, data = self._parse_types(data)
        entities = self._parse_entity(data)

        return types, entities

    def __str__(self):
        return str(self.__class__.__name__)


class ServerErrorParser:
    """Parser of a 'Loginapp::importServerErrorsDescr' message."""

    _SPEC = (
        ("id", INT16),
        ("name", BLOB),
        ("desc", BLOB),
    )

    def parse(self, data: memoryview) -> list[ParsedServerErrorInfo]:
        """Parse server errors."""
        logger.debug("[%s]  (%s)", self, devonly.func_args_values())
        size, shift = UINT16.decode(data)
        data = data[shift:]
        specs = []
        for _ in range(size):
            error_spec = {}
            for field, field_type in self._SPEC:
                value, shift = field_type.decode(data)
                error_spec[field] = value
                data = data[shift:]
            specs.append(
                ParsedServerErrorInfo(
                    id=error_spec["id"],
                    name=error_spec["name"].decode(),
                    desc=error_spec["desc"].decode(),
                )
            )

        return specs

    def __str__(self):
        return str(self.__class__.__name__)
