"""Запросить из консоли componentID у Машины.

KBE_MACHINE_HOST='0.0.0.0' KBE_MACHINE_UDP_PORT=20086
"""

import asyncio
import logging
import pprint
import sys

import environs

from enki import settings
from enki.command.machine import QueryComponentIDCommand
from enki.misc import log
from enki.net.addr import Addr, Port

logger = logging.getLogger(__name__)

_env = environs.Env()

# ЭТО UDP адрес машины
_MACHINE_HOST: str = _env.str("KBE_MACHINE_HOST")
_MACHINE_PORT: int = _env.int("KBE_MACHINE_UDP_PORT")

MACHINE_ADDR = Addr(_MACHINE_HOST, Port(_MACHINE_PORT))


async def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))

    # В Machine может не сработать, чтобы ответ пришёл на порт "ноль". Но у
    # Supervisor это работает.
    cmd = QueryComponentIDCommand(MACHINE_ADDR, Port.get_no_port_obj())
    res = await cmd.execute()
    if not res.success:
        logger.error(res.text)
        sys.exit(1)

    assert res.result is not None
    pprint.pprint(res.result.asdict())

    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
