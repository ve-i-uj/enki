"""Check if the component is alive.

For this command to work, you first need to find out the internal address of the component,
because connections from outside are discarded (lookApp only works for INTERNAL
connections).

But, this script is used to check the health of the Supervisor
component. Supervisor has the API of the component "Machine", but it doesn't
have restriction for INTERNAL address, so the script will get response.
"""

import asyncio
import logging
import sys

import environs

from enki import settings
from enki.core.enkitype import AppAddr
from enki.core import msgspec
from enki.command import RequestCommand
from enki.core.kbeenum import ComponentType
from enki.core.message import Message
from enki.handler.serverhandler.common import OnLookAppParsedData
from enki.misc import log

logger = logging.getLogger(__name__)

_env = environs.Env()

MACHINE_ADDR = AppAddr(
    _env.str('KBE_MACHINE_HOST'),
    _env.int('KBE_MACHINE_TCP_PORT', 20099)
)


async def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))

    cmd_lookApp = RequestCommand(
        MACHINE_ADDR,
        Message(msgspec.app.machine.lookApp, tuple()),
        resp_msg_spec=msgspec.custom.onLookApp.change_component_owner(ComponentType.MACHINE),
        stop_on_first_data_chunk=True
    )
    res = await cmd_lookApp.execute()
    if not res.success:
        logger.error(res.text)
        sys.exit(1)

    msgs = res.result
    msg = msgs[0]
    pd = OnLookAppParsedData(*msg.get_values())

    logger.info(pd.asdict())
    sys.exit(0)


if __name__ == '__main__':
    asyncio.run(main())
