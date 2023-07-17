"""Парсер пользовательских типов-конвертеров (директории assets/scripts/user_type)."""


import collections
import importlib
import inspect
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from enki.misc import devonly

logger = logging.getLogger(__name__)


ModuleName = str
ConverterName = str

@dataclass
class ConverterInfo:
    name: ConverterName
    fd_type: str
    obj_type: str


@dataclass
class UserTypeInfo:
    module_name: str
    converter_info: ConverterInfo

UserTypeInfos = dict[ModuleName, dict[ConverterName, UserTypeInfo]]


class UsetTypeParser:
    """Парсер для папки user_type (пользовательские конвертеры для FD)."""

    def __init__(self, user_type_dir: Path) -> None:
        assert user_type_dir.exists()
        self._user_type_dir = user_type_dir

    def parse(self) -> UserTypeInfos:
        logger.debug('(%s)', devonly.func_args_values())
        sys.path.append(str(self._user_type_dir))
        sys.path.append(str((self._user_type_dir.parent / 'server_common').absolute()))
        sys.path.append(str((self._user_type_dir.parent / 'common').absolute()))
        res: UserTypeInfos = collections.defaultdict(dict)
        for path in self._user_type_dir.rglob("*.py"):
            module = importlib.import_module(path.stem)
            for attr_name in dir(module):
                if attr_name.startswith('__'):
                    continue
                attr = getattr(module, attr_name)
                if not hasattr(attr, 'createObjFromDict') \
                        or not hasattr(attr, 'getDictFromObj') \
                        or not hasattr(attr, 'isSameType'):
                    continue

                # Это скорей всего конвертер, т.к. он обладает нужными методами.
                # Конвертерами с нужными методами может быть или экземпляр,
                # или метод класса, или статический метод. Теперь нужно проверить
                # сигнатуры методов.

                signs = {
                    'createObjFromDict': inspect.signature(attr.createObjFromDict),
                    'getDictFromObj': inspect.signature(attr.getDictFromObj),
                    'isSameType': inspect.signature(attr.isSameType),
                }
                oks = {
                    'createObjFromDict': False,
                    'getDictFromObj': False,
                    'isSameType': False,
                }
                for method_name, sign in signs.items():
                    if isinstance(attr, type):
                        # Этот атрибут - это класс
                        cls = attr
                        if isinstance(cls.__dict__.get(method_name), classmethod) \
                                and len(sign.parameters) == 1:
                            # Это метод класса с одним параметром - ОК
                            oks[method_name] = True
                        elif isinstance(cls.__dict__.get(method_name), staticmethod) \
                                and len(sign.parameters) == 1:
                            # Это статический метод с одним параметром - ОК
                            oks[method_name] = True
                        else:
                            # Других вариантов для класса нет
                            oks[method_name] = False
                    elif isinstance(attr, object):
                        # Этот атрибут - экземпляр класса
                        if len(sign.parameters) == 1:
                            # Это метод с одним параметром - ОК
                            oks[method_name] = True
                        else:
                            oks[method_name] = False

                if all(oks.values()):
                    converter_info = ConverterInfo(
                        name=attr_name,
                        fd_type='Any',
                        obj_type='Any'
                    )
                    for method_name, sign in signs.items():
                        if method_name == 'isSameType':
                            continue
                        elif method_name == 'createObjFromDict':
                            type_or_name = list(sign.parameters.values())[0].annotation
                            if isinstance(type_or_name, str):
                                fd_type = type_or_name
                            else:
                                fd_type = type_or_name.__name__
                            if converter_info.fd_type == 'Any' and fd_type != '_empty':
                                converter_info.fd_type = fd_type
                            type_or_name = sign.return_annotation
                            if isinstance(type_or_name, str):
                                obj_type = type_or_name
                            else:
                                obj_type = type_or_name.__name__
                            if converter_info.obj_type == 'Any' and obj_type != '_empty':
                                converter_info.obj_type = obj_type
                        elif method_name == 'getDictFromObj':
                            type_or_name = sign.return_annotation
                            if isinstance(type_or_name, str):
                                fd_type = type_or_name
                            else:
                                fd_type = type_or_name.__name__
                            if converter_info.fd_type == 'Any' and fd_type != '_empty':
                                converter_info.fd_type = fd_type
                            type_or_name = list(sign.parameters.values())[0].annotation
                            if isinstance(type_or_name, str):
                                obj_type = type_or_name
                            else:
                                obj_type = type_or_name.__name__
                            if converter_info.obj_type == 'Any' and obj_type != '_empty':
                                converter_info.obj_type = obj_type

                        if converter_info.fd_type != 'Any' and converter_info.obj_type != 'Any':
                            break

                        # Если не получилось узнать типы из первого метода,
                        # попробуем вычислить их из остальных.

                    res[module.__name__][converter_info.name] = UserTypeInfo(
                        module_name=module.__name__,
                        converter_info=converter_info
                    )

                # Вывожу предупреждение, если есть попытка сделать конвертер,
                # но у него не правильная сигнатура
                for method_name, ok in oks.items():
                    if not ok:
                        logger.warning(
                            f'The converter class "{attr_name}" has invalid'
                            f'singature of the method "{method_name}"'
                        )

        return res
