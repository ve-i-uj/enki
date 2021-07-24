"""Code generators.

Generate code by parsed data.
"""

import collections
import dataclasses
import logging
import pathlib
from typing import List

from enki import descr, kbetype, interface, dcdescr
from enki.misc import devonly

from . import parser


logger = logging.getLogger(__name__)

_APP_HEADER_TEMPLATE = '''"""Messages of {name}."""

from enki import kbetype, dcdescr
'''

_APP_MSG_TEMPLATE = """
{short_name} = dcdescr.MessageDescr(
    id={id},
    name='{name}',
    args_type=dcdescr.{args_type},
    field_types={field_types},
    desc='{desc}'
)
"""

_SERVERERROR_HEADER_TEMPLATE = '''"""Server errors."""

from enki import dcdescr
'''

_SERVERERROR_TEMPLATE = """
{name} = dcdescr.ServerErrorDescr(
    id={id},
    name='{name}',
    desc='{desc}'
)
"""

_TYPE_HEADER_TEMPLATE = '''"""Generated types represent types of the file types.xml"""

import collections

from enki import kbetype
from enki import dcdescr

'''

_TYPE_SPEC_TEMPLATE = """
{var_name} = dcdescr.DataTypeDescr(
    id={id},
    base_type_name='{base_type_name}',
    name='{name}',    
    module_name={module_name},
    pairs={pairs},
    of={of},
    kbetype={kbetype},
)
"""

_ENTITY_HEADER = '''"""Generated module represents the entity "{name}" of the file entities.xml"""

import collections
import logging

from enki import kbetype, bentity, descr
from enki.misc import devonly

logger = logging.getLogger(__name__)

'''


_ENTITY_INIT_MODULE_TEMPLATE = '''"""Generated classes represent entities of the file entities.xml"""

from .description import DESC_BY_UID

__all__ = ['DESC_BY_UID']
'''

_ENTITY_RPC_CLS_TEMPLATE = '''
class _{entity_name}{component_name}Entity:
    """Remote call to the {component_name}App component of the entity."""
'''

_ENTITY_RPC_METHOD_TEMPLATE = '''
    def {method_name}({arguments}):
        logger.debug('[%s] %s', self, devonly.func_args_values())
'''

_ENTITY_TEMPLATE = """
class {name}Base(bentity.Entity):
    CLS_ID = {entity_id}
"""

_ENTITY_INIT_TEMPLATE = """
    def __init__(self, entity_id: int):
        super().__init__(entity_id) 
        self._cell = _{entity_name}CellEntity()
        self._base = _{entity_name}BaseEntity()

        {attributes}
"""

_ENTITY_ATTRS_TEMPLATE = """self.__{name}: {python_type} = {value}"""

_ENTITY_PROPERTY_TEMPLATE = """
    @property
    def {name}(self) -> {python_type}:
        return self.__{name}
"""

_ENTITY_METHOD_TEMPLATE = """
    def {name}({args}):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
"""

_ENTITY_ARGS_TEMPLATE = '{arg}: {python_type}'

_ENTITY_DESC_MODULE_TEMPLATE = '''"""This generated module contains entity descriptions."""

{entities_import}

from enki import dcdescr
from enki.descr import deftype

DESC_BY_UID = {desc_by_uid}

__all__ = ['DESC_BY_UID']
'''

_ENTITY_DESC_IMPORT_TEMPLATE = """from .{cls_name} import {cls_name}Base"""

_ENTITY_DESC_TEMPLATE = """
    {uid}: dcdescr.EntityDesc(
        name='{entity_name}',
        uid={uid},
        cls={entity_name}Base,
        property_desc_by_id={property_desc_by_id},
        client_methods=[
        ],
        base_methods=[
        ],
        cell_methods=[
        ],
    ),
"""

_ENTITY_PROPERTY_SPEC_TEMPLATE = """
            {uid}: dcdescr.PropertyDesc(
                uid={uid},
                name='{name}',
                kbetype=deftype.{spec_name}_SPEC.kbetype
            ),"""


def _to_string(msg_spec: parser.ParsedAppMessageDC):
    """Convert a message to it string representation."""
    args_type = dcdescr.MsgArgsType(msg_spec.args_type)
    if not msg_spec.field_types:
        if args_type == dcdescr.MsgArgsType.VARIABLE:
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
        name=msg_spec.name,
        args_type=str(dcdescr.MsgArgsType(msg_spec.args_type)),
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

    def generate(self, parsed_types: List[parser.ParsedTypeDC]) -> None:
        """Write code for types."""
        type_count = len(parsed_types)
        parsed_types[:] = self._reorder_types(parsed_types)
        type_by_id = {t.id: t for t in parsed_types}
        assert type_count == len(parsed_types)
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
                    for key, type_id in parsed_type.fd_type_id_by_key.items():
                        type_ = '%s_SPEC.kbetype' % type_by_id[type_id].type_name
                        new_pairs.append(f"        ('{key}', {type_})")
                    kwargs['pairs'] = 'collections.OrderedDict([\n%s\n    ])' % ',\n'.join(new_pairs)

                # Prepare string representation of Array
                kwargs['of'] = None
                if parsed_type.is_array:
                    kwargs['of'] = \
                        '%s_SPEC.kbetype' % type_by_id[parsed_type.arr_of_id].name

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
        self._entity_dst_path.mkdir(parents=True, exist_ok=True)

    def generate(self, entities: List[parser.ParsedEntityDC]) -> None:
        """Write code for entities."""

        def get_python_type(typesxml_id: int) -> str:
            """Calculate the python type of the property"""
            kbe_type = descr.deftype.TYPE_SPEC_BY_ID[typesxml_id].kbetype
            if isinstance(kbe_type.default, interface.PluginType):
                # It's an inner defined type
                python_type = f'kbetype.{kbe_type.default.__class__.__name__}'
            else:
                # It's a built-in type of python
                python_type = type(kbe_type.default).__name__
            return python_type

        def get_type_name(typesxml_id: int) -> str:
            type_spec = descr.deftype.TYPE_SPEC_BY_ID[typesxml_id]
            type_name = type_spec.name if type_spec.name else type_spec.type_name
            return type_name

        def get_default_value(typesxml_id: int) -> str:
            spec = descr.deftype.TYPE_SPEC_BY_ID[typesxml_id]
            return f'descr.deftype.{spec.name}_SPEC.kbetype.default'

        ent_descriptions = {}
        for entity_spec in entities:
            with (self._entity_dst_path / f'{entity_spec.name}.py').open('w') as fh:
                fh.write(_ENTITY_HEADER.format(name=entity_spec.name))

                # Write to the file cell/base remote call classes.
                for name, methods in (('base', entity_spec.base_methods),
                                      ('cell', entity_spec.cell_methods)):
                    fh.write(_ENTITY_RPC_CLS_TEMPLATE.format(
                        entity_name=entity_spec.name,
                        component_name=name.capitalize()
                    ))

                    for method_data in methods:
                        args = ['self']
                        for i, arg_type in enumerate(method_data.arg_types):
                            python_type = get_python_type(arg_type)
                            args.append(f'arg_{i}: {python_type}')

                        fh.write(_ENTITY_RPC_METHOD_TEMPLATE.format(
                            method_name=method_data.name,
                            arguments=', '.join(args)
                        ))

                    fh.write('\n')

                attributes = []
                properties = []
                property_descs = collections.OrderedDict()
                for prop in entity_spec.properties:
                    name = prop.name
                    python_type = get_python_type(prop.typesxml_id)
                    value = get_default_value(prop.typesxml_id)
                    attributes.append(_ENTITY_ATTRS_TEMPLATE.format(
                        name=name,
                        python_type=python_type,
                        value=value,
                    ))
                    properties.append(_ENTITY_PROPERTY_TEMPLATE.format(
                        name=prop.name,
                        python_type=get_python_type(prop.typesxml_id),
                    ))
                    property_descs[prop.uid] = _ENTITY_PROPERTY_SPEC_TEMPLATE.format(
                        uid=prop.uid,
                        name=prop.name,
                        spec_name=get_type_name(prop.typesxml_id),
                    )

                fh.write(_ENTITY_TEMPLATE.format(name=entity_spec.name,
                                                 entity_id=entity_spec.uid))
                fh.write(_ENTITY_INIT_TEMPLATE.format(
                    entity_name=entity_spec.name,
                    attributes='\n        '.join(attributes)
                ))
                # write all getters to that attributes
                fh.writelines(properties)

                for method in entity_spec.client_methods:
                    fh.write(_ENTITY_METHOD_TEMPLATE.format(
                        name=method.name,
                        args=f',\n{" " * (9 + len(method.name))}'.join(
                            ['self'] + [_ENTITY_ARGS_TEMPLATE.format(
                                arg=get_type_name(i).lower(),
                                type_name=get_type_name(i),
                                python_type=get_python_type(i),
                            ) for i in method.arg_types])
                    ))

            prop_descs = ''.join(v for k, v in sorted(property_descs.items()))
            ent_descriptions[entity_spec.name] = _ENTITY_DESC_TEMPLATE.format(
                entity_name=entity_spec.name,
                uid=entity_spec.uid,
                property_desc_by_id='{' + prop_descs + '\n        }'
            )

        with (self._entity_dst_path / 'description.py').open('w') as fh:
            entities_import = '\n'.join(
                _ENTITY_DESC_IMPORT_TEMPLATE.format(cls_name=name)
                for name in sorted(ent_descriptions.keys())
            )
            fh.write(_ENTITY_DESC_MODULE_TEMPLATE.format(
                entities_import=entities_import,
                desc_by_uid='{' + '\n'.join(ent_descriptions.values()) + '}',
            ))

        with (self._entity_dst_path / f'__init__.py').open('w') as fh:
            fh.write(_ENTITY_INIT_MODULE_TEMPLATE)

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
