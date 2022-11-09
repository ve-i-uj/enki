"""The parser of file `kbengine.xml`"""

import pathlib
import logging
import sys
from dataclasses import dataclass

import xmltodict

from enki.net.msgspec import default_kbenginexml

logger = logging.getLogger(__name__)


@dataclass
class ParsedKBEngineXMLDC:
    """Data of entities from file `kbengine.xml`."""
    # There will be only one instance of this class. That's why we don't need
    # to take into account that the original default data will be changed.
    root: default_kbenginexml.root = default_kbenginexml.root()


class KBEngineXMLParser:
    """The parser of the `kbengine.xml` file."""

    def __init__(self, path: pathlib.Path):
        self._path = path

    def parse(self) -> ParsedKBEngineXMLDC:
        """Parses the `kbengine.xml` file."""
        with open(self._path) as fh:
            kbenginexml_dct = xmltodict.parse(fh.read())
        res = ParsedKBEngineXMLDC()
        try:
            stack = [(kbenginexml_dct['root'], ['root'])]
            while stack:
                root, parent_names = stack.pop()
                for key, value in root.items():
                    if value is None:
                        continue
                    if isinstance(value, (int, float, str, bool)):
                        ptr = res
                        for name in parent_names:
                            ptr = getattr(ptr, name)
                        if value in ('true', 'false'):
                            setattr(ptr, key, value == 'true')
                            continue
                        setattr(ptr, key, type(getattr(ptr, key))(value))
                        continue

                    if isinstance(value, list):
                        raise NotImplementedError
                    # It's a child
                    stack.append((value, parent_names + [key]))
        except KeyError as err:
            logger.error(f'{err} . Invalid kbengine.xml? Exit')
            sys.exit(1)

        return res
