"""Обработчик сообщений для компонента Client."""

from __future__ import annotations

import logging
from collections import OrderedDict
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from enki import msgspec
from enki.kbeenum import DistributionFlag
from enki.kbetype.decoders.basic_data_type_decoders import (
    INT16,
    STRING,
    UINT8,
    UINT16,
    UINT32,
)
from enki.kbetype.decoders.custom_decoders import DATATYPE_UID
from enki.misc import devonly
from enki.msg_parser.imsg_parser import IMsgParser, MsgParserResult, ParsedMsgData

if TYPE_CHECKING:
    from collections.abc import Sequence

    from enki.msg.message import Message

logger = logging.getLogger(__name__)


@dataclass
class ParsedPropertyInfo:
    """Данные свойств сущностей из сообщения Client::onImportClientEntityDef."""

    uid: int  # unique identifier of the property
    ed_flag: int  # data distribution flag of the property
    alias_id: int  # predefined id (position, direction, spaceID = 1, 2, 3)
    name: str  # name of the property
    default: str  # default value of the property
    typesxml_id: int  # id of type from types.xml

    @property
    def need_set_method(self) -> bool:
        """Флаг того, нужно ли этому свойству создавать 'set_*' метод."""
        return (
            DistributionFlag(self.ed_flag)
            in DistributionFlag.get_set_method_flags()
        )


@dataclass
class ParsedMethodInfo:
    """Данные методов сущностей из сообщения Client::onImportClientEntityDef."""

    uid: int  # unique identifier of the method
    alias_id: int  # ???
    name: str  # name of the method
    args_count: int  # number of arguments
    arg_types: Sequence[int]  # types of arguments


@dataclass
class ParsedEntityInfo:
    """Данные сущности из сообщения Client::onImportClientEntityDef."""

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
    """Данные типа из сообщения Client::onImportClientEntityDef."""

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
        """Это алиас на простой тип."""
        return self.name != self.base_type_name

    @property
    def is_fixed_dict(self) -> bool:
        """Флаг того, что это тип FIXED_DICT."""
        return self.fd_type_id_by_key is not None

    @property
    def is_array(self) -> bool:
        """Флаг того, что это тип ARRAY."""
        return self.arr_of_id is not None

    @property
    def type_name(self) -> str:
        """Имя типа."""
        if not self.name or self.name.startswith("_"):
            # It's an inner defined type
            return f"{self.base_type_name}_{self.id}"
        return self.name


@dataclass
class OnImportClientEntityDefParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Client::onImportClientEntityDef."""

    types: list[ParsedTypeInfo]
    entities: list[ParsedEntityInfo]


@dataclass(frozen=True)
class OnImportClientEntityDefMsgParserResult(MsgParserResult):
    """Парсер для Client::onImportClientEntityDef."""

    success: bool
    result: OnImportClientEntityDefParsedMsgData | None = None
    msg_id: int = msgspec.client.onImportClientEntityDef.id
    text: str = ""


class OnImportClientEntityDefMsgParser(IMsgParser):
    """Парсер для Client::onImportClientEntityDef."""

    def parse(self, msg: Message) -> OnImportClientEntityDefMsgParserResult:
        """Распарсить сообщение Client::onImportClientEntityDef.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnImportClientEntityDefParserMsgParserResult: объект
                результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])

        types, data = self._parse_types(data)
        entities = self._parse_entity(data)

        return OnImportClientEntityDefMsgParserResult(
            success=True,
            result=OnImportClientEntityDefParsedMsgData(
                types=types, entities=entities
            ),
        )

    def _parse_fixed_dict(
        self, data: memoryview
    ) -> tuple[str, OrderedDict, memoryview]:
        """Parse FIXED_DICT description."""
        key_count, shift = UINT8.decode(data)
        data = data[shift:]
        module_name, shift = STRING.decode(data)
        data = data[shift:]

        pairs = OrderedDict()
        for _ in range(key_count):
            key_name, shift = STRING.decode(data)
            data = data[shift:]
            type_id, shift = DATATYPE_UID.decode(data)
            data = data[shift:]

            pairs[key_name] = type_id

        return module_name, pairs, data

    def _parse_types(
        self, data: memoryview
    ) -> tuple[list[ParsedTypeInfo], memoryview]:
        """Parse types from the file 'types.xml'."""
        types_number, shift = UINT16.decode(data)
        data = data[shift:]

        types = []
        for _ in range(types_number):
            type_id, shift = DATATYPE_UID.decode(data)
            data = data[shift:]
            base_type_name, shift = STRING.decode(data)
            data = data[shift:]
            name, shift = STRING.decode(data)
            data = data[shift:]

            module_name = None
            fd_type_id_by_key = None

            arr_of_id = None

            if base_type_name == "FIXED_DICT":
                mod_name, pairs, data = self._parse_fixed_dict(data)
                module_name = mod_name
                fd_type_id_by_key = pairs
            elif base_type_name == "ARRAY":
                array_type_id, shift = UINT16.decode(data)
                data = data[shift:]
                arr_of_id = array_type_id

            types.append(
                ParsedTypeInfo(
                    id=type_id,
                    base_type_name=base_type_name,
                    name=name,
                    module_name=module_name,
                    fd_type_id_by_key=fd_type_id_by_key,
                    arr_of_id=arr_of_id,
                )
            )

        return types, data

    def _parse_properties(
        self, count: int, data: memoryview
    ) -> tuple[list[ParsedPropertyInfo], memoryview]:
        """Parse properties of an entity."""
        properties = []
        for _ in range(count):
            # unique identifier of the property
            uid, offset = UINT16.decode(data)
            data = data[offset:]

            # data distribution flag of the property
            ed_flag, offset = UINT32.decode(data)
            data = data[offset:]

            # predefined id (position, direction, spaceID = 1, 2, 3)
            alias_id, offset = INT16.decode(data)
            data = data[offset:]

            # name of the property
            name, offset = STRING.decode(data)
            data = data[offset:]

            # default value of the property
            default, offset = STRING.decode(data)
            data = data[offset:]

            # id of type from types.xml
            typesxml_id, offset = UINT16.decode(data)
            data = data[offset:]

            properties.append(
                ParsedPropertyInfo(
                    uid=uid,
                    ed_flag=ed_flag,
                    alias_id=alias_id,
                    name=name,
                    default=default,
                    typesxml_id=typesxml_id,
                )
            )

        return properties, data

    def _parse_methods(
        self, count: int, data: memoryview
    ) -> tuple[list[ParsedMethodInfo], memoryview]:
        """Parse methods of an entity."""
        methods = []
        for _ in range(count):
            uid, shift = UINT16.decode(data)
            data = data[shift:]

            alias_id, shift = INT16.decode(data)
            data = data[shift:]

            name, shift = STRING.decode(data)
            data = data[shift:]

            args_count, shift = UINT8.decode(data)
            data = data[shift:]

            arg_types = []
            for _ in range(args_count):
                type_id, shift = DATATYPE_UID.decode(data)
                arg_types.append(type_id)
                data = data[shift:]

            methods.append(
                ParsedMethodInfo(
                    uid=uid,
                    alias_id=alias_id,
                    name=name,
                    args_count=args_count,
                    arg_types=arg_types,
                )
            )

        return methods, data

    def _parse_entity(self, data: memoryview) -> list[ParsedEntityInfo]:
        """Parse entity data."""
        entities = []
        while data:
            name, offset = STRING.decode(data)
            data = data[offset:]

            uid, offset = UINT16.decode(data)
            data = data[offset:]

            property_count, offset = UINT16.decode(data)
            data = data[offset:]

            client_methods_count, offset = UINT16.decode(data)
            data = data[offset:]

            base_methods_count, offset = UINT16.decode(data)
            data = data[offset:]

            cell_methods_count, offset = UINT16.decode(data)
            data = data[offset:]

            entity_data = ParsedEntityInfo(
                name=name,
                uid=uid,
                property_count=property_count,
                client_methods_count=client_methods_count,
                base_methods_count=base_methods_count,
                cell_methods_count=cell_methods_count,
            )

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
