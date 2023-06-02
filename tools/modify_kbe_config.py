"""The script modifies the kbengine.xml configuration file so KBEngine can work with docker.

It would be placed in the root directory of the assets.
"""

import argparse
import datetime
import logging
import shutil
import sys
import xml.dom.minidom
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List


HOST_ADDR = '0.0.0.0'
TITLE = ('The script modifies the kbengine.xml configuration file so KBEngine '
         'can work with docker.')
FORMAT = '[%(levelname)s] %(asctime)s [%(filename)s:%(lineno)s - %(funcName)s()] %(message)s'

logger = logging.getLogger(__file__)


def read_args():
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--kbe-assets-path', dest='kbe_assets_path', type=str,
                        required=True,
                        help='The path to the game assets')
    parser.add_argument('--env-file', dest='env_file_path', type=str,
                        required=True,
                        help='Settings file')
    parser.add_argument('--log-level', dest='log_level', type=str,
                        default='DEBUG',
                        choices=logging._nameToLevel.keys(),
                        help='Logging level')
    parser.add_argument('--kbengine-xml-args', dest='custom_settings', type=str,
                        help='This field will be modified in kbengine.xml')

    return parser.parse_args()


def setup_root_logger(level_name: str):
    level = logging.getLevelName(level_name)
    logger = logging.getLogger()
    logger.setLevel(level)
    stream_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(FORMAT)
    stream_handler.setFormatter(formatter)
    logger.handlers = [stream_handler]
    logger.info(f'Logger was set (log level = "{level_name}")')


def check_settings(settings: dict) -> bool:
    """Check settings file."""
    res = True
    for name, value in settings.items():
        value = value.strip()
        if name == 'MYSQL_DATABASE' and not value:
            logger.error('The variable "MYSQL_DATABASE" is empty')
            res = False
        if name == 'MYSQL_USER' and not value:
            logger.error('The variable "MYSQL_USER" is empty')
            res = False
        if name == 'MYSQL_PASSWORD' and not value:
            logger.error('The variable "MYSQL_PASSWORD" is empty')
            res = False

    return res


def set_shedu_net_settings(root: ET.Element, settings: dict):
    """
    Set the necessary net settings to the kbengine.xml config to work
    with the "shedu" project.
    """
    dbmgr_el = root.find('dbmgr')
    if dbmgr_el is None:
        dbmgr_el = ET.SubElement(root, 'dbmgr')

    databaseInterface_el = dbmgr_el.find('databaseInterfaces')  # noqa
    if databaseInterface_el is None:
        databaseInterface_el = ET.SubElement(dbmgr_el, 'databaseInterfaces')

    default_el = databaseInterface_el.find('default')
    if default_el is None:
        default_el = ET.SubElement(databaseInterface_el, 'default')

    new_default_el = ET.fromstring(f"""
        <default>
            <type> mysql </type>
            <host> kbe-mariadb </host>
            <port> 0 </port>
            <auth>
                <username> {settings['MYSQL_USER'].strip()} </username>
                <password> {settings['MYSQL_PASSWORD'].strip()} </password>
            </auth>
            <databaseName> {settings['MYSQL_DATABASE'].strip()} </databaseName>
        </default>
    """)

    to_update_els = [el for el in new_default_el if el is not new_default_el]
    for new_el in to_update_els:
        el = default_el.find(new_el.tag)
        if el is not None:
            default_el.remove(el)
        default_el.append(new_el)

    logger.info('Updated elements: {tags})'.format(
        tags=', '.join(f'"{el.tag}"' for el in to_update_els))
    )

    shareDB_el = dbmgr_el.find('shareDB')
    if shareDB_el is None:
        shareDB_el = ET.SubElement(dbmgr_el, 'shareDB')
    shareDB_el.text = 'true'

    logger.info('Updated "shareDB"')

    for name in ('baseapp', 'loginapp'):
        app_el = root.find(name)
        if app_el is None:
            app_el = ET.SubElement(root, name)

        externalAddress_el = app_el.find('externalAddress')
        if externalAddress_el is None:
            externalAddress_el = ET.SubElement(app_el, 'externalAddress')
        externalAddress_el.text = HOST_ADDR

        logger.info(f'Updated {name} "externalAddress"')

    # Т.к. Interfaces находится в соседнем контейнере, нужно задать хост
    interfaces_el = root.find('interfaces')
    if interfaces_el is None:
        interfaces_el = ET.SubElement(root, 'interfaces')
    ihost_el = interfaces_el.find('host')
    if ihost_el is None:
        ihost_el = ET.SubElement(interfaces_el, 'host')
    # Выставляем имя сервиса в docker-compose.yml
    ihost_el.text = 'interfaces'
    logger.info('Updated "root/interfaces/host"')


def _add_element(root: ET.Element, path: str) -> ET.Element:
    for tag in path.split('/'):
        elem = root.find(tag)
        if elem is None:
            elem = ET.SubElement(root, tag)
        root = elem
    return root


def _add_signature(root: ET.Element, settings: dict, namespace: argparse.Namespace):
    sign_elem = ET.fromstring(f"""
    <shedu>
        <comment> This configuration file has been updated by the "Shedu" project </comment>
        <shedu_site> https://github.com/ve-i-uj/shedu </shedu_site>
        <build_data>
            <assets_path> {namespace.kbe_assets_path.strip()} </assets_path>
            <env_file_path> {namespace.env_file_path.strip()} </env_file_path>
            <utc_date> {datetime.datetime.utcnow()} </utc_date>
            <env_variables>
                <KBE_GIT_COMMIT> {settings['KBE_GIT_COMMIT'].strip()} </KBE_GIT_COMMIT>
                <KBE_USER_TAG> {settings['KBE_USER_TAG'].strip()} </KBE_USER_TAG>
                <KBE_ASSETS_SHA> {settings['KBE_ASSETS_SHA'].strip()} </KBE_ASSETS_SHA>
                <KBE_ASSETS_VERSION> {settings['KBE_ASSETS_VERSION'].strip()} </KBE_ASSETS_VERSION>
                <KBE_ASSETS_PATH> {settings['KBE_ASSETS_PATH'].strip()} </KBE_ASSETS_PATH>
            </env_variables>
        </build_data>
    </shedu>
    """)
    root.append(sign_elem)


def set_custom_settings(root: ET.Element, settings: List[str]):
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
    setup_root_logger(level_name=namespace.log_level)
    kbengine_xml_path = Path(namespace.kbe_assets_path) / 'res' / 'server' / 'kbengine.xml'
    if not kbengine_xml_path.exists():
        logger.error('There is no kbengine.xml by path "%s"', kbengine_xml_path)
        sys.exit(1)

    settings_path = Path(namespace.env_file_path)
    if not settings_path.exists():
        logger.error('There is no settings env file by path "%s"', settings_path)
        sys.exit(1)

    settings: dict[str, str] = {}
    for line in settings_path.open(encoding='utf-8'):
        if not line.strip() or line.strip().startswith('#'):
            continue
        var_name, value = line.split('=', 1)
        if not var_name:
            logger.warning('A strange line is in the config file ("%s")', line)
            continue
        settings[var_name] = value

    if not check_settings(settings):
        sys.exit(1)

    logger.info('Copy origin "kbengine.xml" (to "kbengine.xml.bak") ')
    shutil.copyfile(kbengine_xml_path,
                    kbengine_xml_path.with_suffix(kbengine_xml_path.suffix + '.bak'))

    tree: ET.ElementTree = ET.parse(kbengine_xml_path)
    root = tree.getroot()
    if root is None:
        logger.error(f'There is no "root" element in the kbengine.xml')
        return

    custom_settings = namespace.custom_settings.split(';')
    logger.debug(f'Custom settings: {custom_settings}')
    if namespace.custom_settings != '':
        set_custom_settings(root, custom_settings)
    set_shedu_net_settings(root, settings)

    _add_signature(root, settings, namespace)

    root_str = _prettify_xml(root)
    with open(kbengine_xml_path, 'w') as fh:
        fh.write(root_str)

    logger.info(f'The config "{kbengine_xml_path}" has been updated')


if __name__ == '__main__':
    main()
