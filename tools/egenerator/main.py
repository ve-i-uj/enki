#!/usr/bin/env python

"""Updater of client messages (code generator)."""

import asyncio
import logging
import os
from pathlib import Path
import shutil
from types import ModuleType
from typing import List

from enki.misc import log

from tools.egenerator import settings
from tools.egenerator import parser, codegen, datagetter
from tools.parsers import EntityDefParser, KBEngineXMLParser, DefClassData, \
    EntitiesXMLParser

logger = logging.getLogger(__name__)


async def generate_code():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))

    # Parse assets info
    assets_ent_data: dict[str, DefClassData] = {}
    entities_xml_parser: EntitiesXMLParser = EntitiesXMLParser(settings.ENTITIES_XML_PATH)
    entity_def_parser: EntityDefParser = EntityDefParser(settings.ENTITY_DEFS_DIR)
    for ent_data in entities_xml_parser.parse().get_all():
        assets_ent_data[ent_data.name] = entity_def_parser.parse(ent_data.name)

    # Read component entities
    assets_ent_c_data: dict[str, DefClassData] = {}
    entity_def_parser: EntityDefParser = EntityDefParser(settings.ENTITY_DEFS_COMPONENT_DIR)
    for filename in os.listdir(settings.ENTITY_DEFS_COMPONENT_DIR):
        if filename.endswith('.def') and filename[0].isupper():
            comp_name: str = filename.rsplit('.', 1)[0]
            assets_ent_c_data[comp_name] = entity_def_parser.parse(comp_name)

    # Generate entity descriptions
    if settings.GAME_GENERATED_CLIENT_API_DIR.exists():
        shutil.rmtree(settings.GAME_GENERATED_CLIENT_API_DIR)
    settings.GAME_GENERATED_CLIENT_API_DIR.mkdir(parents=True)
    with (settings.GAME_GENERATED_CLIENT_API_DIR / '__init__.py').open('w') as fh:
        fh.write(f'"""The package contains generated python code for '
                 f'the KBEngine client.\n\nGenerated by the "enki" '
                 f'project <{settings.PROJECT_SITE}>\n"""\n\n')
        fh.write('from . import deftype, eserializer, kbenginexml, gameentity, description\n')

    if settings.INCLUDE_MSGES:
        # Generate app descriptions
        login_app_data, base_app_data = await datagetter.app_get_data(
            settings.GAME_ACCOUNT_NAME, settings.GAME_PASSWORD
        )
        parser_ = parser.ClientMsgesParser()
        msg_specs: List[parser.ParsedAppMessageDC] = []
        for app_data in (login_app_data, base_app_data):
            msg_specs.extend(parser_.parse(app_data))

        code_generator = codegen.AppMessagesCodeGen(settings.CodeGenDstPath.APP)
        code_generator.generate(msg_specs)

    if settings.INCLUDE_ERRORS:
        error_dst_path = settings.CodeGenDstPath.SERVERERROR
        error_data = await datagetter.error_get_data()
        parser_ = parser.ServerErrorParser()
        error_specs = parser_.parse(error_data)
        error_code_gen = codegen.ErrorCodeGen(error_dst_path)
        error_code_gen.generate(error_specs)

    # Generate entity descriptions
    type_dst_path = settings.CodeGenDstPath.TYPE
    entity_dst_path = settings.CodeGenDstPath.ENTITY
    eserialier_dst_path = settings.CodeGenDstPath.SERIALIZER_ENTITY

    data = await datagetter.entity_get_data(
        settings.GAME_ACCOUNT_NAME, settings.GAME_PASSWORD
    )
    parser_ = parser.EntityDefParser()
    type_specs, entities = parser_.parse(data)

    type_code_gen = codegen.TypesCodeGen(type_dst_path)
    type_code_gen.generate(type_specs)

    # TODO: [2022-09-22 17:59 burov_alexey@mail.ru]:
    # Это нужно в процедуру (загрузка deftype)
    import sys
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'deftype',
        settings.CodeGenDstPath.TYPE
    )
    assert spec is not None and spec.loader is not None
    module: ModuleType = importlib.util.module_from_spec(spec)
    sys.modules['deftype'] = module
    spec.loader.exec_module(module)

    entity_code_gen = codegen.EntitiesCodeGen(entity_dst_path)
    entity_code_gen.generate(entities, assets_ent_data, assets_ent_c_data, module)

    eserializer_code_gen = codegen.EntitySerializersCodeGen(eserialier_dst_path)
    eserializer_code_gen.generate(entities, assets_ent_data, assets_ent_c_data, module)

    # Generate data of kbengine.xml
    logger.info(f'Generate settings from kbengine.xml ... (to '
                f'"{settings.CodeGenDstPath.KBENGINE_XML}")')
    data = KBEngineXMLParser(settings.KBENGINE_XML_PATH).parse()
    code_gen = codegen.KBEngineXMLDataCodeGen(
        settings.CodeGenDstPath.KBENGINE_XML
    )
    code_gen.generate(data)


async def main():
    try:
        await generate_code()
        logger.info('Done')
    except datagetter.StopClientException as err:
        logger.warning(err)
    except Exception as err:
        logger.error(err, exc_info=True)


if __name__ == '__main__':
    asyncio.run(main())
