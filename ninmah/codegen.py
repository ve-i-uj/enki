"""Code generators.

Generate code by parsed data.
"""

import abc
import dataclasses
import logging
import pathlib
from typing import List, Any, Tuple

from enki import message, kbetype, kbeclient
from enki.misc import devonly

from . import parser


logger = logging.getLogger(__name__)

_APP_HEADER_TEMPLATE = '''"""Messages of {name}."""

from enki import message, kbetype
'''

_MSG_TEMPLATE = """
{short_name} = message.MessageSpec(
    id={id},
    name='{name}',
    args_type=message.{args_type},
    field_types={field_types},
    desc='{desc}'
)
"""

_SERVERERROR_HEADER_TEMPLATE = '''"""Server errors."""

from . import _servererror
'''

_SERVERERROR_TEMPLATE = """
{name} = _servererror.ServerErrorSpec(
    id={id},
    name='{name}',
    desc='{desc}'
)
"""

_DEF_HEADER_TEMPLATE = '''"""Generated types represent types of the file types.xml"""

from enki import kbetype
from . import _deftype

'''

_TYPE_SPEC_TEMPLATE = """
{var_name} = _deftype.DataTypeSpec(
    id={id},
    base_type_name='{base_type_name}',
    name='{name}',    
    module_name={module_name},
    pairs={pairs},
    of={of},
)"""

_SIMPLE_TYPE_TEMPLATE = """
{name} = kbetype.{name}
"""

_TYPE_ALIAS_TEMPLATE = """
{name} = kbetype.{base_type_name}.alias('{name}')
"""

_FD_TYPE_TEMPLATE = """
{name} = kbetype.{base_type_name}.build({var_name}.name, {var_name}.pairs)
"""

_ARRAY_TYPE_TEMPLATE = """
{name} = kbetype.{base_type_name}.build({var_name}.name, {var_name}.of)
"""

_ENTITY_HEADER = '''"""Generated classes represent entity of the file entities.xml"""

import logging

from . import _entity
from .. import deftype

from enki.misc import devonly

logger = logging.getLogger(__name__)

'''

_ENTITY_TEMPLATE = """
class {name}(_entity.Entity):
    ID = {entity_id}
"""

_ENTITY_PROPERTY_TEMPLATE = """
    @property
    def {name}(self) -> deftype.{type_name}:
        return deftype.{type_name}.default
"""

_ENTITY_METHOD_TEMPLATE = """
    def {name}({args}):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
"""

_ENTITY_ARGS_TEMPLATE = '{arg}: deftype.{type_name}'


def _to_string(msg_spec: message.MessageSpec):
    """Convert a message to it string representation."""
    if not msg_spec.field_types:
        field_types = 'tuple()'
    else:
        field_types = '\n' + '\n'.join(
            f'        kbetype.{f.name},' for f in msg_spec.field_types)
        field_types = f'({field_types}\n    )'

    return _MSG_TEMPLATE.format(
        short_name=msg_spec.name.split('::')[1],
        id=msg_spec.id,
        name=msg_spec.name,
        args_type=str(msg_spec.args_type),
        field_types=field_types,
        desc=msg_spec.desc
    )


def _chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


class AppMessagesCodeGen:

    def __init__(self, dst_path: pathlib.Path):
        # Root directory of modules contained app messages
        self._dst_path = dst_path
        self._dst_path.parent.mkdir(parents=True, exist_ok=True)

    def generate(self, spec: List[message.MessageSpec]):
        # Filter specs by apps
        app_msg_specs = {
            'client': [],
            'loginapp': [],
            'baseapp': [],
        }
        for msg_spec in spec:
            if msg_spec.name.startswith('Client'):
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


class TypesCodeGen:

    def __init__(self, type_dst_path: pathlib.Path):
        self._type_dst_path = type_dst_path
        self._type_dst_path.parent.mkdir(parents=True, exist_ok=True)

    def generate(self, parsed_types: List[parser.ParsedTypeData]):
        """Write code for types."""
        type_count = len(parsed_types)
        parsed_types[:] = self._reorder_types(parsed_types)
        type_by_id = {t.id: t for t in parsed_types}
        assert type_count == len(parsed_types)
        with self._type_dst_path.open('w') as fh:
            fh.write(_DEF_HEADER_TEMPLATE)
            for parsed_type in parsed_types:
                kwargs = dataclasses.asdict(parsed_type)

                if parsed_type.module_name is not None:
                    kwargs['module_name'] = f"'{parsed_type.module_name}'"

                kwargs['name'] = parsed_type.type_name

                # Prepare string representation of FD keys
                kwargs['pairs'] = None
                if parsed_type.is_fixed_dict:
                    new_pairs = []
                    for key, type_id in parsed_type.fd_type_id_by_key.items():
                        type_ = type_by_id[type_id].type_name
                        new_pairs.append(f"        '{key}': {type_}")
                    kwargs['pairs'] = '{\n%s\n    }' % ',\n'.join(new_pairs)

                # Prepare string representation of Array
                kwargs['of'] = None
                if parsed_type.is_array:
                    kwargs['of'] = type_by_id[parsed_type.arr_of_id].name

                kwargs['var_name'] = '_%s_SPEC' % kwargs['name']

                result = _TYPE_SPEC_TEMPLATE.format(**kwargs)
                new_lines = []
                for line in result.split('\n'):
                    if line.strip() in ('module_name=None,', 'pairs=None,',
                                        'of=None,'):
                        continue
                    new_lines.append(line)
                result = '\n'.join(new_lines)
                fh.write(result)
                if parsed_type.base_type_name in kbetype.SIMPLE_TYPE_BY_NAME:
                    if parsed_type.is_alias:
                        fh.write(_TYPE_ALIAS_TEMPLATE.format(**kwargs))
                    else:
                        fh.write(_SIMPLE_TYPE_TEMPLATE.format(**kwargs))
                elif parsed_type.is_fixed_dict:
                    fh.write(_FD_TYPE_TEMPLATE.format(**kwargs))
                elif parsed_type.is_array:
                    fh.write(_ARRAY_TYPE_TEMPLATE.format(**kwargs))
                else:
                    raise devonly.LogicError('Unexpected case')

            pairs = []
            for parsed_type in sorted(parsed_types, key=lambda s: s.id):
                pairs.append(f'    {parsed_type.id}: {parsed_type.type_name}')
            spec_by_id_str = '\nTYPE_BY_ID = {\n%s\n}' % ',\n'.join(pairs)
            fh.write(spec_by_id_str)
            fh.write('\n')

            all_lines = []
            for chunk in _chunker(
                    [f"'{s.type_name}'" for s in parsed_types] + ["'TYPE_BY_ID'"], 3):
                all_lines.append('    ' + ', '.join(chunk))
            fh.write('\n__all__ = (\n%s\n)\n' % ',\n'.join(all_lines))

        logger.info(f'Server types have been written (dst file = "{self._type_dst_path}")')

    def _reorder_types(self, type_specs: List[parser.ParsedTypeData]):
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
                raise devonly.LogicError('Unexpected behaviour')
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
        for type_spec in broken_type_specs:
            assert type_spec.fd_type_id_by_key
            max_type_id = max(type_spec.fd_type_id_by_key.values())
            # Insert this type after all declaration of its key types
            index = None
            for i, new_type_spec in enumerate(new_type_specs):
                if new_type_spec.id > max_type_id:
                    index = i
                    break
            new_type_specs.insert(index, type_spec)

        return new_type_specs


class EntitiesCodeGen:

    def __init__(self, entity_dst_path: pathlib.Path):
        self._entity_dst_path = entity_dst_path
        self._entity_dst_path.parent.mkdir(parents=True, exist_ok=True)

    def generate(self, entities: List[parser.ParsedEntityData],
                 types: List[parser.ParsedTypeData]):
        """Write code for entities."""
        type_name_by_id = {t.id: (t.name if t.name else t.type_name)
                           for t in types}

        with self._entity_dst_path.open('w') as fh:
            fh.write(_ENTITY_HEADER)
            for entity_spec in entities:
                fh.write(_ENTITY_TEMPLATE.format(name=entity_spec.name,
                                                 entity_id=entity_spec.uid))
                for prop in entity_spec.properties:
                    fh.write(_ENTITY_PROPERTY_TEMPLATE.format(
                        name=prop.name,
                        type_name=type_name_by_id[prop.typesxml_id]
                    ))
                for method in entity_spec.client_methods:
                    fh.write(_ENTITY_METHOD_TEMPLATE.format(
                        name=method.name,
                        args=f',\n{" " * (9 + len(method.name))}'.join(
                            ['self'] + [_ENTITY_ARGS_TEMPLATE.format(
                                arg=type_name_by_id[i].lower(),
                                type_name=type_name_by_id[i]) for i in method.arg_types])
                    ))

            pairs = []
            for entity_spec in sorted(entities, key=lambda s: s.uid):
                pairs.append(f'    {entity_spec.uid}: {entity_spec.name}')
            spec_by_id_str = '\n\nENTITY_CLS_BY_ID = {\n%s\n}' % ',\n'.join(pairs)
            fh.write(spec_by_id_str)
            fh.write('\n')

            all_lines = []
            for chunk in _chunker(
                    [f"'{s.name}'" for s in entities] + ["'ENTITY_CLS_BY_ID'"], 3):
                all_lines.append('    ' + ', '.join(chunk))
            fh.write('\n__all__ = (\n%s\n)\n' % ',\n'.join(all_lines))

        logger.info(f'Entities have been written (dst file = '
                    f'"{self._entity_dst_path}")')


class ErrorCodeGen:

    def __init__(self, dst_path: pathlib.Path):
        self._dst_path = dst_path
        self._dst_path.parent.mkdir(parents=True, exist_ok=True)

    def generate(self, spec: List[message.servererror.ServerErrorSpec]):
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