import asyncio
import logging
import sys

import environs

from enki import settings
from enki.enkitype import AppAddr
from enki.net import msgspec
from enki.net.command.machine import OnQueryAllInterfaceInfosCommand, \
    OnQueryAllInterfaceInfosClient
from enki.misc import log

logger = logging.getLogger(__name__)

_env = environs.Env()

# The Machine address
_MACHINE_HOST: str = _env.str('KBE_MACHINE_HOST')
_MACHINE_PORT: int = _env.int('KBE_MACHINE_PORT')
MACHINE_ADDR = AppAddr(_MACHINE_HOST, _MACHINE_PORT)


async def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))

    client = OnQueryAllInterfaceInfosClient(
        MACHINE_ADDR, msgspec.app.machine.SPEC_BY_ID
    )
    res = await client.start()
    if not res.success:
        logger.error(f'Cannot connect to the "{MACHINE_ADDR}" server'
                     f' address (err="{res.text}")')
        sys.exit(1)

    cmd = OnQueryAllInterfaceInfosCommand(
        client=client,
        uid=0,
        username='123',
        finderRecvPort=0
    )
    client.set_msg_receiver(cmd)
    resp = await cmd.execute()
    if not resp.success:
        logger.error(f'No response (err="{resp.text}")')
        sys.exit(1)

    logger.info(f'Done (result = {resp.result})')
    sys.exit(0)


if __name__ == '__main__':
    asyncio.run(main())
