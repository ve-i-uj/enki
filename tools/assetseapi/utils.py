"""Утилиты для помощи генератору API серверных сущностей."""

from tools.parsers.entitydef import MethodData
from tools.parsers import AssetsTypeInfoByName


def build_method_args(method_data: MethodData, type_info_by_name: AssetsTypeInfoByName) -> str:
    """Генерирует строку аргументов для переданного метода."""
    args = ['self']
    if method_data.exposed:
        args.append('entity_caller_id: int')
    for i, arg_data in enumerate(method_data.args):
        type_info = type_info_by_name[arg_data.def_type]
        if type_info.converter is not None:
            py_type_name = type_info.converter.split('.')[1]
        else:
            py_type_name = type_info_by_name[arg_data.def_type].py_type_name
        if arg_data.comment is not None:
            args.append(f'{arg_data.comment}: {py_type_name}')
        else:
            args.append(f'arg_{i}: {py_type_name}')
    return f',\n{" " * (9 + len(method_data.name))}'.join(args)
