"""Module implements functions for parsing the defenitions of kbe entities."""

from __future__ import annotations

import logging
import pathlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Union, Any

from lxml import etree

from enki.misc import devonly


logger = logging.getLogger(__name__)


@dataclass
class PropertyData:
    """Description of an entity property."""
    name: str
    type: str
    flags: str
    comment: Union[str, None] = None
    utype: Union[int, None] = None
    persistent: bool = False
    default: Any = None


@dataclass
class MethodArgData:
    """Method argument data."""
    def_type: str
    comment: Union[str, None] = None


@dataclass
class MethodData:
    """Description of an entity method."""
    # context of KBEngine (cell, base, client)
    context: str
    name: str
    exposed: bool = False
    comment: Union[str, None] = None
    utype: Union[int, None] = None
    args: list[MethodArgData] = field(default_factory=lambda: [])


@dataclass
class EntityComponentData:
    name: str
    type: str
    persistent: bool = False


@dataclass
class DefClassData:
    """Def file description."""
    name: str
    doc: Union[str, None] = None
    Interfaces: list[DefClassData] = field(default_factory=lambda: [])
    Properties: list[PropertyData] = field(default_factory=lambda: [])
    BaseMethods: list[MethodData] = field(default_factory=lambda: [])
    CellMethods: list[MethodData] = field(default_factory=lambda: [])
    ClientMethods: list[MethodData] = field(default_factory=lambda: [])
    Components: list[MethodData] = field(default_factory=lambda: [])


class EntityDefParser:

    def __init__(self, entitydef_dir: Path):
        self._entitydef_dir: Path = entitydef_dir
        self._interfaces_dir: Path = entitydef_dir / 'interfaces'
        self._components_dir: Path = entitydef_dir / 'components'

    def parse(self, entity_name: str) -> DefClassData:
        """Return parsed data of the entity def file."""
        logger.debug('(%s)', devonly.func_args_values())
        def_path: Path = self._entitydef_dir / (entity_name + '.def')
        def_data: DefClassData = self._parse_def_file(entity_name, def_path)
        return def_data

    def _parse_components(self, name: str) -> EntityComponentData:
        raise NotImplementedError

    def _parse_interface(self, interface_name: str) -> DefClassData:
        logger.debug('(%s)', devonly.func_args_values())
        def_path: Path = self._interfaces_dir / (interface_name + '.def')
        def_data: DefClassData = self._parse_def_file(interface_name, def_path)
        return def_data

    def _parse_def_file(self, entity_name: str, def_path: Path) -> DefClassData:
        """Parse gotten def file."""
        tree = etree.parse(def_path.as_posix())
        root = tree.getroot()

        def_class_data: DefClassData = DefClassData(entity_name)
        if root[0].tag is etree.Comment:
            def_class_data.doc = root[0].text.strip()
        for elem in root.findall('Interfaces/Interface'):
            if type(elem) is not etree._Element:
                continue
            interface_name: str = elem.text.strip()
            i_def_class_data: DefClassData = self._parse_interface(interface_name)
            def_class_data.Interfaces.append(i_def_class_data)
        for elem in root.findall('Components/*'):
            if type(elem) is not etree._Element:
                continue
            name: str = elem.tag
            type_ = None
            persistent = None
            for e in elem.getchildren():
                if e.tag == 'Type':
                    type_ = e.text.strip()
                elif e.tag == 'Persistent':
                    persistent = e.text.strip() == 'true'
            data: EntityComponentData = EntityComponentData(name, type_, persistent)
            def_class_data.Components.append(data)
        if root.find('Properties') is not None:
            for elem in root.find('Properties'):
                if type(elem) is not etree._Element:
                    continue
                def_class_data.Properties.append(
                    EntityDefParser._parse_property(elem))
        for tag in ('BaseMethods', 'CellMethods', 'ClientMethods'):
            methods_elem = root.find(tag)
            if methods_elem is None:
                continue
            context = tag.replace('Methods', '').lower(),
            parsed_methods = []
            for elem in methods_elem.getchildren():
                if type(elem) is not etree._Element:
                    continue
                parsed_methods.append(
                    EntityDefParser._parse_method(context, elem))
            setattr(def_class_data, tag, parsed_methods)

        return def_class_data

    @staticmethod
    def _parse_method(context, method_elem) -> MethodData:
        """Parse xml element of method definition in an entity def-file."""
        method_data = MethodData(
            context=context,
            name=method_elem.tag.strip()
        )

        # upper comment is the comment of the method
        if type(method_elem.getprevious()) is etree._Comment:
            method_data.comment = method_elem.getprevious().text.strip()

        for elem in method_elem.getchildren():
            if type(elem) is not etree._Element:
                continue
            if elem.tag.strip() == 'Exposed':
                method_data.exposed = True
            elif elem.tag.strip() == 'Utype':
                method_data.utype = int(elem.text.strip())
            elif elem.tag.strip() == 'Arg':
                arg_data = MethodArgData(elem.text.strip())
                method_data.args.append(arg_data)
                # right side comment of the tag `Arg` is the name of the argument
                if type(elem.getnext()) is etree._Comment:
                    arg_data.comment = elem.getnext().text.strip()
                continue

        return method_data

    @staticmethod
    def _parse_property(property_elem: etree._Element) -> PropertyData:
        """Parse a property of an entity in a def file."""
        property_data = PropertyData(
            name=property_elem.tag.strip(),
            type=property_elem.find('Type').text.strip(),
            flags=property_elem.find('Flags').text.strip()
        )
        if type(property_elem.getprevious()) is etree._Comment:
            property_data.comment = property_elem.getprevious().text.strip()
        for elem in property_elem.getchildren():
            if type(elem) is not etree._Element:
                continue
            if elem.tag.strip() == 'Utype':
                property_data.utype = int(elem.text.strip())
            elif elem.tag.strip() == 'Persistent':
                property_data.persistent = (elem.text.strip() == 'true')

        return property_data
