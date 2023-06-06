"""Скрипт добавляет атрибуты hasBase, hasCell, hasClient сущности в entities.xml.

Скрипт однозначно прописывает в entities.xml наличие hasCell, hasBase,
hasClient, основываясь на том, что написано в файле entities.xml и на наличии
методов и свойств сущности. Это решает проблему непрозрачного выставления KBEngine
по умолчанию значений этим атрибутам.

Наприер, есть следующая проблема:
Из-за того, что в kbengine-demo-assets всем сущностям записан GameObject
в интерфейсы, все сущности имеют cell и client
свойства. При запуске компонентов в отдельном контейнере KBEngine
выдаёт ошибку, что не указано у сущности, что она имеет cell
составляющую (hasCell не указана в entities.xml). Поэтому нужно
поправить этот файл перед помещением в контейнер. Если же все серверные
компоненты в одном контейнере, то hasCell высчитывается по какой-то неизвестной
логике и проблемы не возникает. Почему это так - неизвестно.
"""

import logging

from enki.misc import log

from tools import parsers
from tools.parsers import EntitiesXMLParser, EntityDefParser, EntitiesXMLData

from tools.normalize_entitiesxml import settings


def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))
    exml_parser = EntitiesXMLParser(settings.ENTITIES_XML_PATH)
    exml_data = exml_parser.parse()
    edef_parser = EntityDefParser(settings.ENTITY_DEFS_DIR)
    edef_data = {
        ed.name: edef_parser.parse(ed.name) for ed in exml_data.get_all()
    }
    updated_exml_data = parsers.utils.normalize_entitiesxml(
        exml_data, edef_data
    )
    updated_exml_data.to_file(settings.UPDATED_ENTITIES_XML_PATH)


if __name__ == '__main__':
    main()
