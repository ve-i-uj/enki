"""Code generators.

Generate code by parsed data.
"""

import dataclasses
import functools
import logging
import pathlib
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import List

import jinja2

from enki.core import kbeenum
from enki.core import kbetype
from enki.misc import devonly

from tools.parsers import DefClassData, ParsedKBEngineXMLDC
from tools.egenerator import settings

from . import parser
from .parser import ParsedMethodDC
from . import settings

logger = logging.getLogger(__name__)


# TODO: [2022-11-07 13:15 burov_alexey@mail.ru]:
# Оставляю его пока здесь. Ошибки будут использоваться захардкоженные.
# Скорей всего скоро удалю совсем этот функционал.
@dataclass(frozen=True)
class ServerErrorDescr:
    """Description of server errors.

    It's a representation of server files server_errors_defaults.xml / server_errors.xml
    """
    id: int
    name: str
    desc: str


jinja_env = jinja2.Environment()

_APP_HEADER_TEMPLATE = '''"""Messages of {name}."""

from enki.core import kbetype, kbeenum, gedescr
'''

_APP_MSG_TEMPLATE = """
{short_name} = MsgDescr(
    id={id},
    lenght={lenght},
    name='{name}',
    args_type=kbeenum.{args_type},
    field_types={field_types},
    desc='{desc}'
)
"""

_SERVERERROR_HEADER_TEMPLATE = '''"""Server errors."""

from enki.core import gedescr
'''

_SERVERERROR_TEMPLATE = """
{name} = gedescr.ServerErrorDescr(
    id={id},
    name='{name}',
    desc='{desc}'
)
"""

_TYPE_HEADER_TEMPLATE = '''"""Generated types represent types of the file types.xml"""

import collections

from enki.core import kbetype
from enki.core import gedescr

'''

_TYPE_SPEC_TEMPLATE = """
{var_name} = gedescr.DataTypeDescr(
    id={id},
    base_type_name='{base_type_name}',
    name='{name}',
    module_name={module_name},
    pairs={pairs},
    of={of},
    kbetype={kbetype},
)
"""


def _to_string(msg_spec: parser.ParsedAppMessageDC):
    """Convert the message description to it string representation."""
    args_type = kbeenum.MsgArgsType(msg_spec.args_type)
    if not msg_spec.field_types:
        if args_type == kbeenum.MsgArgsType.VARIABLE:
            field_types = '(kbetype.UINT8_ARRAY, )'
        else:
            field_types = 'tuple()'
    else:
        field_types = '\n' + '\n'.join(
            f'        kbetype.{f.name},' for f in msg_spec.field_types)
        field_types = f'({field_types}\n    )'

    return _APP_MSG_TEMPLATE.format(
        short_name=msg_spec.name.split('::')[1],
        id=msg_spec.id,
        lenght=msg_spec.msg_len,
        name=msg_spec.name,
        args_type=str(kbeenum.MsgArgsType(msg_spec.args_type)),
        field_types=field_types,
        desc=msg_spec.desc
    )


def _chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


class AppMessagesCodeGen:

    def __init__(self, dst_path: pathlib.Path):
        # Root directory of modules contained app messages
        self._dst_path = dst_path
        self._dst_path.mkdir(parents=True, exist_ok=True)

    def generate(self, spec: List[parser.ParsedAppMessageDC]) -> None:
        # Filter specs by apps
        app_msg_specs = {
            'client': [],
            'loginapp': [],
            'baseapp': [],
        }
        for msg_spec in spec:
            if msg_spec.name.startswith('TCPClient'):
                app_msg_specs['client'].append(msg_spec)
            elif msg_spec.name.startswith('Loginapp'):
                app_msg_specs['loginapp'].append(msg_spec)
            elif msg_spec.name.startswith('Baseapp') \
                    or msg_spec.name.startswith('Entity'):
                app_msg_specs['baseapp'].append(msg_spec)
            else:
                raise devonly.LogicError(f'Unknown type of the message "{msg_spec}"')

        for app_name, msg_specs in app_msg_specs.items():
            dst_path = self._dst_path / app_name / '_generated.py'
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            with dst_path.open('w') as fh:
                fh.write(_APP_HEADER_TEMPLATE.format(name=app_name.capitalize()))
                for msg_spec in sorted(msg_specs, key=lambda s: s.id):
                    fh.write(_to_string(msg_spec))

                if app_name == 'client':
                    pairs = []
                    for msg_spec in sorted(msg_specs, key=lambda s: s.id):
                        short_name = msg_spec.short_name
                        pairs.append(f'    {short_name}.id: {short_name}')
                    spec_by_id_str = '\nSPEC_BY_ID = {\n%s\n}' % ',\n'.join(pairs)
                    fh.write(spec_by_id_str)
                    fh.write('\n')

                all_lines = []
                module_attrs = [f"'{s.short_name}'" for s in msg_specs]
                if app_name == 'client':
                    module_attrs.append("'SPEC_BY_ID'")
                for chunk in _chunker(module_attrs, 3):
                    all_lines.append('    ' + ', '.join(chunk))
                fh.write('\n__all__ = (\n%s\n)\n' % ',\n'.join(all_lines))

            logger.info(f'{app_name.capitalize()} messages have been written '
                        f'(dst file = "{dst_path}")')

        with (self._dst_path / '__init__.py').open('w') as fh:
            fh.write('from . import baseapp, client, loginapp')


class TypesCodeGen:

    def __init__(self, type_dst_path: pathlib.Path):
        self._type_dst_path = type_dst_path
        self._type_dst_path.parent.mkdir(parents=True, exist_ok=True)

    def generate(self, parsed_types: List[parser.ParsedTypeDC]) -> None:
        """Write code for types."""
        parsed_types[:] = self._reorder_types(parsed_types)
        type_by_id = {t.id: t for t in parsed_types}
        # assert type_count == len(parsed_types)
        with self._type_dst_path.open('w') as fh:
            fh.write(_TYPE_HEADER_TEMPLATE)
            for parsed_type in parsed_types:
                kwargs = dataclasses.asdict(parsed_type)

                if parsed_type.module_name is not None:
                    kwargs['module_name'] = f"'{parsed_type.module_name}'"

                kwargs['name'] = parsed_type.type_name

                # Prepare string representation of FD keys
                kwargs['pairs'] = None
                if parsed_type.is_fixed_dict:
                    new_pairs = []
                    assert parsed_type.fd_type_id_by_key is not None
                    for key, type_id in parsed_type.fd_type_id_by_key.items():
                        type_ = '%s_SPEC.kbetype' % type_by_id[type_id].type_name
                        new_pairs.append(f"        ('{key}', {type_})")
                    kwargs['pairs'] = 'collections.OrderedDict([\n%s\n    ])' % ',\n'.join(new_pairs)

                # Prepare string representation of Array
                kwargs['of'] = None
                if parsed_type.is_array:
                    assert parsed_type.arr_of_id is not None
                    kwargs['of'] = \
                        '%s_SPEC.kbetype' % type_by_id[parsed_type.arr_of_id].type_name

                kwargs['var_name'] = '%s_SPEC' % kwargs['name']

                # Form the field "decoder" string
                if parsed_type.base_type_name in kbetype.SIMPLE_TYPE_BY_NAME:
                    if parsed_type.is_alias:
                        kbetype_str = ("kbetype.{base_type_name}.alias('{name}')"
                                       ).format(**kwargs)
                    else:
                        kbetype_str = 'kbetype.{name}'.format(**kwargs)
                elif parsed_type.is_fixed_dict:
                    kbetype_str = ("kbetype.{base_type_name}.build('{name}', {pairs})"
                                   ).format(**kwargs)
                elif parsed_type.is_array:
                    kbetype_str = ("kbetype.{base_type_name}.build('{name}', {of})"
                                   ).format(**kwargs)
                else:
                    raise devonly.LogicError('Unexpected case')

                kwargs['kbetype'] = kbetype_str

                result = _TYPE_SPEC_TEMPLATE.format(**kwargs)
                new_lines = []
                for line in result.split('\n'):
                    if line.strip() in ('module_name=None,', 'pairs=None,',
                                        'of=None,'):
                        continue
                    new_lines.append(line)
                result = '\n'.join(new_lines)
                fh.write(result)

            pairs = []
            for parsed_type in sorted(parsed_types, key=lambda s: s.id):
                pairs.append(f'    {parsed_type.id}: {parsed_type.type_name}_SPEC')
            spec_by_id_str = '\nTYPE_SPEC_BY_ID = {\n%s\n}' % ',\n'.join(pairs)
            fh.write(spec_by_id_str)
            fh.write('\n')

            all_lines = []
            for chunk in _chunker(
                    [f"'{s.type_name}_SPEC'" for s in parsed_types] + ["'TYPE_SPEC_BY_ID'"], 3):
                all_lines.append('    ' + ', '.join(chunk))
            fh.write('\n__all__ = (\n%s\n)\n' % ',\n'.join(all_lines))

        with (self._type_dst_path.parent / '__init__.py').open('w') as fh:
            fh.write('from ._generated import *')

        logger.info(f'Server types have been written (dst file = "{self._type_dst_path}")')

    def _reorder_types(self, type_specs: List[parser.ParsedTypeDC]):
        """Reorder types that they can be referenced by each other."""
        new_type_specs = []
        # types that need reorder
        broken_type_specs = []
        for type_spec in type_specs:
            if type_spec.base_type_name in kbetype.SIMPLE_TYPE_BY_NAME:
                new_type_specs.append(type_spec)
                continue
            # Alias on FIXED_DICT or ARRAY cannot happen. Alias can refer on
            # a base kbe type.
            if type_spec.arr_of_id and type_spec.arr_of_id > type_spec.id:
                logger.warning('Unexpected behaviour (%s)', type_spec)
                broken_type_specs.append(type_spec)
                # TODO: [2022-08-01 23:07 burov_alexey@mail.ru]:
                # В type_spec.name будет '_BAG_values22_ArrayType'
                continue
                # raise devonly.LogicError('Unexpected behaviour')
            if type_spec.fd_type_id_by_key:
                # Check types of FD keys
                broken = False
                for type_id in type_spec.fd_type_id_by_key.values():
                    if type_id > type_spec.id:
                        broken = True
                        broken_type_specs.append(type_spec)
                        break
                if broken:
                    continue

            new_type_specs.append(type_spec)

        # TODO: [05.01.2021 16:45 burov_alexey@mail.ru]
        # What if broken type has referred to broken type too
        while broken_type_specs:
            type_spec = broken_type_specs[0]
            del broken_type_specs[0]
            if type_spec.is_fixed_dict:
                max_type_id = max(type_spec.fd_type_id_by_key.values())
            elif type_spec.is_array:
                max_type_id = type_spec.arr_of_id
            else:
                raise devonly.LogicError('Unexpected behaviour')
            # Insert this type after all declaration of its key types
            index = None
            for i, new_type_spec in enumerate(new_type_specs):
                if new_type_spec.id == max_type_id:
                    index = i
                    break
            else:
                broken_type_specs.append(type_spec)
                continue
            if index + 1 == len(new_type_specs):
                new_type_specs.append(type_spec)
            else:
                new_type_specs.insert(index + 1, type_spec)

        return new_type_specs


def get_python_type(deftype: ModuleType, typesxml_id: int) -> str:
    """Returns the python type of the property"""
    kbe_type = deftype.TYPE_SPEC_BY_ID[typesxml_id].kbetype
    if isinstance(kbe_type.default, kbetype.EnkiType):
        # It's an inner defined type
        python_type = f'{kbe_type.default.__class__.__name__}'
    else:
        # It's a built-in type of python
        python_type = type(kbe_type.default).__name__
    return python_type


def get_type_name(deftype: ModuleType, typesxml_id: int) -> str:
    type_spec = deftype.TYPE_SPEC_BY_ID[typesxml_id]
    type_name = type_spec.name if type_spec.name else type_spec.type_name
    return type_name


def get_default_value(deftype: ModuleType, typesxml_id: int) -> str:
    spec = deftype.TYPE_SPEC_BY_ID[typesxml_id]
    return f'deftype.{spec.name}_SPEC.kbetype.default'


def build_method_args(deftype: ModuleType, meth_dc: ParsedMethodDC, need_eid: bool = True) -> str:
    args = \
        ['self'] + (['entity_id: int'] if need_eid else []) + \
            [f'{get_type_name(deftype, t).lower()}_{i}: {get_python_type(deftype, t)}'
             for i, t in enumerate(meth_dc.arg_types)]
    return f',\n{" " * (9 + len(meth_dc.name))}'.join(args)


def build_args(deftype: ModuleType, meth_dc: ParsedMethodDC, need_brackets: bool = True) -> str:
    if len(meth_dc.arg_types) == 0:
        return '()' if need_brackets else ''
    args = \
        ', '.join(f'{get_type_name(deftype, t).lower()}_{i}' for i, t in enumerate(meth_dc.arg_types))
    return ('(%s, )' % args) if need_brackets else args


class EntitySerializersCodeGen:
    """Генерирует сириализаторы для RPC на сервер."""

    def __init__(self, eserializer_dst_path: pathlib.Path):
        self._eserializer_dst_path = eserializer_dst_path
        self._eserializer_dst_path.mkdir(parents=True, exist_ok=True)

    def generate(self, entities: List[parser.ParsedEntityDC],
                 assets_ent_data: dict[str, DefClassData],
                 assets_ent_c_data: dict[str, DefClassData],
                 deftype: ModuleType) -> None:
        """Write code for entities serializers."""

        jinja_env.globals.update(
            get_python_type=functools.partial(get_python_type, deftype),
            build_method_args=functools.partial(build_method_args, deftype),
            get_default_value=functools.partial(get_default_value, deftype),
            get_type_name=functools.partial(get_type_name, deftype),
            kbeenum=kbeenum
        )

        for entity_spec in entities:
            is_entity_component: bool = entity_spec.name in assets_ent_c_data
            if is_entity_component:
                ec_type_by_name: dict[str, str] = {}
                dst_path = self._eserializer_dst_path / 'components'
                template_path = settings.JINJA_TEMPLS_DIR / 'eserializer' / 'ecserializer.py.jinja'
            else:
                ec_type_by_name: dict[str, str] = {
                    d.name: d.type for d in assets_ent_data[entity_spec.name].Components
                }
                dst_path = self._eserializer_dst_path
                # TODO: [2022-11-12 08:46 burov_alexey@mail.ru]:
                # В настройки
                template_path = settings.JINJA_TEMPLS_DIR / 'eserializer' / 'eserializer.py.jinja'

            dst_path.mkdir(exist_ok=True)
            with (dst_path / f'{entity_spec.name}.py').open('w') as fh:
                with open(template_path) as tmpl_fh:
                    template = jinja_env.from_string(tmpl_fh.read())
                fh.write(template.render(
                    entity_spec=entity_spec,
                    assets_ent_data=assets_ent_data,
                    ec_type_by_name=ec_type_by_name,
                    assets_ent_c_data=assets_ent_c_data
                ))

        ec_types_by_ename = {}
        for entity_spec in entities:
            if entity_spec.name not in assets_ent_data:
                continue
            ec_types_by_ename[entity_spec.name] = {}
            for d in assets_ent_data[entity_spec.name].Components:
                ec_types_by_ename[entity_spec.name][d.name] = d.type

        with (self._eserializer_dst_path / '__init__.py').open('w') as fh:
            # TODO: [2022-11-12 11:54 burov_alexey@mail.ru]:
            # В настройки
            with open(settings.JINJA_TEMPLS_DIR / 'eserializer' / 'eserializer_init_module.py.jinja') as tmpl_fh:
                template = jinja_env.from_string(tmpl_fh.read())
            fh.write(template.render(
                entities=entities,
                assets_ent_c_data=assets_ent_c_data,
            ))

        (self._eserializer_dst_path / 'components').mkdir(exist_ok=True)
        with (self._eserializer_dst_path / 'components' / '__init__.py').open('w') as fh:
            pass

        with (self._eserializer_dst_path.parent / '__init__.py').open('w') as fh:
            fh.write('from ._generated import *')

        logger.info(f'Entities have been written (dst file = '
                    f'"{self._eserializer_dst_path}")')


class EntitiesCodeGen:

    def __init__(self, entity_dst_path: pathlib.Path):
        self._entity_dst_path = entity_dst_path
        self._entity_dst_path.mkdir(parents=True, exist_ok=True)

    def generate(self, entities: List[parser.ParsedEntityDC],
                 assets_ent_data: dict[str, DefClassData],
                 assets_ent_c_data: dict[str, DefClassData],
                 deftype: ModuleType) -> None:
        """Write code for entities."""

        jinja_env.globals.update(
            get_python_type=functools.partial(get_python_type, deftype),
            build_method_args=functools.partial(build_method_args, deftype),
            build_args=functools.partial(build_args, deftype),
            get_default_value=functools.partial(get_default_value, deftype),
            get_type_name=functools.partial(get_type_name, deftype),
            kbeenum=kbeenum
        )

        for entity_spec in entities:
            is_entity_component: bool = entity_spec.name in assets_ent_c_data
            if is_entity_component:
                ec_type_by_name: dict[str, str] = {}
                dst_path = self._entity_dst_path / 'components'
                template_path = settings.JINJA_TEMPLS_DIR / 'gameentity' / 'entity_component.py.jinja'
            else:
                ec_type_by_name: dict[str, str] = {
                    d.name: d.type for d in assets_ent_data[entity_spec.name].Components
                }
                dst_path = self._entity_dst_path
                # TODO: [2022-11-12 08:46 burov_alexey@mail.ru]:
                # В настройки
                template_path = settings.JINJA_TEMPLS_DIR / 'gameentity' / 'entity.py.jinja'

            dst_path.mkdir(exist_ok=True)
            with (dst_path / f'{entity_spec.name}.py').open('w') as fh:
                with open(template_path) as tmpl_fh:
                    template = jinja_env.from_string(tmpl_fh.read())
                fh.write(template.render(
                    entity_spec=entity_spec,
                    assets_ent_data=assets_ent_data,
                    ec_type_by_name=ec_type_by_name,
                    assets_ent_c_data=assets_ent_c_data
                ))

        ec_types_by_ename = {}
        for entity_spec in entities:
            if entity_spec.name not in assets_ent_data:
                continue
            ec_types_by_ename[entity_spec.name] = {}
            for d in assets_ent_data[entity_spec.name].Components:
                ec_types_by_ename[entity_spec.name][d.name] = d.type

        with (settings.CodeGenDstPath.ROOT / 'description.py').open('w') as fh:
            with open(settings.JINJA_TEMPLS_DIR / 'gameentity' / 'description.py.jinja') as tmpl_fh:
                template = jinja_env.from_string(tmpl_fh.read())
            fh.write(template.render(
                entities=entities,
                ec_types_by_ename=ec_types_by_ename,
                assets_ent_c_data=assets_ent_c_data,
            ))

        with (self._entity_dst_path / '__init__.py').open('w') as fh:
            with open(settings.JINJA_TEMPLS_DIR / 'gameentity' / 'entity_init_module.py.jinja') as tmpl_fh:
                template = jinja_env.from_string(tmpl_fh.read())
            fh.write(template.render(
                entities=entities,
                assets_ent_c_data=assets_ent_c_data,
            ))

        (self._entity_dst_path / 'components').mkdir(exist_ok=True)
        with (self._entity_dst_path / 'components' / '__init__.py').open('w') as fh:
            pass

        with (self._entity_dst_path.parent / '__init__.py').open('w') as fh:
            fh.write('from ._generated import *')

        logger.info(f'Entities have been written (dst file = '
                    f'"{self._entity_dst_path}")')


class ErrorCodeGen:

    def __init__(self, dst_path: pathlib.Path):
        self._dst_path = dst_path
        self._dst_path.parent.mkdir(parents=True, exist_ok=True)

    def generate(self, spec: List[parser.ParsedServerErrorDC]) -> None:
        with self._dst_path.open('w') as fh:
            fh.write(_SERVERERROR_HEADER_TEMPLATE)

            for error_spec in spec:
                fh.write(
                    _SERVERERROR_TEMPLATE.format(**dataclasses.asdict(error_spec)))

            pairs = []
            for error_spec in sorted(spec, key=lambda s: s.id):
                pairs.append(f'    {error_spec.id}: {error_spec.name}')
            spec_by_id_str = '\nERROR_BY_ID = {\n%s\n}' % ',\n'.join(pairs)
            fh.write(spec_by_id_str)
            fh.write('\n')

            all_lines = []
            for chunk in _chunker(
                    [f"'{s.name}'" for s in spec] + ["'ERROR_BY_ID'"], 2):
                all_lines.append('    ' + ', '.join(chunk))
            fh.write('\n__all__ = (\n%s\n)\n' % ',\n'.join(all_lines))

        logger.info(f'Server errors have been written (dst file = '
                    f'"{self._dst_path}")')


class KBEngineXMLDataCodeGen:

    def __init__(self, entity_dst_path: pathlib.Path):
        self._entity_dst_path = entity_dst_path
        self._entity_dst_path.parent.mkdir(parents=True, exist_ok=True)

    def generate(self, config_dc: ParsedKBEngineXMLDC):
        with (self._entity_dst_path).open('w') as fh:
            with open(settings.JINJA_TEMPLS_DIR / 'kbenginexml.py.jinja') as tmpl_fh:
                template = jinja_env.from_string(tmpl_fh.read())
            fh.write(template.render(
                root=config_dc.root
            ))
