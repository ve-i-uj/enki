"""Classes for forming a client-server vocabulary."""

import abc
import dataclasses
import logging
import pathlib
from typing import List, Any

from enki import message, servererror
from enki.misc import devonly

from . import client, parser

logger = logging.getLogger(__name__)

_HEADER_TEMPLATE = '''"""Messages of {name}."""

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

from enki import servererror
'''

_SERVERERROR_TEMPLATE = """
{name} = servererror.ServerErrorSpec(
    id={id},
    name='{name}',
    desc='{desc}'
)
"""


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
                fh.write(_HEADER_TEMPLATE.format(name=app_name.capitalize()))
                for msg_spec in sorted(msg_specs, key=lambda s: s.id):
                    fh.write(_to_string(msg_spec))

                if app_name == 'client':
                    pairs = []
                    for msg_spec in sorted(msg_specs, key=lambda s: s.id):
                        short_name = msg_spec.name.split('::')[1]
                        pairs.append(f'    {short_name}.id: {short_name}')
                    spec_by_id_str = '\nSPEC_BY_ID = {\n%s\n}' % ',\n'.join(pairs)
                    fh.write(spec_by_id_str)

            logger.info(f'{app_name.capitalize()} messages have been written '
                        f'(dst file = "{dst_path}")')


class EntityMolder(_Molder):
    """Molds base of entity message communication."""

    def __init__(self, client_: client.NinmahClient, account_name: str,
                 password: str, dst_path: pathlib.Path):
        self._client = client_
        self._account_name = account_name
        self._password = password
        self._dst_path = dst_path
        self._dst_path.parent.mkdir(parents=True, exist_ok=True)

    async def _get_spec_data(self) -> bytes:
        await self._client.fire('login', self._account_name, self._password)
        return await self._client.fire('get_entity_def_specs')

    def _parse(self, data: bytes) -> Any:
        parser_ = parser.EntityDefParser()
        return parser_.parse_entity_defs(data)

    def _write(self, spec: Any):
        pass


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

    def _write(self, spec: List[servererror.ServerErrorSpec]):
        with self._dst_path.open('w') as fh:
            fh.write(_SERVERERROR_HEADER_TEMPLATE)
            for error_spec in spec:
                fh.write(
                    _SERVERERROR_TEMPLATE.format(**dataclasses.asdict(error_spec)))

        logger.info(f'Server errors have been written (dst file = '
                    f'"{self._dst_path}")')
