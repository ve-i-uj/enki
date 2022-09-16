#!/usr/bin/env python

"""Updater of client messages (code generator)."""

import argparse
import functools
import importlib
import logging
import os
import signal
import shutil
from pathlib import Path
from types import ModuleType
from typing import List

from tornado import ioloop

from enki.misc import log, runutil
from enki import exception

from tools.ninmah import settings
from tools.ninmah import parser, codegen, datagetter
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

    shutdown_func = functools.partial(runutil.shutdown, 0)
    sig_exit_func = functools.partial(runutil.sig_exit, shutdown_func)
    signal.signal(signal.SIGINT, sig_exit_func)
    signal.signal(signal.SIGTERM, sig_exit_func)

    # Generate entity descriptions
    if settings.DST_DIR.exists():
        shutil.rmtree(settings.DST_DIR)
    settings.DST_DIR.mkdir()
    with (settings.DST_DIR / '__init__.py').open('w') as fh:
        fh.write('from . import deftype, entity, kbenginexml')

    if settings.INCLUDE_MSGES:
        # Generate app descriptions
        login_app_data, base_app_data = await datagetter.app_get_data(
            settings.ACCOUNT_NAME, settings.PASSWORD
        )
        parser_ = parser.ClientMsgesParser()
        msg_specs: List[parser.ParsedAppMessageDC] = []
        for app_data in (login_app_data, base_app_data):
            msg_specs.extend(parser_.parse(app_data))

        code_generator = codegen.AppMessagesCodeGen(settings.CodeGenDstPath.APP)
        code_generator.generate(msg_specs)

        # Generate error descriptions
        error_dst_path = settings.CodeGenDstPath.SERVERERROR
        error_data = await datagetter.error_get_data()
        parser_ = parser.ServerErrorParser()
        error_specs = parser_.parse(error_data)
        error_code_gen = codegen.ErrorCodeGen(error_dst_path)
        error_code_gen.generate(error_specs)

    # Generate entity descriptions
    type_dst_path = settings.CodeGenDstPath.TYPE
    entity_dst_path = settings.CodeGenDstPath.ENTITY

    data = await datagetter.entity_get_data(
        settings.ACCOUNT_NAME, settings.PASSWORD
    )

    parser_ = parser.EntityDefParser()
    type_specs, entities = parser_.parse(data)

    type_code_gen = codegen.TypesCodeGen(type_dst_path)
    type_code_gen.generate(type_specs)

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

    # Generate data of kbengine.xml
    logger.info(f'Generate settings from kbengine.xml ... (to '
                f'"{settings.CodeGenDstPath.KBENGINE_XML}")')
    data = KBEngineXMLParser(settings.KBENGINE_XML_PATH).parse()
    code_gen = codegen.KBEngineXMLDataCodeGen(
        settings.CodeGenDstPath.KBENGINE_XML
    )
    code_gen.generate(data)


def main():

    async def create():
        try:
            await generate_code()
            logger.info('Done')
        except exception.StopClientException as err:
            logger.warning(err)
        except Exception as err:
            logger.error(err, exc_info=True)
        await runutil.shutdown(0)

    ioloop.IOLoop.current().asyncio_loop.create_task(create())  # type: ignore
    ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
