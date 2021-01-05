"""Classes for forming a client-server vocabulary."""

import abc
import dataclasses
import logging
import pathlib
from typing import List, Any, Tuple

from enki import message, kbetype, spec
from enki.misc import devonly

from . import client, parser

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


class _Molder(abc.ABC):

    async def mold(self):
        data = await self._get_spec_data()
        spec = self._parse(data)
        self._write(spec)

    @abc.abstractmethod
    async def _get_spec_data(self) -> Any:
        """Get encoded spec."""
        pass

    @abc.abstractmethod
    def _parse(self, data: Any) -> Any:
        """Parse encoded spec."""
        pass

    @abc.abstractmethod
    def _write(self, spec: Any):
        """Write to somewhere the spec."""
        pass


class ClientMolder(_Molder):
    """Mold base of client-server message communication."""

    def __init__(self, client_: client.NinmahClient, account_name: str,
                 password: str, dst_path: pathlib.Path):
        self._client = client_
        self._account_name = account_name
        self._password = password
        # Root directory of modules contained app messages
        self._dst_path = dst_path
        self._dst_path.parent.mkdir(parents=True, exist_ok=True)

    async def _get_spec_data(self) -> List[bytes]:
        spec_data = []
        spec_data.append(await self._client.fire('get_loginapp_msg_specs'))
        # Request baseapp messages
        await self._client.fire('login', self._account_name, self._password)
        spec_data.append(await self._client.fire('get_baseapp_msg_specs'))

        return spec_data

    def _parse(self, data: List[bytes]) -> List[message.MessageSpec]:
        parser_ = parser.ClientMsgesParser()
        msg_specs = []
        for app_data in data:
            msg_specs.extend(parser_.parse_app_msges(app_data))

        return msg_specs

    def _write(self, spec: List[message.MessageSpec]):
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
            dst_path = self._dst_path / f'{app_name}.py'
            with dst_path.open('w') as fh:
                fh.write(_APP_HEADER_TEMPLATE.format(name=app_name.capitalize()))
                for msg_spec in sorted(msg_specs, key=lambda s: s.id):
                    fh.write(_to_string(msg_spec))

                if app_name == 'client':
                    pairs = []
                    for msg_spec in sorted(msg_specs, key=lambda s: s.id):
                        short_name = msg_spec.name.split('::')[1]
                        pairs.append(f'    {short_name}.id: {short_name}')
                    spec_by_id_str = '\nSPEC_BY_ID = {\n%s\n}' % ',\n'.join(pairs)
                    fh.write(spec_by_id_str)
                    fh.write('\n')

            logger.info(f'{app_name.capitalize()} messages have been written '
                        f'(dst file = "{dst_path}")')


class EntityMolder(_Molder):
    """Molds base of entity message communication."""

    def __init__(self, client_: client.NinmahClient, account_name: str,
                 password: str, type_dst_path: pathlib.Path,
                 entity_dst_path: pathlib.Path):
        self._client = client_
        self._account_name = account_name
        self._password = password
        self._type_dst_path = type_dst_path
        self._entity_dst_path = entity_dst_path

        self._type_dst_path.parent.mkdir(parents=True, exist_ok=True)
        self._entity_dst_path.parent.mkdir(parents=True, exist_ok=True)

    async def _get_spec_data(self) -> bytes:
        await self._client.fire('login', self._account_name, self._password)
        return await self._client.fire('get_entity_def_specs')

    def _parse(self, data: bytes) -> Any:
        parser_ = parser.EntityDefParser()
        types, entities = parser_.parse(data)

        type_name_by_id = {t.id: (t.name if t.name else t.type_name)
                           for t in types}

        def cast_method_data(method_data) -> spec.entity.MethodData:
            return spec.entity.MethodData(
                name=method_data.name,
                arg_types=[type_name_by_id[i] for i in method_data.arg_types]
            )

        def cast_property(property_data) -> spec.entity.PropertyData:
            return spec.entity.PropertyData(
                name=property_data.name,
                default=property_data.default,
                type_name=type_name_by_id[property_data.typesxml_id]
            )

        new_entities = []
        for data in entities:
            new_entities.append(spec.entity.EntityData(
                name=data.name,
                uid=data.uid,
                properties=[cast_property(p) for p in data.properties],
                client_methods=[cast_method_data(m) for m in data.client_methods],
                base_methods=[cast_method_data(m) for m in data.base_methods],
                cell_methods=[cast_method_data(m) for m in data.cell_methods],
            ))

        return types, new_entities

    def _reorder_types(self, type_specs: List[spec.deftype.DataTypeSpec]):
        """Reorder types that they can be referenced by each other."""
        new_type_specs = []
        # types need reorder
        broken_type_specs = []
        for type_spec in type_specs:
            if type_spec.base_type_name in kbetype.SIMPLE_TYPE_BY_NAME:
                new_type_specs.append(type_spec)
                continue
            # Alias on FIXED_DICT or ARRAY cannot happen. Alias can refer on
            # a base kbe type.
            if type_spec.is_array and type_spec.of > type_spec.id:
                raise devonly.LogicError('Unexpected behaviour')
            if type_spec.is_fixed_dict:
                # Check types of FD keys
                broken = False
                for type_id in type_spec.pairs.values():
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
            assert type_spec.is_fixed_dict
            max_type_id = max(type_spec.pairs.values())
            # Insert this type after all declaration of its key types
            index = None
            for i, new_type_spec in enumerate(new_type_specs):
                if new_type_spec.id > max_type_id:
                    index = i
                    break
            new_type_specs.insert(index, type_spec)

        return new_type_specs

    def _write_types(self, type_specs: List[spec.deftype.DataTypeSpec]):
        """Write code for types."""
        type_count = len(type_specs)
        type_specs = self._reorder_types(type_specs)
        type_by_id = {t.id: t for t in type_specs}
        assert type_count == len(type_specs)
        with self._type_dst_path.open('w') as fh:
            fh.write(_DEF_HEADER_TEMPLATE)
            for type_spec in type_specs:
                module_name = type_spec.module_name
                if module_name is not None:
                    type_spec.module_name = f"'{module_name}'"

                type_spec.name = type_spec.type_name

                kwargs = dataclasses.asdict(type_spec)

                # Prepare string representation of FD keys
                if type_spec.is_fixed_dict:
                    new_pairs = []
                    for key, type_id in type_spec.pairs.items():
                        type_ = type_by_id[type_id].name
                        new_pairs.append(f"        '{key}': {type_}")
                    kwargs['pairs'] = '{\n%s\n    }' % ',\n'.join(new_pairs)

                # Prepare string representation of Array
                if type_spec.is_array:
                    kwargs['of'] = type_by_id[type_spec.of].name

                kwargs['var_name'] = f'_{type_spec.name}_SPEC'

                result = _TYPE_SPEC_TEMPLATE.format(**kwargs)
                new_lines = []
                for line in result.split('\n'):
                    if line.strip() in ('module_name=None,', 'pairs=None,',
                                        'of=None,'):
                        continue
                    new_lines.append(line)
                result = '\n'.join(new_lines)
                fh.write(result)
                if type_spec.base_type_name in kbetype.SIMPLE_TYPE_BY_NAME:
                    if type_spec.is_alias:
                        fh.write(_TYPE_ALIAS_TEMPLATE.format(**kwargs))
                    else:
                        fh.write(_SIMPLE_TYPE_TEMPLATE.format(**kwargs))
                elif type_spec.is_fixed_dict:
                    fh.write(_FD_TYPE_TEMPLATE.format(**kwargs))
                elif type_spec.is_array:
                    fh.write(_ARRAY_TYPE_TEMPLATE.format(**kwargs))
                else:
                    raise devonly.LogicError('Unexpected case')

            pairs = []
            for type_spec in sorted(type_specs, key=lambda s: s.id):
                pairs.append(f'    {type_spec.id}: {type_spec.name}')
            spec_by_id_str = '\nTYPE_BY_ID = {\n%s\n}' % ',\n'.join(pairs)
            fh.write(spec_by_id_str)
            fh.write('\n')

            all_lines = []
            for chunk in _chunker(
                    [f"'{s.name}'" for s in type_specs] + ["'TYPE_BY_ID'"], 3):
                all_lines.append('    ' + ', '.join(chunk))
            fh.write('\n__all__ = (\n%s\n)\n' % ',\n'.join(all_lines))

        logger.info(f'Server types have been written (dst file = "{self._type_dst_path}")')

    def _write_entity(self, entity_specs: List[spec.entity.EntityData]):
        """Write code for entities."""
        with self._entity_dst_path.open('w') as fh:
            fh.write(_ENTITY_HEADER)
            for entity_spec in entity_specs:
                fh.write(_ENTITY_TEMPLATE.format(name=entity_spec.name,
                                                 entity_id=entity_spec.uid))
                for prop in entity_spec.properties:
                    fh.write(_ENTITY_PROPERTY_TEMPLATE.format(
                        name=prop.name,
                        type_name=prop.type_name
                    ))
                for method in entity_spec.client_methods:
                    fh.write(_ENTITY_METHOD_TEMPLATE.format(
                        name=method.name,
                        args=f',\n{" " * (9 + len(method.name))}'.join(
                            ['self'] + [_ENTITY_ARGS_TEMPLATE.format(
                                arg=t.lower(), type_name=t)
                                for t in method.arg_types])
                    ))

            pairs = []
            for entity_spec in sorted(entity_specs, key=lambda s: s.uid):
                pairs.append(f'    {entity_spec.uid}: {entity_spec.name}')
            spec_by_id_str = '\n\nENTITY_CLS_BY_ID = {\n%s\n}' % ',\n'.join(pairs)
            fh.write(spec_by_id_str)
            fh.write('\n')

            all_lines = []
            for chunk in _chunker(
                    [f"'{s.name}'" for s in entity_specs] + ["'ENTITY_CLS_BY_ID'"], 3):
                all_lines.append('    ' + ', '.join(chunk))
            fh.write('\n__all__ = (\n%s\n)\n' % ',\n'.join(all_lines))

        logger.info(f'Entities have been written (dst file = '
                    f'"{self._entity_dst_path}")')


    def _write(self, spec: Tuple[List[spec.deftype.DataTypeSpec],
                                 List[spec.entity.EntityData]]):
        self._write_types(spec[0])
        self._write_entity(spec[1])


class ServerErrorMolder(_Molder):
    """Molds server errors."""

    def __init__(self, client_: client.NinmahClient, dst_path: pathlib.Path):
        self._client = client_
        self._dst_path = dst_path
        self._dst_path.parent.mkdir(parents=True, exist_ok=True)

    async def _get_spec_data(self) -> bytes:
        return await self._client.fire('get_server_error_specs')

    def _parse(self, data: bytes) -> Any:
        parser_ = parser.ServerErrorParser()
        return parser_.parse(data)

    def _write(self, spec: List[spec.servererror.ServerErrorSpec]):
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
