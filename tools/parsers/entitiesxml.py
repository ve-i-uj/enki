"""The parser of file `entities.xml`"""

import pathlib
from dataclasses import dataclass

from lxml import etree


@dataclass
class EntityData:
    """Data of entities from file `entities.xml`."""
    name: str
    # `id` is the entity id in DB. It is given with the same order
    # like in `entities.xml` file
    id: int
    hasBase: bool = False
    hasCell: bool = False
    hasClient: bool = False


class EntitiesXMLData:
    """Class implements access methods to parsed data of the file `entities.xml`."""

    def __init__(self, parsed_data: tuple[EntityData]):
        self._parsed_data = parsed_data

    def get_all(self) -> tuple[EntityData]:
        return self._parsed_data

    def get_base(self) -> tuple[EntityData]:
        """All entities have `base` context."""
        return tuple(d for d in self._parsed_data if d.hasBase)

    def get_cell(self) -> tuple[EntityData]:
        """All entities have `cell` context."""
        return tuple(d for d in self._parsed_data if d.hasCell)

    def get_client(self) -> tuple[EntityData]:
        """All entities have `client` context."""
        return tuple(d for d in self._parsed_data if d.hasClient)


class EntitiesXMLParser:
    """The parser of the file `entities.xml` ."""

    def __init__(self, entities_path: pathlib.Path):
        self._entities_path = entities_path

    def parse(self) -> EntitiesXMLData:
        """Parses the `entities.xml` file."""
        tree = etree.parse(self._entities_path.as_posix())
        root = tree.getroot()
        ents = []
        i = 0
        for elem in root.getchildren():
            if type(elem) is not etree._Element:
                continue
            entity_data: EntityData = EntityData(name=elem.tag.strip(), id=i)

            entity_data.hasBase = (elem.attrib.get('hasBase', 'false') == 'true')
            entity_data.hasCell = (elem.attrib.get('hasCell', 'false') == 'true')
            entity_data.hasClient = (elem.attrib.get('hasClient', 'false') == 'true')

            ents.append(entity_data)
            i += 1

        return EntitiesXMLData(tuple(ents))
