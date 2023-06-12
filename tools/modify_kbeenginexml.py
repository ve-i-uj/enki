"""The script modifies the "kbengine.xml" configuration file."""

import argparse
import datetime
import itertools
import logging
import shutil
import sys
import xml.dom.minidom
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List

from enki.misc import log


TITLE = ('The script modifies the kbengine.xml configuration file so KBEngine '
         'can work with docker.')

logger = logging.getLogger(__file__)


def read_args():
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--kbe-assets-path', dest='kbe_assets_path', type=str,
                        required=True,
                        help='The path to the game assets')
    parser.add_argument('--data-file', dest='data_file_path', type=str,
                        required=False,
                        help=('The data file path contained attributes need '
                              'to be changed in kbengine.xml'))
    parser.add_argument('--log-level', dest='log_level', type=str,
                        default='DEBUG',
                        choices=logging._nameToLevel.keys(),
                        help='Logging level')
    parser.add_argument('--kbengine-xml-args', dest='custom_settings', type=str,
                        help='This field will be modified in kbengine.xml')

    return parser.parse_args()


def _add_element(root: ET.Element, path: str) -> ET.Element:
    for tag in path.split('/'):
        elem = root.find(tag)
        if elem is None:
            elem = ET.SubElement(root, tag)
        root = elem
    return root


def update_kbenginexml(root: ET.Element, settings: list[str]):
    """Set user settings to the kbengine.xml ."""
    for s in settings:
        pair = s.split('=', 1)
        if len(pair) != 2:
            logger.warning(f'Invalid format of settings value ("{s}"). Skip')
            continue
        path, value = pair
        path = path.replace('.', '/')
        path = path.split('/', 1)[1]
        elems = root.findall(path)
        if not elems:
            logger.info(f'There is no element "{path}". It will be added')
            elem = _add_element(root, path)
            elems = [elem]
        if len(elems) > 1:
            logger.warning(f'Updating of element list is not implemented ("{s}"). Skip')
            continue

        elem = elems[0]
        priv_text = elem.text
        elem.text = f' {value.strip()} '
        logger.info(f'Updated: {elem.tag} = {elem.text} (old = {priv_text})')


def _prettify_xml(elem: ET.Element) -> str:
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'unicode')
    rough_string = ''.join(line.strip() for line in rough_string.split('\n') if line.strip())
    return xml.dom.minidom.parseString(rough_string).toprettyxml(indent="\t")


def main():
    namespace = read_args()
    log.setup_root_logger(namespace.log_level)
    kbengine_xml_path = Path(namespace.kbe_assets_path) / 'res' / 'server' / 'kbengine.xml'
    if not kbengine_xml_path.exists():
        logger.error('There is no kbengine.xml by path "%s"', kbengine_xml_path)
        sys.exit(1)

    settings_path = Path(namespace.data_file_path)
    if not settings_path.exists():
        logger.error('There is no data file contained kbengine.xml attributes "%s"', settings_path)
        sys.exit(1)

    tree: ET.ElementTree = ET.parse(kbengine_xml_path)
    root = tree.getroot()
    if root is None:
        logger.error(f'There is no "root" element in the kbengine.xml')
        sys.exit(1)

    settings: list[str] = []
    with settings_path.open(encoding='utf-8') as fh:
        for line in fh:
            if not line.strip() or line.strip().startswith('#'):
                continue
            settings.append(line)

    if namespace.custom_settings is not None or namespace.custom_settings != '':
        custom_settings: list[str] = namespace.custom_settings.split(';')
        logger.debug(f'Custom settings: {custom_settings}')
        settings.extend(custom_settings)

    logger.info('Copy origin "kbengine.xml" (to "kbengine.xml.bak") ')
    shutil.copyfile(kbengine_xml_path,
                    kbengine_xml_path.with_suffix(kbengine_xml_path.suffix + '.bak'))

    update_kbenginexml(root, settings)

    root_str = _prettify_xml(root)
    with open(kbengine_xml_path, 'w') as fh:
        fh.write(root_str)

    logger.info(f'The config "{kbengine_xml_path}" has been updated')


if __name__ == '__main__':
    main()
