"""Classes for forming a client-server vocabulary."""

import abc
import logging
import pathlib
from typing import List, Any

from enki import message
from enki.misc import devonly

from . import client, parser

logger = logging.getLogger(__name__)

_HEADER_TEMPLATE = '''"""Messages of {name}."""

from enki import message
from enki import kbetype
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

    def __init__(self, client_: client.UpdaterClient, account_name: str,
                 password: str, dst_path: pathlib.Path):
        self._client = client_
        self._account_name = account_name
        self._password = password
        # Root directory of modules contained app messages
        self._dst_path = dst_path
        self._dst_path.parent.mkdir(parents=True, exist_ok=True)

    async def _get_spec_data(self) -> List[bytes]:
        """Get encoded spec."""
        spec_data = []
        await self._client.start()
        spec_data.append(await self._client.fire('get_loginapp_msg_specs'))
        # Request baseapp messages
        await self._client.fire('login', self._account_name, self._password)
        spec_data.append(await self._client.fire('get_baseapp_msg_specs'))

        return spec_data

    def _parse(self, data: List[bytes]) -> List[message.MessageSpec]:
        """Parse encoded spec."""
        parser_ = parser.ClientMsgesParser()
        msg_specs = []
        for app_data in data:
            msg_specs.extend(parser_.parse_app_msges(app_data))

        return msg_specs

    def _write(self, spec: List[message.MessageSpec]):
        """Write to somewhere the spec."""
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
                for msg in sorted(msg_specs, key=lambda s: s.id):
                    fh.write(_to_string(msg))

            logger.info(f'{app_name.capitalize()} messages have been written '
                        f'(dst file = "{dst_path}")')
