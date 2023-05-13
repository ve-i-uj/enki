"""Отправить сообщение Logger::queryLoad для проверки что компонент живой."""

import asyncio
import logging
import sys

import environs

from enki import settings
from enki.core.enkitype import AppAddr
from enki.core import msgspec
from enki.net.client import TCPClient
from enki.command.logger import QueryLoadCommand
from enki.misc import log

logger = logging.getLogger(__name__)

# The Machine address
_env = environs.Env()
_HOST: str = _env.str('KBE_LOGGER_HOST')
_PORT: int = _env.int('KBE_LOGGER_PORT')
LOGGER_ADDR = AppAddr(_HOST, _PORT)


async def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))
    client = TCPClient(LOGGER_ADDR, msgspec.app.logger.SPEC_BY_ID)
    res = await client.start()
    if not res.success:
        logger.error(f'Cannot connect to the "{LOGGER_ADDR}" server address '
                     f'(err="{res.text}")')
        sys.exit(1)

    cmd = QueryLoadCommand(client)
    client.set_msg_receiver(cmd)
    resp = await cmd.execute()
    if not resp.success:
        logger.error(resp.text)
        sys.exit(1)

    logger.info('Done')
    sys.exit(0)


if __name__ == '__main__':
    asyncio.run(main())
