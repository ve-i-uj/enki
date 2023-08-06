"""Точка входа для генератора API серверных сущностей."""

import builtins
import copy
import functools
import logging
import shutil
from pathlib import Path

import jinja2

from enki.misc import log

from tools.assetsapi import settings
from tools.parsers import TypesXMLParser
from tools.parsers.entitiesxml import EntitiesXMLParser
from tools.parsers.entitydef import DefClassData, EntityDefParser
from tools.parsers.typesxml import AssetsTypeInfoByName

from tools.assetsapi import utils
from tools.parsers.usertype import UserTypeInfos, UsetTypeParser


def _generate_types(type_info_by_name: AssetsTypeInfoByName,
                   user_type_infos: UserTypeInfos, dst_path: Path):
    with settings.Templates.TYPESXML_JINJA_TEMPLATE_PATH.open('r') as fh:
        jinja_entity_template = fh.read()
    jinja_env = jinja2.Environment()
    template = jinja_env.from_string(jinja_entity_template)
    types_text = template.render(
        type_info_by_name=type_info_by_name,
        user_type_infos=user_type_infos,
        is_converter_fds=False
    )
    with dst_path.open('w') as fh:
        fh.write(types_text)


def _generate_entities(dst_dir: Path,
                       type_info_by_name: AssetsTypeInfoByName,
                       user_type_infos: UserTypeInfos,
                       entities_def_data: dict[str, DefClassData],
                       proxy_entities_list: list[str]):
    with settings.Templates.ENTITY_JINJA_TEMPLATE_PATH.open('r') as fh:
        jinja_entity_template = fh.read()
    jinja_env = jinja2.Environment()
    template = jinja_env.from_string(jinja_entity_template)
    dst_dir.mkdir(exist_ok=True)
    for entity_name, entity_info in entities_def_data.items():
        entity_text = template.render(
            type_info_by_name=type_info_by_name,
            entity_info=entity_info,
            build_method_args=functools.partial(
                utils.build_method_args, user_type_infos=user_type_infos
            ),
            proxy_entities_list=proxy_entities_list
        )
        with (dst_dir / f'{entity_name.lower()}.py').open('w') as fh:
            fh.write(entity_text)


def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))

    if settings.CodeGenDstPath.ASSETSAPI_DIR.exists():
        shutil.rmtree(settings.CodeGenDstPath.ASSETSAPI_DIR)
    shutil.copytree(
        settings.EnkiPaths.ASSETSAPI_FOR_COPY_DIR,
        settings.CodeGenDstPath.ASSETSAPI_DIR
    )

    if settings.ONLY_KBENGINE_API:
        return

    if settings.ADD_ASSETSTOOLS:
        if settings.CodeGenDstPath.ASSETSTOOLS_DIR.exists():
            shutil.rmtree(settings.CodeGenDstPath.ASSETSTOOLS_DIR)
        shutil.copytree(
            settings.EnkiPaths.ASSETSTOOLS_FOR_COPY_DIR,
            settings.CodeGenDstPath.ASSETSTOOLS_DIR
        )

    typesxml_parser = TypesXMLParser(settings.AssetsDirs.TYPES_XML_PATH)
    type_info_by_name = typesxml_parser.parse()

    exml_parser = EntitiesXMLParser(settings.AssetsDirs.ENTITIES_XML_PATH)
    exml_data = exml_parser.parse()

    edef_parser = EntityDefParser(settings.AssetsDirs.ENTITY_DEFS_DIR)
    entities_def_data = {
        ed.name: edef_parser.parse(ed.name) for ed in exml_data.get_all()
    }

    # Здесь нужно сгенерировать модуль-заглушку `assetsapi.user_type` (см. README)
    settings.CodeGenDstPath.USER_TYPE_DIR.mkdir(exist_ok=True)
    with settings.CodeGenDstPath.USER_TYPE_INIT.open('w') as fh:
        fh.write('from typing import Dict\n')
        for info in (i for i in type_info_by_name.values() if i.converter is not None):
            fh.write(f'{info.py_type_name}FD = Dict\n')

    # Теперь, когда есть заглушка, можно считывать модули из user_type

    user_type_parser = UsetTypeParser(settings.AssetsDirs.USER_TYPE_DIR)
    user_type_infos = user_type_parser.parse()

    _generate_types(
        type_info_by_name=type_info_by_name,
        user_type_infos=user_type_infos,
        dst_path=settings.CodeGenDstPath.TYPESXML
    )

    _generate_entities(
        dst_dir=settings.CodeGenDstPath.ENTITIES,
        type_info_by_name=type_info_by_name,
        user_type_infos=user_type_infos,
        entities_def_data=entities_def_data,
        proxy_entities_list=settings.PROXY_ENTITIES
    )

    # Теперь сгенерируем интерфейсы сущностей из папки scripts/entity_defs/interfaces

    # Нужно собрать все интерфейсы из всех сущностей
    interfaces_data: dict[str, DefClassData] = {}
    for data in entities_def_data.values():
        if data.Interfaces:
            for i_data in data.Interfaces:
                interfaces_data[i_data.name] = i_data

    # И отдать их на генерацию, как простые сущности, только в другую папку
    _generate_entities(
        dst_dir=settings.CodeGenDstPath.INTERFACES,
        type_info_by_name=type_info_by_name,
        user_type_infos=user_type_infos,
        entities_def_data=interfaces_data,
        proxy_entities_list=[]
    )

    # А это генерация описаний FIXED_DICT с конвертерами, чтобы использовать
    # их в аннотациях в user_type.
    new_type_info_by_name = copy.deepcopy(type_info_by_name)
    new_types = {}
    for info in (i for i in new_type_info_by_name.values() if i.converter is not None):
        # Нужно "отключить" конвертер у FD, чтобы не было импорта из user_type.
        # Но важно так же сохранить этот тип, т.к. на него будут ссылаться
        # описания других типов.
        info.converter = None
        # И нужно добавить "новый" тип, чтобы его можно было использовать в user_type
        new_type_info = copy.deepcopy(info)
        new_type_info.py_type_name = f'{info.py_type_name}FD'
        new_types[new_type_info.py_type_name] = new_type_info
    new_type_info_by_name.update(new_types)

    with settings.Templates.TYPESXML_JINJA_TEMPLATE_PATH.open('r') as fh:
        jinja_entity_template = fh.read()
    jinja_env = jinja2.Environment()
    template = jinja_env.from_string(jinja_entity_template)
    types_text = template.render(
        type_info_by_name=new_type_info_by_name,
        user_type_infos=user_type_infos,
        is_converter_fds=True
    )
    with settings.CodeGenDstPath.TYPESXML_WITHOUT_CONVERTERS.open('w') as fh:
        fh.write(types_text)

    with settings.Templates.USER_TYPE_PATH.open('r') as fh:
        jinja_entity_template = fh.read()
    jinja_env = jinja2.Environment()
    template = jinja_env.from_string(jinja_entity_template)
    builtin_types= [
        t.__name__ for t in builtins.__dict__.values() if isinstance(t, type)
    ]
    text = template.render(
        type_names=sorted(set(
            i.py_type_name for i in new_type_info_by_name.values()
            if i.py_type_name not in builtin_types
        ))
    )
    with settings.CodeGenDstPath.USER_TYPE_INIT.open('w') as fh:
        fh.write(text)


if __name__ == '__main__':
    main()
