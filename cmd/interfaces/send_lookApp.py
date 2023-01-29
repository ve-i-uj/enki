import asyncio
import logging
import sys
from enki.net.kbeclient.client import StreamClient

import environs

from enki import settings
from enki.enkitype import AppAddr
from enki.net import msgspec
from enki.net.command.interfaces import InterfacesLookAppCommand
from enki.misc import log

logger = logging.getLogger(__name__)

_env = environs.Env()

_HOST: str = _env.str('KBE_INTERFACES_HOST')
_PORT: int = _env.int('KBE_INTERFACES_PORT')
INTERFACES_ADDR = AppAddr(_HOST, _PORT)


async def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))

    client = StreamClient(
        INTERFACES_ADDR, msgspec.app.interfaces.SPEC_BY_ID
    )
    res = await client.start()
    if not res.success:
        logger.error(f'Cannot connect to the "{INTERFACES_ADDR}" server'
                     f' address (err="{res.text}")')
        sys.exit(1)

    cmd = InterfacesLookAppCommand(client)
    client.set_msg_receiver(cmd)

    res = await cmd.execute()
    if not res.success:
        logger.error(res.text)
        sys.exit(1)

    logger.info(res.result)
    sys.exit(0)


if __name__ == '__main__':
    asyncio.run(main())
