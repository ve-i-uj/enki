"""The module contains the parser for file `types.xml`"""

import collections
import dataclasses
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Generator, Optional, Type, Union, Dict, Any, List

from enki.misc import devonly
from enki.core.kbetype import Vector2, Vector3, Vector4, FixedDict, Array
from enki.core._upf import EntityCall

from lxml import etree

logger = logging.getLogger(__name__)


@dataclass
class ParsedAssetsType:
    """Данные типа из types.xml ."""
    name: str  # DBID
    py_type_name: str  # Dbid (Dbid = Uint64, а Uint64 = int)
    line_number: Optional[int] = None

    # Для простых типов
    base_type_name: Optional[str] = None  # UINT64

    # FIXED_DICT data
    fd_pairs: Optional[dict[str, str]] = None
    converter: Optional[str] = None
    inner_arr_names: list[str] = dataclasses.field(default_factory=list)

    # ARRAY data
    arr_of: Optional[str] = None
    arr_of_py_type_name: Optional[str] = None

    @property
    def is_fixed_dict(self) -> bool:
        return self.fd_pairs is not None

    @property
    def is_array(self) -> bool:
        return self.arr_of is not None

    @property
    def is_base_type(self) -> bool:
        """Основные типы идущие от KBEngine (UINT32 и т.п.)"""
        return not self.is_array and not self.is_fixed_dict \
            and self.base_type_name is None

    @property
    def is_base_type_alias(self) -> bool:
        return self.base_type_name is not None


AssetsTypeInfoByName = collections.OrderedDict[str, ParsedAssetsType]
_XMLElem = etree._Element


class TypesXMLParser:
    """Парсер types.xml ."""

    _PY_TYPE_BY_KBE_TYPE = {
        'UINT8': 'int',
        'UINT16': 'int',
        'UINT32': 'int',
        'UINT64': 'int',
        'INT8': 'int',
        'INT16': 'int',
        'INT32': 'int',
        'INT64': 'int',
        'FLOAT': 'float',
        'DOUBLE': 'float',
        'VECTOR2': 'Vector2',
        'VECTOR3': 'Vector3',
        'VECTOR4': 'Vector4',
        'STRING': 'str',
        'UNICODE': 'str',
        'PYTHON': 'dict',
        'PY_DICT': 'dict',
        'PY_TUPLE': 'tuple',
        'PY_LIST': 'list',
        'ENTITYCALL': 'EntityCall',
        'BLOB': 'bytes',
        'BOOL': 'bool',

        # Это на случай, если кто-то определит массив прямо в аргументе метода
        'ARRAY': 'list',
        'FIXED_DICT': 'dict',
    }

    def __init__(self, typesxml_path: Path):
        self._typesxml_path: Path = typesxml_path
        # Мапинг имени типа к его Python аналогуё
        self._type_map: dict[str, str] = {}
        self._type_map.update(self._PY_TYPE_BY_KBE_TYPE)
        self._aliases: dict[str, str] = {}  # Python type alias by types.xml type name
        logger.debug('[%s] %s', self, devonly.func_args_values())

    @staticmethod
    def _normalize_type_name(type_name: str) -> str:
        return ''.join(
            w.capitalize() for w in type_name.split('_')
        )

    def parse(self) -> AssetsTypeInfoByName:
        with self._typesxml_path.open('r', encoding='utf-8', errors='ignore') as fh:
            tree = etree.parse(fh) # type: ignore
        root = tree.getroot()

        res: AssetsTypeInfoByName = collections.OrderedDict()
        for kbe_type_name, py_type_name in self._PY_TYPE_BY_KBE_TYPE.items():
            res[kbe_type_name] = ParsedAssetsType(
                name=self._normalize_type_name(kbe_type_name),
                py_type_name=py_type_name
            )

        for elem in root.getchildren():
            if elem.tag is etree.Comment:
                continue
            elem_text = elem.text.strip()
            if elem_text == 'FIXED_DICT':
                for type_info in self._parse_fixed_dict(elem):
                    res[type_info.name] = type_info
            elif elem_text == 'ARRAY':
                type_info = self._parse_array(elem)
                res[type_info.name] = type_info
            else:
                type_info = self._parse_basic_type(elem)
                res[type_info.name] = type_info

        return res

    def _parse_basic_type(self, elem: _XMLElem) -> ParsedAssetsType:
        alias_type_name = elem.tag
        normalized_alias_type_name = self._normalize_type_name(alias_type_name)
        base_type_name: str = elem.text.strip()
        assert base_type_name in self._type_map

        self._type_map[alias_type_name] = normalized_alias_type_name

        return ParsedAssetsType(
            name=alias_type_name,
            py_type_name=normalized_alias_type_name,
            line_number=elem.sourceline,
            base_type_name=base_type_name
        )

    def _parse_array(self, elem: _XMLElem) -> ParsedAssetsType:
        alias_type_name: str = elem.tag
        array_el_type_name: str = elem.findall('of', namespaces=None)[0].text.strip()
        assert array_el_type_name in self._type_map

        normalized_alias_type_name = self._normalize_type_name(alias_type_name)
        normalized_el_type_name = self._normalize_type_name(array_el_type_name)

        self._type_map[alias_type_name] = normalized_alias_type_name

        return ParsedAssetsType(
            name=alias_type_name,
            py_type_name=normalized_alias_type_name,
            line_number=elem.sourceline,

            arr_of=array_el_type_name,
            arr_of_py_type_name=normalized_el_type_name
        )

    def _parse_fixed_dict(self, elem: _XMLElem) -> Generator[ParsedAssetsType, None, None]:
        # Используется генератор, т.к. может быть массив, определённый внутри
        # словаря и его нужно запомнить раньше (чтобы сгенерировать его тип
        # до генерации тела FD)
        alias_type_name: str = elem.tag
        normalized_alias_type_name = self._normalize_type_name(alias_type_name)

        converter = None
        converter_elem = elem.findall('implementedBy', namespaces=None)
        if converter_elem:
            converter = converter_elem[0].text.strip()

        pairs = {}
        inner_arr_names = []
        for fd_property_desc in elem.findall('Properties/*', namespaces=None):
            prop_name = fd_property_desc.tag
            type_elem = fd_property_desc.findall('Type')[0]
            prop_type_name = type_elem.text.strip()
            if prop_type_name == 'ARRAY':
                # Это может быть на лету определённый массив (он определяется прямо в FD).
                # В этом случае тип имеет имя "Type", поэтому изменим его на имя
                # связанное с этим FD.
                elem_name = f'{alias_type_name}_Inner_Arr1'
                type_elem.tag = elem_name
                # Таким образом добавлен тип данных этого массива и будет в дальнейшем сгенерирован
                arr_info = self._parse_array(type_elem)
                assert arr_info.arr_of_py_type_name is not None
                yield arr_info
                inner_arr_names.append(arr_info.name)
                py_prop_type_name = arr_info.py_type_name
            else:
                py_prop_type_name = self._type_map[prop_type_name]

            pairs[prop_name] = py_prop_type_name

        self._type_map[alias_type_name] = normalized_alias_type_name

        yield ParsedAssetsType(
            name=alias_type_name,
            py_type_name=normalized_alias_type_name,
            line_number=elem.sourceline,
            fd_pairs=pairs,
            converter=converter,
            inner_arr_names=inner_arr_names,
        )
