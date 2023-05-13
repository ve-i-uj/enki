"""
Эта команда не работает, т.к. lookApp работает только у INTERNAL подключений,
а у Машины ресивер только на внутренние события (т.е. EXTERNAL ресивер).
"""

import asyncio
import logging
import sys
from enki.net.client import StreamClient

import environs

from enki import settings
from enki.core.enkitype import AppAddr
from enki.core import msgspec
from enki.command.machine import MachineLookAppCommand
from enki.misc import log

logger = logging.getLogger(__name__)

_env = environs.Env()

# The Machine address
MACHINE_ADDR = AppAddr(
    _env.str('KBE_MACHINE_HOST'),
    _env.int('KBE_MACHINE_PORT')
)


async def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))

    client = StreamClient(
        MACHINE_ADDR, msgspec.app.machine.SPEC_BY_ID
    )
    res = await client.start()
    if not res.success:
        logger.error(f'Cannot connect to the "{MACHINE_ADDR}" server'
                     f' address (err="{res.text}")')
        sys.exit(1)

    cmd = MachineLookAppCommand(client)
    client.set_msg_receiver(cmd)

    res = await cmd.execute()
    if not res.success:
        logger.error(res.text)
        sys.exit(1)

    logger.info(res.result)
    sys.exit(0)


if __name__ == '__main__':
    asyncio.run(main())
