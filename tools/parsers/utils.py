import logging

from .entitiesxml import EntitiesXMLData, EntityData
from .entitydef import DefClassData

from enki.misc import devonly

logger = logging.getLogger(__name__)


def normalize_entitiesxml(entitiesxml_data: EntitiesXMLData,
                          edef_data_by_name: dict[str, DefClassData]) -> EntitiesXMLData:
    """Добавляет атрибуты hasCell, hasBase сущности, если это требуется."""
    logger.debug('%s', devonly.func_args_values())
    new_entities_data: list[EntityData] = []
    for edata in entitiesxml_data.get_all():
        edef_data = edef_data_by_name[edata.name]
        edef_data = edef_data.get_merged()
        if edata.hasBase or edef_data.has_base:
            edata.hasBase = True
        if edata.hasCell or edef_data.has_cell:
            edata.hasCell = True
        # Похоже, что только если прямо прописан клиент считается, что он есть
        # if edata.hasClient or edef_data.has_client:
        if edata.hasClient:
            edata.hasClient = True
        new_entities_data.append(edata)

    return EntitiesXMLData(tuple(new_entities_data))
