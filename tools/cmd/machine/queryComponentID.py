"""Запросить из консоли componentID у Машины.

KBE_MACHINE_HOST='0.0.0.0' KBE_MACHINE_UDP_PORT=20086
"""

import asyncio
import logging
import pprint
import sys

from environs import Env, EnvError

from enki import settings
from enki.command.machine import QueryComponentIDCommand
from enki.misc import log
from enki.net.addr import Addr, Port

logger = logging.getLogger(__name__)


async def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))

    # Это самый наглядный способ получить при эксплуатации, какой переменной
    # не хватает
    env = Env()
    got_error = False
    try:
        kbe_machine_host = env.str("KBE_MACHINE_HOST")
    except EnvError as err:
        got_error = True
        logger.error(err)
    try:
        kbe_machine_udp_port = env.int("KBE_MACHINE_UDP_PORT")
    except EnvError as err:
        got_error = True
        logger.error(err)

    if got_error:
        logger.error("Failed to load environment variables")
        sys.exit(1)

    machine_addr = Addr(kbe_machine_host, Port(kbe_machine_udp_port))

    # В Machine может не сработать, чтобы ответ пришёл на порт "ноль". Но у
    # Supervisor это работает.
    cmd = QueryComponentIDCommand(machine_addr, Port.get_no_port_obj())
    res = await cmd.execute()
    if not res.success:
        logger.error(res.text)
        sys.exit(1)

    assert res.result is not None
    pprint.pprint(res.result.asdict())

    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
