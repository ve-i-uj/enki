"""Точка входа для генератора API серверных сущностей."""

import builtins
import collections
import copy
from dataclasses import dataclass
import functools
import logging
import shutil
from pathlib import Path
from typing import Tuple

import jinja2

from enki.misc import log

from tools.assetsapi import settings
from tools.parsers import TypesXMLParser
from tools.parsers.entitiesxml import EntitiesXMLParser
from tools.parsers.entitydef import DefClassData, EntityComponentData, EntityDefParser
from tools.parsers.typesxml import AssetsTypeInfoByName

from tools.assetsapi import utils
from tools.parsers.usertype import UserTypeInfo, UserTypeInfos, UsetTypeParser


ComponentOwnerTypeName = str
ComponentAttrName = str
ComponentTypeName = str


@dataclass
class ComponentData:
    owner_name: ComponentOwnerTypeName
    component_attr_name: ComponentAttrName
    def_cls_data: DefClassData


ComponentsData = dict[ComponentOwnerTypeName, list[ComponentData]]


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
                       proxy_entities_list: list[str],
                       components_data_by_entity_name: ComponentsData,
                       is_interfaces: bool = False):
    with settings.Templates.ENTITY_JINJA_TEMPLATE_PATH.open('r') as fh:
        jinja_entity_template = fh.read()
    jinja_env = jinja2.Environment()
    template = jinja_env.from_string(jinja_entity_template)
    dst_dir.mkdir(exist_ok=True)
    for entity_name, entity_info in entities_def_data.items():
        components_data = components_data_by_entity_name[entity_name]
        comp_names_by_comp_type_name = collections.defaultdict(str)
        comp_info_by_comp_type_name: dict[str, ComponentData] = {}
        for comp_info in components_data:
            if not comp_names_by_comp_type_name[comp_info.def_cls_data.name]:
                comp_names_by_comp_type_name[comp_info.def_cls_data.name] = f'"{comp_info.component_attr_name}"'
            else:
                comp_names_by_comp_type_name[comp_info.def_cls_data.name] += f' or "{comp_info.component_attr_name}"'
            comp_info_by_comp_type_name[comp_info.def_cls_data.name] = comp_info

        entity_text = template.render(
            type_info_by_name=type_info_by_name,
            entity_info=entity_info,
            build_method_args=functools.partial(
                utils.build_method_args, user_type_infos=user_type_infos,
                use_def_comments_like_params=settings.USE_DEF_COMMENTS_LIKE_PARAMS
            ),
            component_types=sorted(set([info.type for info in entity_info.Components])),
            comp_info_by_comp_type_name=comp_info_by_comp_type_name,
            comp_names_by_comp_type_name=comp_names_by_comp_type_name,
            is_interfaces=is_interfaces,
            is_proxy_entity=(entity_info.name in proxy_entities_list)
        )
        with (dst_dir / f'{entity_name.lower()}.py').open('w') as fh:
            fh.write(entity_text)


def _generate_components(dst_dir: Path,
                         type_info_by_name: AssetsTypeInfoByName,
                         user_type_infos: UserTypeInfos,
                         components_data: dict[ComponentTypeName, ComponentData]):
    with settings.Templates.COMPONENT_JINJA_TEMPLATE_PATH.open('r') as fh:
        jinja_entity_template = fh.read()
    jinja_env = jinja2.Environment()
    template = jinja_env.from_string(jinja_entity_template)
    dst_dir.mkdir(exist_ok=True)
    for component_name, component_info in components_data.items():
        entity_text = template.render(
            type_info_by_name=type_info_by_name,
            entity_info=component_info.def_cls_data,
            build_method_args=functools.partial(
                utils.build_method_args, user_type_infos=user_type_infos,
                use_def_comments_like_params=settings.USE_DEF_COMMENTS_LIKE_PARAMS
            ),
            proxy_entities_list=[]
        )
        with (dst_dir / f'{component_name.lower()}.py').open('w') as fh:
            fh.write(entity_text)


def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))

    if settings.CodeGenDstPath.ASSETSAPI_DIR.exists():
        shutil.rmtree(settings.CodeGenDstPath.ASSETSAPI_DIR)
    shutil.copytree(
        settings.EnkiPaths.ASSETSAPI_FOR_COPY_DIR,
        settings.CodeGenDstPath.ASSETSAPI_DIR
    )

    if settings.ADD_TYPING_EXTENSIONS_LIB:
        shutil.copy(
            settings.EnkiPaths.TYPING_EXTENSIONS_PATH,
            settings.CodeGenDstPath.TYPING_EXTENSIONS_PATH
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

    # Собираем все компоненты, которые подключены к сущностям

    components_data: ComponentsData = collections.defaultdict(list)
    component_type_infos = {}
    entity_def_parser = EntityDefParser(settings.AssetsDirs.ENTITY_DEFS_COMPONENT_DIR)
    for entity_data in entities_def_data.values():
        for c_data in entity_data.Components:
            if c_data.type not in components_data:
                comp_info = ComponentData(
                    c_data.type,  c_data.name, entity_def_parser.parse(c_data.type)
                )
                components_data[entity_data.name].append(comp_info)
                component_type_infos[c_data.type] = comp_info

    # Здесь нужно сгенерировать модуль-заглушку `assetsapi.user_type` (см. README)

    settings.CodeGenDstPath.USER_TYPE_DIR.mkdir(exist_ok=True)
    with settings.CodeGenDstPath.USER_TYPE_INIT.open('w') as fh:
        fh.write('from typing import Dict\n')
        for info in (i for i in type_info_by_name.values() if i.converter is not None):
            fh.write(f'{info.py_type_name}FD = Dict\n')

    # Теперь, когда есть заглушка, можно считывать модули из user_type

    site_packages_dir = None
    if settings.SITE_PACKAGES_DIR is not None:
        site_packages_dir = settings.SITE_PACKAGES_DIR
    user_type_parser = UsetTypeParser(settings.AssetsDirs.USER_TYPE_DIR,
                                      site_packages_dir)
    user_type_infos: dict[str, dict[str, UserTypeInfo]] = user_type_parser.parse()

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
        proxy_entities_list=settings.PROXY_ENTITIES,
        components_data_by_entity_name=components_data
    )

    # Теперь сгенерируем интерфейсы сущностей из папки scripts/entity_defs/interfaces

    # Нужно собрать все интерфейсы из всех сущностей
    interfaces_data: dict[str, DefClassData] = {}
    for entity_data in entities_def_data.values():
        for i_data in entity_data.Interfaces:
            interfaces_data[i_data.name] = i_data

    # И отдать их на генерацию, как простые сущности, только в другую папку
    _generate_entities(
        dst_dir=settings.CodeGenDstPath.INTERFACES,
        type_info_by_name=type_info_by_name,
        user_type_infos=user_type_infos,
        entities_def_data=interfaces_data,
        proxy_entities_list=[],
        components_data_by_entity_name=components_data,
        is_interfaces=True
    )

    _generate_components(
        dst_dir=settings.CodeGenDstPath.COMPONENTS,
        type_info_by_name=type_info_by_name,
        user_type_infos=user_type_infos,
        components_data=component_type_infos,
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
    builtin_types = [
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
