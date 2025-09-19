"""The parser of file `entities.xml`."""

import logging
from dataclasses import dataclass
from pathlib import Path

from lxml import (
    etree,  # pyright: ignore[reportUnknownVariableType, reportAttributeAccessIssue]
)

from enki.misc import devonly

logger = logging.getLogger(__name__)


@dataclass
class EntityData:
    """The entity data from file 'entities.xml'."""

    name: str
    # `id` is the entity id in DB. It is given with the same order
    # like in `entities.xml` file
    id: int
    hasBase: bool = False  # noqa: N815
    hasCell: bool = False  # noqa: N815
    hasClient: bool = False  # noqa: N815


class EntitiesXMLData:
    """Class implements access methods to parsed data of the file `entities.xml`."""

    def __init__(self, parsed_data: tuple[EntityData]) -> None:
        self._parsed_data = parsed_data

    def get_all(self) -> tuple[EntityData, ...]:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        return self._parsed_data

    def get_base(self) -> tuple[EntityData, ...]:
        """All entities have `base` context."""
        return tuple(d for d in self._parsed_data if d.hasBase)

    def get_cell(self) -> tuple[EntityData, ...]:
        """All entities have `cell` context."""
        return tuple(d for d in self._parsed_data if d.hasCell)

    def get_client(self) -> tuple[EntityData, ...]:
        """All entities have `client` context."""
        return tuple(d for d in self._parsed_data if d.hasClient)

    def write_to_file(self, path: Path) -> None:
        """Записать данные entities.xml в файл, переданный в аргументе."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        with path.open("w") as fh:
            fh.write("<root>\n")
            for edata in self._parsed_data:
                fh.write(
                    f'    <{edata.name} hasBase="{str(edata.hasBase).lower()}" '
                    f'hasCell="{str(edata.hasCell).lower()}" '
                    f'hasClient="{str(edata.hasClient).lower()}">'
                    f"</{edata.name}>\n"
                )
            fh.write("</root>\n")


class EntitiesXMLParser:
    """The parser of the file `entities.xml` ."""

    def __init__(self, entities_path: Path) -> None:
        self._entities_path = entities_path
        logger.debug("[%s] %s", self, devonly.func_args_values())

    def parse(self) -> EntitiesXMLData:
        """Parses the `entities.xml` file."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        tree = etree.parse(self._entities_path.as_posix(), parser=None)
        root = tree.getroot()
        ents = []
        i = 0
        for elem in root.getchildren():
            if type(elem) is not etree._Element:
                continue
            entity_data: EntityData = EntityData(name=elem.tag.strip(), id=i)

            entity_data.hasBase = elem.attrib.get("hasBase", "false") == "true"
            entity_data.hasCell = elem.attrib.get("hasCell", "false") == "true"
            entity_data.hasClient = (
                elem.attrib.get("hasClient", "false") == "true"
            )

            ents.append(entity_data)
            i += 1

        return EntitiesXMLData(tuple(ents))
