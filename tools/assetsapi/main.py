"""Точка входа для генератора API серверных сущностей."""

import functools
import logging
from pathlib import Path
import shutil

import jinja2

from enki.misc import log

from tools.assetsapi import settings
from tools.parsers import TypesXMLParser
from tools.parsers.entitiesxml import EntitiesXMLParser
from tools.parsers.entitydef import DefClassData, EntityDefParser
from tools.parsers.typesxml import AssetsTypeInfoByName

from tools.assetsapi import utils
from tools.parsers.usertype import UserTypeInfos, UsetTypeParser


def generate_types(type_info_by_name: AssetsTypeInfoByName,
                   user_type_infos: UserTypeInfos, dst_path: Path):
    with settings.Templates.TYPESXML_JINJA_TEMPLATE_PATH.open('r') as fh:
        jinja_entity_template = fh.read()
    jinja_env = jinja2.Environment()
    template = jinja_env.from_string(jinja_entity_template)
    types_text = template.render(
        type_info_by_name=type_info_by_name,
        user_type_infos=user_type_infos
    )
    with dst_path.open('w') as fh:
        fh.write(types_text)


def generate_entities(entity_defs_dir: Path,
                      dst_dir: Path,
                      type_info_by_name: AssetsTypeInfoByName,
                      user_type_infos: UserTypeInfos,
                      edef_data: dict[str, DefClassData]):
    with settings.Templates.ENTITY_JINJA_TEMPLATE_PATH.open('r') as fh:
        jinja_entity_template = fh.read()
    jinja_env = jinja2.Environment()
    template = jinja_env.from_string(jinja_entity_template)
    dst_dir.mkdir(exist_ok=True)
    for entity_name, entity_info in edef_data.items():
        entity_text = template.render(
            type_info_by_name=type_info_by_name,
            entity_info=entity_info,
            build_method_args=functools.partial(
                utils.build_method_args, user_type_infos=user_type_infos
            )
        )
        with (dst_dir / f'{entity_name.lower()}.py').open('w') as fh:
            fh.write(entity_text)


def copy_modules_from_enki(collection_path: Path, vector_path: Path,
                           itype_dir: Path, dst_dir: Path):
    shutil.copyfile(collection_path, dst_dir / 'collection.py')
    shutil.copyfile(vector_path, dst_dir / 'vector.py')

    for path in itype_dir.rglob("*.py"):
        shutil.copy(path, dst_dir)


def add_math_module(vector_path: Path, dst_dir: Path):
    shutil.copyfile(vector_path, dst_dir / 'Math.py')


def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))
    settings.CodeGenDstPath.ROOT.mkdir(exist_ok=True)

    copy_modules_from_enki(
        collection_path=settings.EnkiPaths.COLLECTION_MODULE,
        vector_path=settings.EnkiPaths.VECTOR_MODULE,
        itype_dir=settings.EnkiPaths.ITYPE_DIR,
        dst_dir=settings.CodeGenDstPath.ROOT
    )

    add_math_module(
        vector_path=settings.EnkiPaths.VECTOR_MODULE,
        dst_dir=settings.CodeGenDstPath.ROOT
    )

    if settings.ONLY_KBENGINE_API:
        return

    typesxml_parser = TypesXMLParser(settings.AssetsDirs.TYPES_XML_PATH)
    type_info_by_name = typesxml_parser.parse()

    exml_parser = EntitiesXMLParser(settings.AssetsDirs.ENTITIES_XML_PATH)
    exml_data = exml_parser.parse()

    edef_parser = EntityDefParser(settings.AssetsDirs.ENTITY_DEFS_DIR)
    edef_data = {
        ed.name: edef_parser.parse(ed.name) for ed in exml_data.get_all()
    }

    user_type_parser = UsetTypeParser(settings.AssetsDirs.USER_TYPE_DIR)
    user_type_infos = user_type_parser.parse()

    generate_types(
        type_info_by_name=type_info_by_name,
        user_type_infos=user_type_infos,
        dst_path=settings.CodeGenDstPath.TYPES
    )

    generate_entities(
        entity_defs_dir=settings.AssetsDirs.ENTITY_DEFS_DIR,
        dst_dir=settings.CodeGenDstPath.ENTITIES,
        type_info_by_name=type_info_by_name,
        user_type_infos=user_type_infos,
        edef_data=edef_data
    )


if __name__ == '__main__':
    main()
